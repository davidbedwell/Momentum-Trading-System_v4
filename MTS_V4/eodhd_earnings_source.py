from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
import math
from typing import Any, Callable, Iterable, Mapping
import urllib.parse
import urllib.request

from .contracts import SubjectMetadata
from .intake import IntakePayload


EODHD_EARNINGS_SCHEMA = (
    "security_id", "ticker", "event_type", "report_date", "fiscal_period_end",
    "availability_class", "reported_eps", "eps_estimate", "surprise_pct", "currency",
)


def _finite(value: object, *, field: str, required: bool = True) -> float | None:
    if value in (None, "") and not required:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"EODHD earnings {field} is missing or nonnumeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"EODHD earnings {field} is not finite")
    return number


def _default_fetch(url: str, timeout: float) -> object:
    request = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "MTS-V4/1.0"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


@dataclass(frozen=True, slots=True)
class EODHDEarningsCalendarSource:
    api_token: str
    start_date: str
    end_date: str
    timeout_seconds: float = 30.0
    base_url: str = "https://eodhd.com/api/calendar/earnings"
    fetch_json: Callable[[str, float], object] = _default_fetch

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        if not self.api_token.strip():
            raise ValueError("EODHD API token cannot be blank")
        start = date.fromisoformat(self.start_date)
        end = date.fromisoformat(self.end_date)
        if start > end:
            raise ValueError("earnings acquisition start_date cannot follow end_date")
        security_id = str(subject.attributes.get("security_id", "")).strip()
        if not security_id:
            raise ValueError("earnings subject requires stable security_id attribute")
        ticker = subject.ticker.strip().upper()
        params = urllib.parse.urlencode({
            "symbols": f"{ticker}.US", "from": self.start_date, "to": self.end_date,
            "fmt": "json", "api_token": self.api_token,
        })
        document = self.fetch_json(f"{self.base_url}?{params}", self.timeout_seconds)
        raw_rows = document.get("earnings", ()) if isinstance(document, Mapping) else document
        if not isinstance(raw_rows, list):
            raise ValueError("EODHD earnings response does not contain an earnings list")

        normalized: list[dict[str, Any]] = []
        identities: set[tuple[str, str]] = set()
        for raw in raw_rows:
            if not isinstance(raw, Mapping) or raw.get("actual") in (None, ""):
                continue
            report_date = str(raw.get("report_date", "")).strip()
            fiscal_period = str(raw.get("date", "")).strip()
            parsed_report = date.fromisoformat(report_date)
            date.fromisoformat(fiscal_period)
            if not start <= parsed_report <= end:
                continue
            code = str(raw.get("code", "")).split(".", 1)[0].upper()
            if code and code != ticker:
                raise ValueError(f"EODHD response symbol mismatch: requested={ticker} received={code}")
            identity = (report_date, fiscal_period)
            if identity in identities:
                raise ValueError(f"duplicate EODHD earnings report/period identity: {identity}")
            identities.add(identity)
            actual = _finite(raw.get("actual"), field="actual")
            estimate = _finite(raw.get("estimate"), field="estimate", required=False)
            surprise = _finite(raw.get("percent"), field="percent", required=False)
            availability = str(raw.get("before_after_market", "")).strip()
            normalized.append({
                "security_id": security_id,
                "ticker": ticker,
                "event_type": "EARNINGS",
                "report_date": report_date,
                "fiscal_period_end": fiscal_period,
                "availability_class": availability,
                "reported_eps": actual,
                "eps_estimate": estimate,
                "surprise_pct": surprise,
                "currency": str(raw.get("currency", "")).strip() or None,
            })
        normalized.sort(key=lambda row: (row["report_date"], row["fiscal_period_end"]))
        coverage_start = normalized[0]["report_date"] if normalized else None
        coverage_end = normalized[-1]["report_date"] if normalized else None
        yield IntakePayload(
            payload=normalized,
            evidence_type="POINT_IN_TIME_EARNINGS_CALENDAR",
            artifact_type="TABULAR_EVENT_SERIES",
            source_identity="EODHD_CORPORATE_EVENTS_CALENDAR",
            coverage_start=coverage_start,
            coverage_end=coverage_end,
            row_count=len(normalized),
            schema=EODHD_EARNINGS_SCHEMA,
            provenance={
                "provider": "EODHD", "endpoint": "/api/calendar/earnings",
                "symbol": f"{ticker}.US", "requested_start": self.start_date,
                "requested_end": self.end_date,
                "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
                "estimate_semantics": "PROVIDER_ASSOCIATED_HISTORICAL_CONSENSUS",
                "timing_semantics": "PROVIDER_BEFORE_AFTER_MARKET_CLASS",
            },
            neutral_semantics=(
                "Historical reported earnings records, associated consensus estimates, surprise "
                "percentages, and provider-declared before/after-market availability classes."
            ),
        )
