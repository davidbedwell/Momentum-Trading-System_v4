from __future__ import annotations

from datetime import datetime
import math
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

from .derived_market_store import DerivedFeatureDefinition, DerivedFeatureSetDefinition


EARNINGS_FEATURE_SET_ID = "mts_earnings_event_context"
EARNINGS_FEATURE_SET_VERSION = "v1"
NY = ZoneInfo("America/New_York")


def earnings_event_feature_set() -> DerivedFeatureSetDefinition:
    features = (
        DerivedFeatureDefinition("earnings_surprise_pct", "v1", "Reported EPS surprise percentage from the event record", ("POINT_IN_TIME_EARNINGS",), 0, "KNOWN_AFTER_EVENT_TIMESTAMP", "PREDICTOR"),
        DerivedFeatureDefinition("earnings_reported_eps", "v1", "Reported EPS from the event record", ("POINT_IN_TIME_EARNINGS",), 0, "KNOWN_AFTER_EVENT_TIMESTAMP", "CONTEXT"),
        DerivedFeatureDefinition("earnings_estimate_eps", "v1", "EPS estimate associated with the event record", ("POINT_IN_TIME_EARNINGS",), 0, "KNOWN_AFTER_EVENT_TIMESTAMP", "CONTEXT"),
        DerivedFeatureDefinition("earnings_event_count", "v1", "Number of earnings event records mapped to this security/effective session", ("POINT_IN_TIME_EARNINGS",), 0, "KNOWN_AFTER_EVENT_TIMESTAMP", "CONTEXT"),
    )
    return DerivedFeatureSetDefinition(
        EARNINGS_FEATURE_SET_ID,
        EARNINGS_FEATURE_SET_VERSION,
        "Point-in-time earnings event measurements aligned to the first market close after the event became known.",
        features,
        attributes={"event_alignment": "FIRST_MARKET_CLOSE_AFTER_EVENT_TIME", "future_information": False},
    )


def _finite(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _parse_event_time(value: object) -> datetime:
    text = str(value).strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError("earnings event_time must include timezone; naive event timing is not point-in-time safe")
    return parsed.astimezone(NY)


def build_earnings_event_rows(
    events: Sequence[Mapping[str, Any]],
    *,
    market_close_times_by_security: Mapping[str, Sequence[datetime]],
) -> tuple[Mapping[str, Any], ...]:
    """Align each event to the first supplied market close strictly after event time.

    Callers provide actual session-close timestamps; this function does not infer
    holidays or fabricate a trading calendar. Multiple records mapping to the same
    security/session are rejected rather than silently combined.
    """
    close_index = {
        security_id: tuple(sorted(close.astimezone(NY) for close in closes))
        for security_id, closes in market_close_times_by_security.items()
    }
    output = []
    identities: set[tuple[str, str]] = set()
    for event in events:
        if str(event.get("event_type", "")).upper() != "EARNINGS":
            continue
        security_id = str(event.get("security_id", "")).strip()
        if not security_id or security_id not in close_index:
            continue
        event_time = _parse_event_time(event.get("event_time"))
        effective_close = next((close for close in close_index[security_id] if close > event_time), None)
        if effective_close is None:
            continue
        effective_date = effective_close.date().isoformat()
        identity = (security_id, effective_date)
        if identity in identities:
            raise ValueError(f"multiple earnings records map to one security/effective session: {identity}")
        identities.add(identity)
        output.append({
            "security_id": security_id,
            "effective_date": effective_date,
            "eligible": bool(event.get("eligible", True)),
            "earnings_surprise_pct__v1": _finite(event.get("surprise_pct")),
            "earnings_reported_eps__v1": _finite(event.get("reported_eps")),
            "earnings_estimate_eps__v1": _finite(event.get("eps_estimate")),
            "earnings_event_count__v1": 1.0,
        })
    return tuple(sorted(output, key=lambda row: (row["effective_date"], row["security_id"])))
