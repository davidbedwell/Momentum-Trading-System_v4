from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import io
from typing import Iterable, Mapping, Sequence
import urllib.request

from .contracts import SubjectMetadata
from .intake import IntakePayload


CURRENT_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


class UniverseSourceError(RuntimeError):
    pass


def _ticker_for_yfinance(value: object) -> str:
    return str(value).strip().upper().replace(".", "-")


def _security_id_from_cik_and_ticker(cik: object, ticker: object) -> str:
    """Frozen calibration security identity, distinct across issuer share classes."""
    raw = str(cik).strip()
    if raw.endswith(".0"):
        raw = raw[:-2]
    if not raw.isdigit():
        raise UniverseSourceError(f"invalid CIK: {cik!r}")
    normalized_ticker = _ticker_for_yfinance(ticker)
    if not normalized_ticker:
        raise UniverseSourceError("ticker cannot be blank")
    safe_ticker = "".join(character if character.isalnum() else "_" for character in normalized_ticker)
    return f"CAL_SEC_CIK_{int(raw):010d}_{safe_ticker}"


def normalize_current_sp500_rows(
    records: Sequence[Mapping[str, object]],
    *,
    acquisition_floor: str,
    source_identity: str,
) -> tuple[Mapping[str, object], ...]:
    date.fromisoformat(acquisition_floor)
    rows: list[dict[str, object]] = []
    for record in records:
        raw_added = str(record.get("Date added", "")).strip()
        if not raw_added or raw_added.lower() in {"nan", "none", "nat"}:
            start = acquisition_floor
        else:
            start = max(date.fromisoformat(raw_added[:10]).isoformat(), acquisition_floor)
        rows.append({
            "security_id": _security_id_from_cik_and_ticker(
                record.get("CIK", ""), record.get("Symbol", "")
            ),
            "ticker": _ticker_for_yfinance(record.get("Symbol", "")),
            "start_date": start,
            "end_date": None,
            "sector_id": str(record.get("GICS Sector", "")).strip() or None,
            "industry_id": str(record.get("GICS Sub-Industry", "")).strip() or None,
            "source_identity": source_identity,
        })
    rows.sort(key=lambda item: str(item["security_id"]))
    security_ids = [str(item["security_id"]) for item in rows]
    tickers = [str(item["ticker"]) for item in rows]
    if len(security_ids) != len(set(security_ids)):
        raise UniverseSourceError("current constituent evidence contains duplicate calibration security identities")
    if len(tickers) != len(set(tickers)):
        raise UniverseSourceError("current constituent evidence contains duplicate normalized tickers")
    if not 490 <= len(rows) <= 510:
        raise UniverseSourceError(f"unexpected current S&P constituent count: {len(rows)}")
    return tuple(rows)


@dataclass(frozen=True, slots=True)
class CurrentSp500CalibrationUniverseSource:
    """Acquire a dated current-member universe through Intake for calibration only.

    This source is intentionally not represented as authoritative point-in-time
    history. Former members are absent, so historical research remains
    survivorship-biased. CIK identifies the issuer, so the frozen calibration
    security identity combines CIK and ticker to keep separate share classes
    distinct; it is not an authoritative permanent security master.
    """

    as_of_date: str
    acquisition_floor: str

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        if subject.attributes.get("research_scope_type") != "UNIVERSE":
            raise UniverseSourceError("current S&P universe source requires a UNIVERSE research scope")
        date.fromisoformat(self.as_of_date)
        date.fromisoformat(self.acquisition_floor)
        try:
            import pandas as pd
        except ImportError as exc:
            raise UniverseSourceError("pandas with HTML-table support is required") from exc
        request = urllib.request.Request(
            CURRENT_SP500_URL,
            headers={"User-Agent": "Momentum-Trading-System-v4/1.0 universe-calibration"},
        )
        try:
            with urllib.request.urlopen(request, timeout=60.0) as response:
                source_html = response.read().decode("utf-8")
        except Exception as exc:
            raise UniverseSourceError(
                f"current S&P constituent acquisition failed: {type(exc).__name__}: {exc}"
            ) from exc
        tables = pd.read_html(io.StringIO(source_html))
        required = {"Symbol", "GICS Sector", "GICS Sub-Industry", "Date added", "CIK"}
        candidates = [
            table
            for table in tables
            if required.issubset({str(column) for column in table.columns})
        ]
        if len(candidates) != 1:
            raise UniverseSourceError(
                f"expected exactly one current S&P constituent table; found {len(candidates)}"
            )
        source_identity = f"WIKIPEDIA_CURRENT_SP500_AS_OF_{self.as_of_date}_CALIBRATION_ONLY"
        rows = normalize_current_sp500_rows(
            candidates[0].to_dict(orient="records"),
            acquisition_floor=self.acquisition_floor,
            source_identity=source_identity,
        )
        yield IntakePayload(
            payload=rows,
            evidence_type="CURRENT_UNIVERSE_MEMBERSHIP_CALIBRATION",
            artifact_type="NORMALIZED_DATASET",
            source_identity=source_identity,
            coverage_start=min(str(row["start_date"]) for row in rows),
            coverage_end=self.as_of_date,
            row_count=len(rows),
            schema=("security_id", "ticker", "start_date", "end_date", "sector_id", "industry_id", "source_identity"),
            provenance={
                "provider": "Wikipedia",
                "source_url": CURRENT_SP500_URL,
                "as_of_date": self.as_of_date,
                "acquisition_floor": self.acquisition_floor,
                "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
                "point_in_time_history": False,
                "former_members_included": False,
                "survivorship_bias": True,
                "authorized_use": "ENGINEERING_AND_AI_CALIBRATION_ONLY",
            },
            neutral_semantics=(
                "Dated current S&P 500 constituents with source-reported entry dates and frozen "
                "CIK-plus-share-class calibration identity, "
                "and current sector attributes. Former constituents are absent. This evidence can exercise "
                "universe plumbing and AI calibration but cannot establish authoritative historical PIT results."
            ),
        )
