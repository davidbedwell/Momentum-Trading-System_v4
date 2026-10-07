from __future__ import annotations

from datetime import date, timedelta
import math
from typing import Any, Mapping

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodSpec, ParameterContract

METHOD_ID = "analysis.measurements.participation_context"


def _finite(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def participation_context(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Expose neutral participation measurements and temporally proximate events.

    The Research Director chooses the averaging and event windows. This method
    performs arithmetic/alignment only: it does not choose float/RVOL thresholds,
    classify an event as a meaningful catalyst, form an interaction rule, rank
    observations, or decide whether any relationship is predictive.
    """
    adv_window = int(parameters["adv_window"])
    event_window_days = int(parameters["event_window_days"])
    ohlcv = None
    structure = []
    events = []
    for payload in evidence_payloads.values():
        rows = list(payload)
        keys = set().union(*(row.keys() for row in rows)) if rows else set()
        if {"date", "close", "volume"}.issubset(keys):
            ohlcv = rows
        elif "float_shares" in keys:
            structure = rows
        elif "event_type" in keys or "headline" in keys:
            events = rows
    if ohlcv is None:
        raise ValueError("OHLCV input is required")

    ordered = sorted((dict(row) for row in ohlcv), key=lambda row: str(row.get("date", "")))
    volumes = [_finite(row.get("volume")) for row in ordered]
    events_by_date: dict[str, list[Mapping[str, object]]] = {}
    for event in events:
        event_date = str(event.get("event_date") or str(event.get("event_time") or "")[:10])
        if event_date:
            events_by_date.setdefault(event_date, []).append(event)

    panel = []
    for index, row in enumerate(ordered):
        prior = [value for value in volumes[max(0, index - adv_window):index] if value is not None]
        average_volume = sum(prior) / len(prior) if prior else None
        volume = volumes[index]
        relative_volume = None if volume is None or average_volume in (None, 0.0) else volume / average_volume
        matches: list[Mapping[str, object]] = []
        try:
            session_date = date.fromisoformat(str(row.get("date"))[:10])
        except ValueError:
            session_date = None
        if session_date is not None:
            for offset in range(-event_window_days, event_window_days + 1):
                matches.extend(events_by_date.get((session_date + timedelta(days=offset)).isoformat(), []))
        panel.append(
            {
                "date": str(row.get("date"))[:10],
                "volume": volume,
                "average_volume": average_volume,
                "relative_volume": relative_volume,
                "proximate_event_count": len(matches),
                "proximate_event_types": sorted(
                    {str(item.get("event_type")) for item in matches if item.get("event_type")}
                ),
                "proximate_event_records": [
                    {
                        "event_time": item.get("event_time"),
                        "event_type": item.get("event_type"),
                        "headline": item.get("headline"),
                        "publisher": item.get("publisher"),
                        "source_url": item.get("source_url"),
                        "eps_estimate": item.get("eps_estimate"),
                        "reported_eps": item.get("reported_eps"),
                        "surprise_pct": item.get("surprise_pct"),
                    }
                    for item in matches[:20]
                ],
            }
        )

    float_shares = _finite(structure[-1].get("float_shares")) if structure else None
    latest = dict(panel[-1]) if panel else {}
    latest_volume = _finite(latest.get("volume")) if latest else None
    current_float_turnover = (
        None
        if latest_volume is None or float_shares in (None, 0.0)
        else latest_volume / float_shares
    )

    return {
        "adv_window": adv_window,
        "event_window_days": event_window_days,
        "current_float_shares": float_shares,
        "current_float_turnover": current_float_turnover,
        "latest_session": latest,
        "scientific_authority": {
            "threshold_selection": "AI_RESEARCH_DIRECTOR_ONLY",
            "catalyst_classification": "AI_RESEARCH_DIRECTOR_ONLY",
            "interaction_definition": "AI_RESEARCH_DIRECTOR_ONLY",
            "predictive_interpretation": "AI_RESEARCH_DIRECTOR_ONLY",
            "human_low_float_high_rvol_catalyst_idea": "NONBINDING_RESEARCH_LEAD_ONLY",
        },
        "historical_float_limitation": (
            "Current float is not applied to historical dates; dated historical float is required for "
            "historical float or float-turnover interaction testing."
        ),
        "event_boundary": (
            "Temporal proximity and source event text are exposed without assigning materiality, catalyst status, "
            "market significance, causation, direction, or predictive value."
        ),
        "derived_dataset_catalog": {
            "participation_event_panel": {
                "row_count": len(panel),
                "schema": list(panel[0]) if panel else [],
                "output_path": ["derived_datasets", "participation_event_panel"],
                "temporary": True,
            }
        },
        "derived_datasets": {"participation_event_panel": panel},
        "interpretation_boundary": "NEUTRAL_MEASUREMENTS_AND_EVENT_EVIDENCE_ONLY_AI_RD_OWNS_SCIENCE",
    }


def method_spec() -> MethodSpec:
    return MethodSpec(
        METHOD_ID,
        ("NORMALIZED_DATASET",),
        (
            "Expose continuous relative-volume, current-float/current-turnover, and temporally proximate event "
            "evidence. The AI Research Director chooses averaging/event windows and owns all thresholds, catalyst "
            "classification, interactions, hypotheses, comparisons, and predictive conclusions."
        ),
        (
            ParameterContract(
                "adv_window",
                True,
                (int,),
                minimum_value=2,
                maximum_value=252,
                meaning="RD-selected prior-session averaging window used only to calculate continuous relative volume",
            ),
            ParameterContract(
                "event_window_days",
                True,
                (int,),
                minimum_value=0,
                maximum_value=10,
                meaning="RD-selected symmetric calendar-day window used only to expose temporally proximate events",
            ),
        ),
        2,
        True,
        True,
        False,
        {
            "scientific_selection": "AI_RESEARCH_DIRECTOR_ONLY",
            "threshold_selection": "AI_RESEARCH_DIRECTOR_ONLY",
            "catalyst_classification": "AI_RESEARCH_DIRECTOR_ONLY",
            "interaction_definition": "AI_RESEARCH_DIRECTOR_ONLY",
            "deterministic_ranking": False,
            "hard_coded_float_threshold": False,
            "hard_coded_relative_volume_threshold": False,
            "reusable_derived_dataset": True,
            "derived_dataset_name": "participation_event_panel",
            "historical_float_requires_dated_source": True,
        },
    )


def analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, participation_context)
