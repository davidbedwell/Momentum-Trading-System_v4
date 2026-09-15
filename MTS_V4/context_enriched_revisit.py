from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from statistics import median, pstdev
from typing import Any, Mapping, Sequence

from .cache import TemporaryResearchCache
from .contracts import EvidenceDescriptor, SubjectMetadata
from .derived_market_store import DerivedMarketQuery, DerivedMarketStore


def _finite(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _descriptor(
    *,
    cache: TemporaryResearchCache,
    subject: SubjectMetadata,
    evidence_type: str,
    rows: Sequence[Mapping[str, object]],
    provenance: Mapping[str, object],
    neutral_semantics: str,
) -> EvidenceDescriptor:
    identity = hashlib.sha256(
        json.dumps(
            {"subject_id": subject.subject_id, "evidence_type": evidence_type, "provenance": provenance},
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    evidence_id = f"evidence:{subject.subject_id}:{evidence_type.lower()}:{identity[:24]}"
    cache_key = f"cache:{evidence_id}"
    materialized = tuple(dict(row) for row in rows)
    cache.put(cache_key, materialized)
    dates = [str(row["effective_date"]) for row in materialized if row.get("effective_date")]
    schema = tuple(materialized[0]) if materialized else ()
    return EvidenceDescriptor(
        evidence_id=evidence_id,
        subject_id=subject.subject_id,
        evidence_type=evidence_type,
        artifact_type="TABULAR",
        source_identity="NEXUS_DERIVED_MARKET_STORE",
        coverage_start=min(dates, default=None),
        coverage_end=max(dates, default=None),
        row_count=len(materialized),
        schema=schema,
        cache_key=cache_key,
        provenance=dict(provenance),
        neutral_semantics=neutral_semantics,
        content_identity=identity,
    )


def build_context_enriched_revisit_evidence(
    *,
    store: DerivedMarketStore,
    cache: TemporaryResearchCache,
    subject: SubjectMetadata,
    universe_id: str,
    security_id: str,
    sector_id: str,
    security_sector_ids: Mapping[str, str],
    predictor_feature_set_id: str,
    predictor_feature_set_version: str,
    outcome_feature_set_id: str,
    outcome_feature_set_version: str,
) -> tuple[EvidenceDescriptor, ...]:
    """Expose ticker rows and uniformly calculated time-aligned market context.

    The calculation creates no scientific condition, threshold, rank, finding, or
    hypothesis. Every available numeric predictor receives the same market and
    current-sector summary treatment at each date.
    """
    feature_set = store.get_feature_set(predictor_feature_set_id, predictor_feature_set_version)
    outcome_set = store.get_feature_set(outcome_feature_set_id, outcome_feature_set_version)
    if feature_set is None or outcome_set is None:
        raise RuntimeError("context-enriched revisit feature sets are unavailable")
    predictor_columns = tuple(feature_set.feature_columns)
    outcome_columns = tuple(outcome_set.feature_columns)
    predictor_state = store.state(
        universe_id, predictor_feature_set_id, predictor_feature_set_version
    )
    outcome_state = store.state(
        universe_id, outcome_feature_set_id, outcome_feature_set_version
    )
    full_rows = store.query(DerivedMarketQuery(
        universe_id=universe_id,
        feature_set_id=predictor_feature_set_id,
        feature_set_version=predictor_feature_set_version,
        feature_columns=predictor_columns,
    ))
    by_date: dict[str, list[Mapping[str, object]]] = {}
    subject_by_date: dict[str, Mapping[str, object]] = {}
    for row in full_rows:
        if not row.get("eligible", True):
            continue
        date = str(row["effective_date"])
        by_date.setdefault(date, []).append(row)
        if str(row.get("security_id")) == security_id:
            subject_by_date[date] = row

    contextual_rows: list[Mapping[str, object]] = []
    for date in sorted(subject_by_date):
        population = by_date[date]
        sector_population = [
            row for row in population
            if security_sector_ids.get(str(row.get("security_id"))) == sector_id
        ]
        output: dict[str, object] = {
            "security_id": security_id,
            "effective_date": date,
            "eligible": True,
            "market_security_count": len(population),
            "current_sector_id": sector_id,
            "current_sector_security_count": len(sector_population),
        }
        subject_row = subject_by_date[date]
        for column in predictor_columns:
            output[f"subject__{column}"] = subject_row.get(column)
            market_values = [value for row in population if (value := _finite(row.get(column))) is not None]
            sector_values = [value for row in sector_population if (value := _finite(row.get(column))) is not None]
            output[f"market_median__{column}"] = median(market_values) if market_values else None
            output[f"market_dispersion__{column}"] = pstdev(market_values) if len(market_values) > 1 else None
            output[f"current_sector_median__{column}"] = median(sector_values) if sector_values else None
            output[f"current_sector_dispersion__{column}"] = pstdev(sector_values) if len(sector_values) > 1 else None
        contextual_rows.append(output)

    outcome_rows = store.query(DerivedMarketQuery(
        universe_id=universe_id,
        feature_set_id=outcome_feature_set_id,
        feature_set_version=outcome_feature_set_version,
        security_ids=(security_id,),
        feature_columns=outcome_columns,
    ))
    common = {
        "universe_id": universe_id,
        "security_id": security_id,
        "ticker": subject.ticker,
        "historical_membership_classification": "CURRENT_MEMBER_CONDITIONED",
        "former_constituents_present": False,
        "current_sector_labels_are_historical_pit": False,
    }
    return (
        _descriptor(
            cache=cache,
            subject=subject,
            evidence_type="TIME_ALIGNED_SUBJECT_MARKET_CONTEXT",
            rows=contextual_rows,
            provenance={
                **common,
                "feature_set_id": predictor_feature_set_id,
                "feature_set_version": predictor_feature_set_version,
                "uniform_context_calculation": True,
                "historical_outcomes_present": False,
                "source_high_water_mark": predictor_state.high_water_mark,
            },
            neutral_semantics=(
                "At each completed daily observation T, the ticker's predictor-time measurements are paired "
                "with uniformly calculated full-current-member-universe and current-sector medians and "
                "dispersion using only predictor rows dated T. Former constituents are absent and current "
                "sector labels are not represented as historical classifications."
            ),
        ),
        _descriptor(
            cache=cache,
            subject=subject,
            evidence_type="HISTORICAL_SUBJECT_OUTCOMES_EXPLORATION",
            rows=outcome_rows,
            provenance={
                **common,
                "feature_set_id": outcome_feature_set_id,
                "feature_set_version": outcome_feature_set_version,
                "contains_future_outcomes": True,
                "future_outcome_access_explicitly_authorized": True,
                "research_phase": "EXPLORATION",
                "source_high_water_mark": outcome_state.high_water_mark,
            },
            neutral_semantics=(
                "Historical ticker outcome measurements for exploratory predictive discovery. These columns "
                "contain future information and may not be used as prediction-time evidence in validation."
            ),
        ),
    )
