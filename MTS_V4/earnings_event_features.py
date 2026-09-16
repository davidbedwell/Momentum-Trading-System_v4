from __future__ import annotations

from datetime import date, datetime
import math
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

from .derived_market_store import DerivedFeatureDefinition, DerivedFeatureSetDefinition


EARNINGS_FEATURE_SET_ID = "mts_earnings_event_context"
EARNINGS_FEATURE_SET_VERSION = "v1"
NY = ZoneInfo("America/New_York")
MAX_ALIGNMENT_GAP_DAYS = 7


def earnings_event_feature_set() -> DerivedFeatureSetDefinition:
    features = (
        DerivedFeatureDefinition("earnings_surprise_pct", "v1", "Reported EPS surprise percentage from the event record", ("POINT_IN_TIME_EARNINGS_CALENDAR",), 0, "KNOWN_BY_ALIGNED_EVENT_SESSION", "PREDICTOR"),
        DerivedFeatureDefinition("earnings_reported_eps", "v1", "Reported EPS from the event record", ("POINT_IN_TIME_EARNINGS_CALENDAR",), 0, "KNOWN_BY_ALIGNED_EVENT_SESSION", "CONTEXT"),
        DerivedFeatureDefinition("earnings_estimate_eps", "v1", "EPS estimate associated with the event record", ("POINT_IN_TIME_EARNINGS_CALENDAR",), 0, "KNOWN_BY_ALIGNED_EVENT_SESSION", "CONTEXT"),
        DerivedFeatureDefinition("earnings_event_count", "v1", "Number of earnings event records mapped to this security/effective session", ("POINT_IN_TIME_EARNINGS_CALENDAR",), 0, "KNOWN_BY_ALIGNED_EVENT_SESSION", "CONTEXT"),
        DerivedFeatureDefinition("earnings_timing_known", "v1", "One when provider timing is BeforeMarket/AfterMarket or an exact timestamp; zero when conservatively delayed to the next observed session close", ("POINT_IN_TIME_EARNINGS_CALENDAR",), 0, "KNOWN_BY_ALIGNED_EVENT_SESSION", "CONTEXT"),
    )
    return DerivedFeatureSetDefinition(
        EARNINGS_FEATURE_SET_ID,
        EARNINGS_FEATURE_SET_VERSION,
        "Earnings event measurements aligned to the first market close at which the provider-declared event timing was observable.",
        features,
        attributes={
            "event_alignment": "EXACT_TIMESTAMP_OR_PROVIDER_BEFORE_AFTER_MARKET_CLASS",
            "unknown_timing_policy": "CONSERVATIVE_NEXT_OBSERVED_SESSION_CLOSE",
            "future_information": False,
        },
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


def _effective_close_for_event(
    event: Mapping[str, Any], closes: Sequence[datetime]
) -> datetime | None:
    if not closes:
        return None
    if event.get("event_time") not in (None, ""):
        event_time = _parse_event_time(event.get("event_time"))
        if (closes[0].date() - event_time.date()).days > MAX_ALIGNMENT_GAP_DAYS:
            return None
        return next((close for close in closes if close > event_time), None)

    report_date = date.fromisoformat(str(event.get("report_date", "")).strip())
    if (closes[0].date() - report_date).days > MAX_ALIGNMENT_GAP_DAYS:
        return None
    availability = str(event.get("availability_class", "")).strip().upper().replace("_", "")
    if availability in {"BEFOREMARKET", "BMO"}:
        return next((close for close in closes if close.date() >= report_date), None)
    if availability in {"AFTERMARKET", "AMC"}:
        return next((close for close in closes if close.date() > report_date), None)
    # Unknown categorical timing is not guessed. The following observed
    # session's close is conservative whether the release occurred before,
    # during, or after the report-date session.
    return next((close for close in closes if close.date() > report_date), None)


def build_earnings_event_rows(
    events: Sequence[Mapping[str, Any]],
    *,
    market_close_times_by_security: Mapping[str, Sequence[datetime]],
) -> tuple[Mapping[str, Any], ...]:
    """Align each event to the first supplied market close strictly after event time.

    Callers provide actual session-close timestamps; this function does not infer
    holidays or fabricate a trading calendar. Multiple records mapping to the same
    security/session are represented as one explicitly ambiguous row: the event
    count is preserved, conflicting measurements are null, and timing is known
    only when every contributing record has known timing.
    """
    close_index = {
        security_id: tuple(sorted(close.astimezone(NY) for close in closes))
        for security_id, closes in market_close_times_by_security.items()
    }
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for event in events:
        if str(event.get("event_type", "")).upper() != "EARNINGS":
            continue
        security_id = str(event.get("security_id", "")).strip()
        if not security_id or security_id not in close_index:
            continue
        effective_close = _effective_close_for_event(event, close_index[security_id])
        if effective_close is None:
            continue
        effective_date = effective_close.date().isoformat()
        identity = (security_id, effective_date)
        grouped.setdefault(identity, []).append(event)

    def agreed_finite(records: Sequence[Mapping[str, Any]], field: str) -> float | None:
        values = {_finite(record.get(field)) for record in records}
        return next(iter(values)) if len(values) == 1 else None

    output = []
    for (security_id, effective_date), records in grouped.items():
        timing_known = all(
            record.get("event_time") not in (None, "")
            or str(record.get("availability_class", "")).strip().upper().replace("_", "")
            in {"BEFOREMARKET", "BMO", "AFTERMARKET", "AMC"}
            for record in records
        )
        output.append({
            "security_id": security_id,
            "effective_date": effective_date,
            "eligible": all(bool(record.get("eligible", True)) for record in records),
            "earnings_surprise_pct__v1": agreed_finite(records, "surprise_pct"),
            "earnings_reported_eps__v1": agreed_finite(records, "reported_eps"),
            "earnings_estimate_eps__v1": agreed_finite(records, "eps_estimate"),
            "earnings_event_count__v1": float(len(records)),
            "earnings_timing_known__v1": 1.0 if timing_known else 0.0,
        })
    return tuple(sorted(output, key=lambda row: (row["effective_date"], row["security_id"])))
