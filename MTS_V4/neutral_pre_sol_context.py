from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any, Mapping, Sequence

from .analysis import RegisteredAnalysisMethod
from .contracts import AnalysisRequest, AnalysisResult, EvidenceDescriptor, ResearchPhase, SubjectMetadata
from .method_catalog import MethodSpec

FINRA_METHOD_ID = "analysis.measurements.finra_neutral_substrate"
FINRA_ANALYSIS_ID = "analysis:finra-neutral-substrate:v1"
EVENT_METHOD_ID = "analysis.measurements.catalyst_timing_substrate"
EVENT_ANALYSIS_ID = "analysis:catalyst-timing-substrate:v1"


def _number(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def finra_neutral_substrate(payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = [dict(r) for payload in payloads.values() for r in payload if isinstance(r, Mapping)]
    by_week: dict[str, dict[str, object]] = {}
    summary_types: set[str] = set()
    for row in rows:
        week = str(row.get("weekStartDate") or row.get("summaryStartDate") or "")[:10]
        summary = str(row.get("summaryTypeCode") or "UNKNOWN")
        summary_types.add(summary)
        if not week:
            continue
        key = f"{week}|{summary}"
        item = by_week.setdefault(key, {"week_start": week, "summary_type": summary, "share_quantity": 0.0, "trade_count": 0.0, "source_row_count": 0})
        item["source_row_count"] = int(item["source_row_count"]) + 1
        shares = _number(row.get("totalWeeklyShareQuantity"))
        trades = _number(row.get("totalWeeklyTradeCount"))
        if shares is not None:
            item["share_quantity"] = float(item["share_quantity"]) + shares
        if trades is not None:
            item["trade_count"] = float(item["trade_count"]) + trades
    panel = sorted(by_week.values(), key=lambda r: (str(r["week_start"]), str(r["summary_type"])))
    return {
        "source_row_count": len(rows),
        "summary_types_present": sorted(summary_types),
        "derived_dataset_catalog": {"finra_weekly_neutral_panel": {"row_count": len(panel), "schema": list(panel[0]) if panel else [], "output_path": ["derived_datasets", "finra_weekly_neutral_panel"], "temporary": True}},
        "derived_datasets": {"finra_weekly_neutral_panel": panel},
        "interpretation_boundary": "FINRA_SOURCE_DEFINED_COUNTS_AND_QUANTITIES_ONLY_AI_RD_OWNS_SCIENCE",
    }


def _timing(value: object) -> str:
    text = str(value or "").strip().replace("Z", "+00:00")
    if not text:
        return "UNKNOWN"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return "UNKNOWN"
    # Classification uses the timestamp's represented local clock only; no timezone is invented.
    hour = dt.hour
    if hour < 9:
        return "BEFORE_MARKET_HOURS"
    if hour >= 16:
        return "AFTER_MARKET_HOURS"
    return "DURING_MARKET_HOURS"


def catalyst_timing_substrate(payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = [dict(r) for payload in payloads.values() for r in payload if isinstance(r, Mapping)]
    inventory = []
    for row in rows:
        event_time = row.get("event_time")
        inventory.append({
            "event_time": event_time,
            "event_date": row.get("event_date") or str(event_time or "")[:10] or None,
            "event_type": row.get("event_type"),
            "release_clock_class": _timing(event_time),
            "headline": row.get("headline"),
            "publisher": row.get("publisher"),
            "eps_estimate": row.get("eps_estimate"),
            "reported_eps": row.get("reported_eps"),
            "surprise_pct": row.get("surprise_pct"),
        })
    inventory.sort(key=lambda r: str(r.get("event_time") or ""))
    return {
        "source_row_count": len(rows),
        "event_types_present": sorted({str(r.get("event_type")) for r in rows if r.get("event_type")}),
        "timing_policy": "MECHANICAL_REPRESENTED_CLOCK_CLASSIFICATION_NO_MATERIALITY_OR_CAUSALITY",
        "derived_dataset_catalog": {"catalyst_timing_inventory": {"row_count": len(inventory), "schema": list(inventory[0]) if inventory else [], "output_path": ["derived_datasets", "catalyst_timing_inventory"], "temporary": True}},
        "derived_datasets": {"catalyst_timing_inventory": inventory},
        "interpretation_boundary": "EVENT_INVENTORY_AND_CLOCK_TIMING_ONLY_AI_RD_OWNS_SCIENCE",
    }


def method_specs() -> tuple[MethodSpec, ...]:
    common = {"scientific_selection": "none", "deterministic_ranking": False, "reusable_derived_dataset": True}
    return (
        MethodSpec(FINRA_METHOD_ID, ("NORMALIZED_DATASET",), "Aggregate source-defined FINRA weekly categories/counts/quantities without interpretation.", (), 1, True, True, False, {**common, "derived_dataset_name": "finra_weekly_neutral_panel"}),
        MethodSpec(EVENT_METHOD_ID, ("NORMALIZED_DATASET",), "Inventory provider event records and mechanically classify represented release clock time without assigning catalyst significance.", (), 1, True, True, False, {**common, "derived_dataset_name": "catalyst_timing_inventory"}),
    )


def analysis_methods() -> tuple[RegisteredAnalysisMethod, ...]:
    return (RegisteredAnalysisMethod(FINRA_METHOD_ID, finra_neutral_substrate), RegisteredAnalysisMethod(EVENT_METHOD_ID, catalyst_timing_substrate))


def _run(*, subject: SubjectMetadata, descriptor: EvidenceDescriptor, method_id: str, logical_id: str, cache, analysis) -> tuple[str, AnalysisResult]:
    request = AnalysisRequest(request_id=f"pre-sol:{subject.subject_id}:{method_id}", subject_id=subject.subject_id, question="Human-authorized neutral pre-Sol mechanical substrate.", method_id=method_id, evidence_ids=(descriptor.evidence_id,), parameters={}, research_phase=ResearchPhase.EXPLORATION, rationale="Precompute recurring mechanical source organization before AI scientific interpretation.")
    result = analysis.execute(request, {descriptor.evidence_id: cache.get(descriptor.cache_key)})
    if result.execution_metadata.get("execution_status") != "SUCCESS":
        raise RuntimeError(f"pre-Sol neutral substrate failed: {method_id}: {result.outputs.get('execution_error')}")
    return logical_id, replace(result, execution_metadata={**result.execution_metadata, "future_information": {"contains_future_information": False, "direct_method_allows_future_information": False, "inherited_from_result_ids": [], "policy": "SOURCE_TIME_ONLY"}})


def build_for_subject(*, subject: SubjectMetadata, evidence: Sequence[EvidenceDescriptor], cache, analysis) -> Mapping[str, AnalysisResult]:
    out: dict[str, AnalysisResult] = {}
    for descriptor in evidence:
        if descriptor.evidence_type == "FINRA_OTC_TRANSPARENCY_WEEKLY":
            key, result = _run(subject=subject, descriptor=descriptor, method_id=FINRA_METHOD_ID, logical_id=FINRA_ANALYSIS_ID, cache=cache, analysis=analysis)
            out[key] = result
        elif descriptor.evidence_type == "CORPORATE_EVENT_AND_NEWS":
            key, result = _run(subject=subject, descriptor=descriptor, method_id=EVENT_METHOD_ID, logical_id=EVENT_ANALYSIS_ID, cache=cache, analysis=analysis)
            out[key] = result
    return out
