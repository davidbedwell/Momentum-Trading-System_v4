from __future__ import annotations

from dataclasses import replace
from datetime import date
import math
from typing import Any, Mapping, Sequence

from .analysis import RegisteredAnalysisMethod
from .contracts import AnalysisRequest, AnalysisResult, EvidenceDescriptor, ResearchPhase, SubjectMetadata
from .method_catalog import MethodSpec

METHOD_ID = "analysis.measurements.sec_share_structure"
LOGICAL_ANALYSIS_ID = "analysis:sec-share-structure-substrate:v1"


def _finite(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _iso_date(value: object) -> str | None:
    text = str(value or "").strip()[:10]
    if not text:
        return None
    try:
        date.fromisoformat(text)
    except ValueError:
        return None
    return text


def sec_share_structure_context(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Mechanically align SEC share facts to market dates using only known-at data."""
    ohlcv = None
    sec_rows = None
    for payload in evidence_payloads.values():
        rows = list(payload) if isinstance(payload, (list, tuple)) else []
        keys = set().union(*(row.keys() for row in rows)) if rows else set()
        if {"date", "close", "volume"}.issubset(keys):
            ohlcv = rows
        elif {"fact_kind", "known_at", "period_end", "value", "unit"}.issubset(keys):
            sec_rows = rows
    if ohlcv is None:
        raise ValueError("daily OHLCV evidence is required")
    if sec_rows is None:
        raise ValueError("POINT_IN_TIME_SHARE_STRUCTURE evidence is required")

    facts = [dict(row) for row in sec_rows]
    market = sorted((dict(row) for row in ohlcv), key=lambda row: str(row.get("date", "")))
    panel: list[dict[str, object]] = []

    for row in market:
        session = str(row.get("date", ""))[:10]
        eligible = [
            fact for fact in facts
            if fact.get("fact_kind") == "SHARES_OUTSTANDING"
            and (_iso_date(fact.get("known_at")) or "9999-12-31") <= session
            and str(fact.get("unit", "")).lower() in {"shares", "share"}
        ]
        latest = max((_iso_date(f.get("known_at")) for f in eligible), default=None)
        candidates = [f for f in eligible if _iso_date(f.get("known_at")) == latest] if latest else []
        values = sorted({v for f in candidates if (v := _finite(f.get("value"))) is not None})
        shares = values[0] if len(values) == 1 else None
        volume = _finite(row.get("volume"))
        panel.append({
            "date": session,
            "volume": volume,
            "shares_outstanding_known_at_t": shares,
            "shares_outstanding_source_known_at": latest,
            "shares_outstanding_ambiguous": len(values) > 1,
            "volume_over_shares_outstanding": (
                None if volume is None or shares in (None, 0.0) else volume / shares
            ),
        })

    public_float_rows = [
        dict(row) for row in facts if row.get("fact_kind") == "PUBLIC_FLOAT_REPORTED"
    ]
    return {
        "policy": {
            "point_in_time_known_at_alignment": True,
            "current_float_back_projection": False,
            "deterministic_thresholds": False,
            "deterministic_signal": False,
            "scientific_interpretation": "AI_RESEARCH_DIRECTOR_ONLY",
        },
        "sec_public_float_reported_facts": public_float_rows,
        "historical_float_boundary": (
            "SEC EntityPublicFloat is preserved in its reported unit. This method does not relabel monetary public float as float shares."
        ),
        "evidence_capabilities": {
            "historical_shares_outstanding": {
                "available": True,
                "source": "SEC_POINT_IN_TIME_DISCLOSURES",
                "temporal_semantics": "KNOWN_AT_ALIGNED",
            },
            "historical_tradable_float_shares": {
                "available": False,
                "reason": "CURRENT_FREE_SEC_SOURCE_DOES_NOT_PROVIDE_HISTORICAL_TRADABLE_FLOAT_SHARE_COUNTS",
            },
            "sec_entity_public_float": {
                "available": bool(public_float_rows),
                "meaning": "REPORTED_PUBLIC_FLOAT_VALUE_IN_ORIGINAL_SEC_UNIT_NOT_TRADABLE_FLOAT_SHARE_COUNT",
            },
        },
        "ai_research_director_data_boundary": {
            "may_identify_historical_tradable_float_as_missing_variable": True,
            "may_request_historical_tradable_float_as_next_data_requirement": True,
            "must_not_claim_historical_tradable_float_relationship_tested_without_float_share_evidence": True,
            "must_not_back_project_current_float": True,
            "scientific_priority_assigned": False,
            "scientific_interpretation": "AI_RESEARCH_DIRECTOR_ONLY",
        },
        "derived_dataset_catalog": {
            "sec_share_structure_panel": {
                "row_count": len(panel),
                "schema": list(panel[0]) if panel else [],
                "output_path": ["derived_datasets", "sec_share_structure_panel"],
                "temporary": True,
            }
        },
        "derived_datasets": {"sec_share_structure_panel": panel},
        "interpretation_boundary": "OBJECTIVE_POINT_IN_TIME_RECONCILIATION_ONLY_AI_RD_OWNS_SCIENCE",
    }


def method_spec() -> MethodSpec:
    return MethodSpec(
        METHOD_ID,
        ("NORMALIZED_DATASET",),
        "Align SEC share-structure facts to daily market dates without scientific interpretation.",
        (),
        2,
        True,
        False,
        True,
        {
            "scientific_selection": "none",
            "deterministic_ranking": False,
            "point_in_time_safe": True,
            "current_float_back_projection": False,
            "reusable_derived_dataset": True,
            "derived_dataset_name": "sec_share_structure_panel",
        },
    )


def analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, sec_share_structure_context)


def build_for_subject(
    *,
    subject: SubjectMetadata,
    evidence: Sequence[EvidenceDescriptor],
    cache,
    analysis,
) -> Mapping[str, AnalysisResult]:
    ohlcv = [
        item for item in evidence
        if item.evidence_type == "OHLCV"
        and {"date", "close", "volume"}.issubset(item.schema)
    ]
    sec = [
        item for item in evidence
        if item.evidence_type == "POINT_IN_TIME_SHARE_STRUCTURE"
        and {"fact_kind", "known_at", "period_end", "value", "unit"}.issubset(item.schema)
    ]
    if len(ohlcv) != 1 or len(sec) != 1:
        return {}

    descriptors = (ohlcv[0], sec[0])
    request = AnalysisRequest(
        request_id=f"sec-share-structure:{subject.subject_id}:v1",
        subject_id=subject.subject_id,
        question="Human-authorized neutral point-in-time SEC share-structure reconciliation.",
        method_id=METHOD_ID,
        evidence_ids=tuple(item.evidence_id for item in descriptors),
        parameters={},
        research_phase=ResearchPhase.EXPLORATION,
        rationale="Precompute objective known-at share-structure measurements before AI scientific interpretation.",
    )
    result = analysis.execute(
        request,
        {item.evidence_id: cache.get(item.cache_key) for item in descriptors},
    )
    if result.execution_metadata.get("execution_status") != "SUCCESS":
        raise RuntimeError(f"SEC share-structure substrate failed: {result.outputs.get('execution_error')}")
    result = replace(
        result,
        execution_metadata={
            **result.execution_metadata,
            "future_information": {
                "contains_future_information": False,
                "direct_method_allows_future_information": False,
                "inherited_from_result_ids": [],
                "policy": "POINT_IN_TIME_KNOWN_AT_ONLY",
            },
        },
    )
    return {LOGICAL_ANALYSIS_ID: result}
