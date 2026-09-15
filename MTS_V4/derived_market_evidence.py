from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Mapping

from .cache import TemporaryResearchCache
from .contracts import EvidenceDescriptor, SubjectMetadata
from .derived_market_store import DerivedMarketQuery, DerivedMarketStore


def universe_subject(*, universe_id: str, display_ticker: str | None = None, attributes: Mapping[str, object] | None = None) -> SubjectMetadata:
    scope_id = f"universe:{universe_id}"
    payload = {"research_scope_type": "UNIVERSE", "universe_id": universe_id, "contains_multiple_securities": True}
    payload.update(dict(attributes or {}))
    return SubjectMetadata(subject_id=scope_id, ticker=display_ticker or universe_id, asset_class="EQUITY_UNIVERSE", attributes=payload)


def derived_market_evidence_descriptor(
    *,
    store: DerivedMarketStore,
    cache: TemporaryResearchCache,
    subject: SubjectMetadata,
    query: DerivedMarketQuery,
    allow_future_outcomes: bool = False,
) -> EvidenceDescriptor:
    """Materialize one deterministic Nexus slice with a hard outcome-access gate.

    Outcome/future-information columns are denied by default. Historical
    EXPLORATION callers must opt in explicitly. Validation/live callers should
    never set that capability, preventing a prompt or Analysis request from
    smuggling future outcomes into predictor evidence.
    """
    expected_subject_id = f"universe:{query.universe_id}"
    if subject.subject_id != expected_subject_id:
        raise ValueError(
            "derived market universe query must be owned by matching universe research subject: "
            f"{subject.subject_id!r} != {expected_subject_id!r}"
        )
    feature_set = store.get_feature_set(query.feature_set_id, query.feature_set_version)
    if feature_set is None:
        raise ValueError(f"unknown feature set: {query.feature_set_key}")
    requested = set(query.feature_columns or feature_set.feature_columns)
    feature_by_column = {feature.column_name: feature for feature in feature_set.features}
    outcome_columns = sorted(
        column for column in requested
        if column in feature_by_column and feature_by_column[column].classification == "OUTCOME"
    )
    if outcome_columns and not allow_future_outcomes:
        raise ValueError(
            "future/outcome derived columns require explicit historical-exploration authorization: "
            + ", ".join(outcome_columns)
        )

    rows = store.query(query)
    query_json = json.dumps(asdict(query), sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(query_json.encode("utf-8")).hexdigest()[:24]
    evidence_id = f"derived-market:{query.universe_id}:{query.feature_set_key}:{digest}"
    cache_key = f"cache:{evidence_id}"
    cache.put(cache_key, rows)
    state = store.state(query.universe_id, query.feature_set_id, query.feature_set_version)
    schema = ("security_id", "effective_date", "eligible", *(query.feature_columns or feature_set.feature_columns))
    coverage_start = min((str(row["effective_date"]) for row in rows), default=None)
    coverage_end = max((str(row["effective_date"]) for row in rows), default=None)
    return EvidenceDescriptor(
        evidence_id=evidence_id,
        subject_id=subject.subject_id,
        evidence_type="DERIVED_MARKET_PANEL",
        artifact_type="TABULAR",
        source_identity="NEXUS_DERIVED_MARKET_STORE",
        coverage_start=coverage_start,
        coverage_end=coverage_end,
        row_count=len(rows),
        schema=tuple(schema),
        cache_key=cache_key,
        provenance={
            "universe_id": query.universe_id,
            "feature_set_id": query.feature_set_id,
            "feature_set_version": query.feature_set_version,
            "derived_store_high_water_mark": state.high_water_mark,
            "query": asdict(query),
            "contains_future_outcomes": bool(outcome_columns),
            "future_outcome_access_explicitly_authorized": bool(outcome_columns and allow_future_outcomes),
            "raw_reacquirable_market_data_in_nexus": False,
        },
        neutral_semantics=(
            "Point-in-time derived market observations selected from the Nexus-owned derived market store. "
            "Rows may span multiple securities; security_id identifies each row-level member."
        ),
        content_identity=digest,
    )
