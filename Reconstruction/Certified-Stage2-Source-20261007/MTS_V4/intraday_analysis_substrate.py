from __future__ import annotations

from dataclasses import replace
from datetime import datetime
import math
from typing import Any, Mapping, Sequence

from .analysis import RegisteredAnalysisMethod
from .contracts import AnalysisRequest, AnalysisResult, EvidenceDescriptor, ResearchPhase, SubjectMetadata
from .method_catalog import MethodSpec

METHOD_ID = "analysis.substrate.intraday_participation"
LOGICAL_ANALYSIS_ID = "analysis:intraday-participation-substrate:v1"
OPENING_RANGE_MINUTES = (5, 15, 30)
FORWARD_MINUTES = (5, 15, 30, 60)


def _finite(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _minute(value: object) -> int | None:
    text = str(value or "")
    try:
        hour, minute = text[:5].split(":")
        return int(hour) * 60 + int(minute)
    except (TypeError, ValueError):
        return None


def _forward_close(rows: list[dict[str, object]], index: int, bars: int) -> float | None:
    target = index + bars
    return _finite(rows[target].get("close")) if target < len(rows) else None


def intraday_participation_substrate(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Precompute objective intraday measurements without scientific selection or interpretation."""
    intraday: list[dict[str, object]] | None = None
    events: list[dict[str, object]] = []
    structure: list[dict[str, object]] = []
    for payload in evidence_payloads.values():
        rows = [dict(row) for row in payload] if isinstance(payload, (list, tuple)) else []
        keys = set().union(*(row.keys() for row in rows)) if rows else set()
        if {"timestamp", "market_time", "session", "open", "high", "low", "close", "volume"}.issubset(keys):
            intraday = rows
        elif "event_type" in keys or "headline" in keys:
            events = rows
        elif "float_shares" in keys:
            structure = rows
    if intraday is None:
        raise ValueError("INTRADAY_OHLCV evidence is required")

    ordered = sorted(intraday, key=lambda row: str(row.get("timestamp", "")))
    by_date: dict[str, list[dict[str, object]]] = {}
    for row in ordered:
        by_date.setdefault(str(row.get("date", ""))[:10], []).append(row)

    events_by_date: dict[str, list[dict[str, object]]] = {}
    for event in events:
        event_date = str(event.get("event_date") or str(event.get("event_time") or "")[:10])[:10]
        if event_date:
            events_by_date.setdefault(event_date, []).append(event)

    # Time-matched cumulative-volume history. Each regular-session clock slot is compared
    # only with the same slot on prior sessions; no threshold or scientific ranking is applied.
    prior_cumulative_by_slot: dict[str, list[float]] = {}
    session_rows: list[dict[str, object]] = []
    session_summaries: list[dict[str, object]] = []

    for session_date in sorted(by_date):
        day = by_date[session_date]
        pre = [r for r in day if r.get("session") == "PREMARKET"]
        regular = [r for r in day if r.get("session") == "REGULAR"]
        pre_highs = [v for r in pre if (v := _finite(r.get("high"))) is not None]
        pre_lows = [v for r in pre if (v := _finite(r.get("low"))) is not None]
        pre_volumes = [v for r in pre if (v := _finite(r.get("volume"))) is not None]
        pre_high = max(pre_highs) if pre_highs else None
        pre_low = min(pre_lows) if pre_lows else None
        pre_volume = sum(pre_volumes) if pre_volumes else None

        ranges: dict[int, tuple[float | None, float | None]] = {}
        for minutes in OPENING_RANGE_MINUTES:
            cutoff = 570 + minutes
            subset = [r for r in regular if (_minute(r.get("market_time")) or 10**9) < cutoff]
            highs = [v for r in subset if (v := _finite(r.get("high"))) is not None]
            lows = [v for r in subset if (v := _finite(r.get("low"))) is not None]
            ranges[minutes] = (max(highs) if highs else None, min(lows) if lows else None)

        cumulative_volume = 0.0
        cumulative_pv = 0.0
        first_premarket_high_break: str | None = None
        first_or_break: dict[int, dict[str, str | None]] = {
            m: {"above": None, "below": None} for m in OPENING_RANGE_MINUTES
        }
        today_slot_cumulative: dict[str, float] = {}

        for index, row in enumerate(regular):
            volume = _finite(row.get("volume")) or 0.0
            high = _finite(row.get("high"))
            low = _finite(row.get("low"))
            close = _finite(row.get("close"))
            typical = None
            h, l = _finite(row.get("high")), _finite(row.get("low"))
            if h is not None and l is not None and close is not None:
                typical = (h + l + close) / 3.0
            cumulative_volume += volume
            if typical is not None:
                cumulative_pv += typical * volume
            vwap = cumulative_pv / cumulative_volume if cumulative_volume else None
            slot = str(row.get("market_time", ""))[:5]
            history = prior_cumulative_by_slot.get(slot, [])
            mean_prior = sum(history) / len(history) if history else None
            time_adjusted_rvol = (
                None if mean_prior in (None, 0.0) else cumulative_volume / mean_prior
            )
            today_slot_cumulative[slot] = cumulative_volume

            if first_premarket_high_break is None and pre_high is not None and high is not None and high > pre_high:
                first_premarket_high_break = str(row.get("timestamp"))
            for minutes, (or_high, or_low) in ranges.items():
                minute = _minute(row.get("market_time"))
                if minute is None or minute < 570 + minutes:
                    continue
                if first_or_break[minutes]["above"] is None and or_high is not None and high is not None and high > or_high:
                    first_or_break[minutes]["above"] = str(row.get("timestamp"))
                if first_or_break[minutes]["below"] is None and or_low is not None and low is not None and low < or_low:
                    first_or_break[minutes]["below"] = str(row.get("timestamp"))

            record: dict[str, object] = {
                "timestamp": row.get("timestamp"),
                "date": session_date,
                "market_time": row.get("market_time"),
                "close": close,
                "volume": volume,
                "cumulative_regular_volume": cumulative_volume,
                "time_adjusted_relative_volume": time_adjusted_rvol,
                "time_adjusted_rvol_prior_session_count": len(history),
                "vwap": vwap,
                "close_minus_vwap": None if close is None or vwap is None else close - vwap,
                "premarket_high": pre_high,
                "premarket_low": pre_low,
                "premarket_volume": pre_volume,
            }
            for minutes in OPENING_RANGE_MINUTES:
                record[f"opening_range_{minutes}m_high"] = ranges[minutes][0]
                record[f"opening_range_{minutes}m_low"] = ranges[minutes][1]
            # Source interval is five minutes. These are exhaustive future path measurements,
            # explicitly exploration-only and not eligible as prediction-time features.
            for minutes in FORWARD_MINUTES:
                future = _forward_close(regular, index, minutes // 5)
                record[f"forward_return_{minutes}m"] = (
                    None if close in (None, 0.0) or future is None else future / close - 1.0
                )
            session_rows.append(record)

        for slot, cumulative in today_slot_cumulative.items():
            prior_cumulative_by_slot.setdefault(slot, []).append(cumulative)

        current_float = None
        if session_date == max(by_date) and structure:
            current_float = _finite(structure[-1].get("float_shares"))
        session_summaries.append({
            "date": session_date,
            "premarket_high": pre_high,
            "premarket_low": pre_low,
            "premarket_volume": pre_volume,
            "regular_session_volume": cumulative_volume,
            "current_float_shares_if_current_session": current_float,
            "current_session_volume_over_current_float": (
                None if current_float in (None, 0.0) else cumulative_volume / current_float
            ),
            "first_premarket_high_break_timestamp": first_premarket_high_break,
            "opening_range_breaks": {str(k): v for k, v in first_or_break.items()},
            "event_records": events_by_date.get(session_date, []),
        })

    return {
        "policy": {
            "scientific_selection": "AI_RESEARCH_DIRECTOR_ONLY",
            "scientific_interpretation": "AI_RESEARCH_DIRECTOR_ONLY",
            "deterministic_thresholds": False,
            "deterministic_signal": False,
            "opening_range_minutes": list(OPENING_RANGE_MINUTES),
            "opening_range_windows_are_nonexclusive_measurement_infrastructure": True,
            "forward_minutes": list(FORWARD_MINUTES),
            "forward_outcomes_are_exploration_only_not_prediction_features": True,
            "current_float_back_projection": False,
            "historical_float_turnover_available": False,
        },
        "availability": {
            "historical_intraday_scope": "PROVIDER_AVAILABLE_RECENT_INTRADAY_ONLY",
            "historical_tradable_float_shares": "UNAVAILABLE_FROM_CURRENT_FREE_SOURCES",
            "current_float_may_be_used_only_for_current_session": True,
        },
        "derived_dataset_catalog": {
            "intraday_measurement_panel": {
                "row_count": len(session_rows),
                "schema": list(session_rows[0]) if session_rows else [],
                "output_path": ["derived_datasets", "intraday_measurement_panel"],
                "temporary": True,
            },
            "intraday_session_summary": {
                "row_count": len(session_summaries),
                "schema": list(session_summaries[0]) if session_summaries else [],
                "output_path": ["derived_datasets", "intraday_session_summary"],
                "temporary": True,
            },
        },
        "derived_datasets": {
            "intraday_measurement_panel": session_rows,
            "intraday_session_summary": session_summaries,
        },
        "interpretation_boundary": "OBJECTIVE_INTRADAY_MEASUREMENTS_ONLY_AI_RD_OWNS_SCIENCE",
    }


def method_spec() -> MethodSpec:
    return MethodSpec(
        METHOD_ID,
        ("NORMALIZED_DATASET",),
        "Precompute neutral intraday participation, premarket, opening-range, VWAP, event-alignment, time-matched volume, and forward-path measurements before AI scientific interpretation.",
        (),
        1,
        True,
        False,
        True,
        {
            "scientific_selection": "none",
            "deterministic_ranking": False,
            "deterministic_signal": False,
            "current_float_back_projection": False,
            "reusable_derived_dataset": True,
        },
    )


def analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, intraday_participation_substrate)


def build_for_subject(
    *,
    subject: SubjectMetadata,
    evidence: Sequence[EvidenceDescriptor],
    cache,
    analysis,
) -> Mapping[str, AnalysisResult]:
    intraday = [item for item in evidence if item.evidence_type == "INTRADAY_OHLCV"]
    optional = [
        item for item in evidence
        if item.evidence_type in {"CORPORATE_EVENT_AND_NEWS", "MARKET_STRUCTURE_SNAPSHOT"}
    ]
    if len(intraday) != 1:
        return {}
    descriptors = tuple(intraday + optional)
    request = AnalysisRequest(
        request_id=f"intraday-participation:{subject.subject_id}:v1",
        subject_id=subject.subject_id,
        question="Human-authorized neutral intraday participation and event measurement substrate.",
        method_id=METHOD_ID,
        evidence_ids=tuple(item.evidence_id for item in descriptors),
        parameters={},
        research_phase=ResearchPhase.EXPLORATION,
        rationale="Precompute objective intraday measurements before AI scientific interpretation.",
    )
    result = analysis.execute(request, {item.evidence_id: cache.get(item.cache_key) for item in descriptors})
    if result.execution_metadata.get("execution_status") != "SUCCESS":
        raise RuntimeError(f"intraday participation substrate failed: {result.outputs.get('execution_error')}")
    result = replace(
        result,
        execution_metadata={
            **result.execution_metadata,
            "future_information": {
                "contains_future_information": True,
                "direct_method_allows_future_information": True,
                "inherited_from_result_ids": [],
                "policy": "EXPLORATION_FORWARD_OUTCOMES_PRESENT_AND_EXPLICITLY_NOT_PREDICTION_FEATURES",
            },
        },
    )
    return {LOGICAL_ANALYSIS_ID: result}
