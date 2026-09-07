from __future__ import annotations

import base64
import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping, Sequence

from .contracts import SubjectMetadata
from .intake import IntakePayload


class LiveSourceError(RuntimeError):
    pass


def _schema(rows: Sequence[Mapping[str, object]]) -> tuple[str, ...]:
    names: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            name = str(key)
            if name not in seen:
                seen.add(name)
                names.append(name)
    return tuple(names)


def _coverage(rows: Sequence[Mapping[str, object]], candidates: Sequence[str]) -> tuple[str | None, str | None]:
    values: list[str] = []
    for row in rows:
        for field in candidates:
            value = row.get(field)
            if value not in (None, ""):
                values.append(str(value))
                break
    return (min(values), max(values)) if values else (None, None)


def _json_request(url: str, *, headers: Mapping[str, str] | None = None, data: bytes | None = None, timeout: float = 60.0):
    request = urllib.request.Request(url, data=data, headers=dict(headers or {}), method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), {str(k).lower(): str(v) for k, v in response.headers.items()}
    except Exception as exc:
        raise LiveSourceError(f"request failed for {url}: {type(exc).__name__}: {exc}") from exc


def _rows_from_document(document: object) -> list[dict[str, object]]:
    if isinstance(document, list):
        return [dict(row) for row in document if isinstance(row, Mapping)]
    if isinstance(document, Mapping):
        data = document.get("data")
        if isinstance(data, list):
            return [dict(row) for row in data if isinstance(row, Mapping)]
        if isinstance(data, Mapping):
            nested = data.get("data")
            if isinstance(nested, list):
                return [dict(row) for row in nested if isinstance(row, Mapping)]
    raise LiveSourceError("provider response did not contain a row list")


class CompositeEvidenceSource:
    def __init__(self, *sources) -> None:
        self._sources = tuple(sources)

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        for source in self._sources:
            yield from source.acquire(subject)


@dataclass(frozen=True, slots=True)
class YFinanceDailyOhlcvSource:
    period: str = "2y"

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise LiveSourceError("yfinance is required for YFinanceDailyOhlcvSource") from exc
        frame = yf.download(subject.ticker, period=self.period, interval="1d", auto_adjust=False, progress=False, threads=False)
        if frame.empty:
            raise LiveSourceError(f"yfinance returned no daily rows for {subject.ticker}")
        if getattr(frame.columns, "nlevels", 1) > 1:
            frame.columns = [str(item[0]).lower() for item in frame.columns]
        else:
            frame.columns = [str(item).lower() for item in frame.columns]
        frame = frame.reset_index()
        frame.columns = [str(item).lower() for item in frame.columns]
        date_col = "date" if "date" in frame.columns else frame.columns[0]
        frame[date_col] = frame[date_col].astype(str).str[:10]
        keep = [name for name in (date_col, "open", "high", "low", "close", "adj close", "volume") if name in frame.columns]
        rows = frame[keep].where(frame[keep].notna(), None).to_dict(orient="records")
        yield IntakePayload(
            payload=rows,
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="YFINANCE_DAILY",
            coverage_start=str(rows[0][date_col]),
            coverage_end=str(rows[-1][date_col]),
            row_count=len(rows),
            schema=tuple(keep),
            provenance={"provider": "yfinance", "period": self.period, "interval": "1d", "acquired_at_utc": datetime.now(timezone.utc).isoformat()},
            neutral_semantics=("Observed daily open, high, low, close and aggregate volume. These values describe market path and aggregate activity; they do not establish intent, causation, predictiveness, accumulation, distribution, or trade utility."),
        )


class _UnusualWhalesBase:
    base_url = "https://api.unusualwhales.com"

    def __init__(self, api_key: str | None = None, *, limit: int = 500) -> None:
        self.api_key = (api_key if api_key is not None else os.environ.get("UNUSUAL_WHALES_API_KEY", "")).strip()
        if not self.api_key:
            raise LiveSourceError("UNUSUAL_WHALES_API_KEY is required")
        self.limit = int(limit)

    def _get(self, path: str, params: Mapping[str, object] | None = None) -> list[dict[str, object]]:
        query = urllib.parse.urlencode({k: v for k, v in (params or {}).items() if v is not None})
        url = self.base_url + path + (("?" + query) if query else "")
        document, _ = _json_request(url, headers={"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"})
        return _rows_from_document(document)


class UnusualWhalesDarkPoolSource(_UnusualWhalesBase):
    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        rows = self._get(f"/api/darkpool/{urllib.parse.quote(subject.ticker.upper())}", {"limit": self.limit})
        start, end = _coverage(rows, ("executed_at", "date", "timestamp"))
        yield IntakePayload(
            payload=rows,
            evidence_type="OFF_EXCHANGE_DARKPOOL_PRINTS",
            artifact_type="NORMALIZED_DATASET",
            source_identity="UNUSUAL_WHALES_DARKPOOL",
            coverage_start=start,
            coverage_end=end,
            row_count=len(rows),
            schema=_schema(rows),
            provenance={"provider": "Unusual Whales", "endpoint": f"/api/darkpool/{subject.ticker.upper()}", "limit": self.limit, "acquired_at_utc": datetime.now(timezone.utc).isoformat()},
            neutral_semantics=("Source-defined dark-pool/off-exchange stock prints for the requested ticker. Off-exchange execution does not by itself establish institutional identity, buyer or seller intent, accumulation, distribution, bullishness, bearishness, price suppression, or causation. Provider-side classifications and NBBO comparisons are observations or estimates under the provider's definitions."),
        )


class UnusualWhalesFlowAlertsSource(_UnusualWhalesBase):
    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        rows = self._get("/api/option-trades/flow-alerts", {"ticker_symbol": subject.ticker.upper(), "limit": self.limit})
        start, end = _coverage(rows, ("start_time", "end_time", "executed_at", "created_at", "date"))
        yield IntakePayload(
            payload=rows,
            evidence_type="LARGE_UNUSUAL_OPTIONS_ACTIVITY",
            artifact_type="NORMALIZED_DATASET",
            source_identity="UNUSUAL_WHALES_FLOW_ALERTS",
            coverage_start=start,
            coverage_end=end,
            row_count=len(rows),
            schema=_schema(rows),
            provenance={"provider": "Unusual Whales", "endpoint": "/api/option-trades/flow-alerts", "ticker_symbol": subject.ticker.upper(), "limit": self.limit, "acquired_at_utc": datetime.now(timezone.utc).isoformat()},
            neutral_semantics=("Unusual Whales source-defined options flow alerts aggregate option transactions that meet provider alert rules. Large or unusual option activity may reflect directional exposure, hedging, volatility positioning, spreads, liquidity provision, opening or closing activity, or combinations of these. Ask-side calls are not inherently bullish and bid-side puts are not inherently bearish; multi-leg context can materially change interpretation."),
        )


class UnusualWhalesGreekExposureByExpirySource(_UnusualWhalesBase):
    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        ticker = subject.ticker.upper()
        endpoint = f"/api/stock/{urllib.parse.quote(ticker)}/greek-exposure/expiry"
        rows = self._get(endpoint)
        start, end = _coverage(rows, ("date", "timestamp", "updated_at", "created_at"))
        yield IntakePayload(
            payload=rows,
            evidence_type="OPTIONS_GREEK_EXPOSURE_BY_EXPIRY",
            artifact_type="NORMALIZED_DATASET",
            source_identity="UNUSUAL_WHALES_GREEK_EXPOSURE_BY_EXPIRY",
            coverage_start=start,
            coverage_end=end,
            row_count=len(rows),
            schema=_schema(rows),
            provenance={
                "provider": "Unusual Whales",
                "endpoint": endpoint,
                "scope": "TICKER",
                "ticker": ticker,
                "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
            },
            neutral_semantics=("Provider-calculated options Greek exposure aggregated by expiration for the requested ticker. Exposure values describe the provider's Greek-exposure calculations and concentration across expirations; they do not by themselves establish dealer identity, dealer positioning, hedging direction, support or resistance, future price direction, causation, predictiveness, or trade utility."),
        )


class UnusualWhalesFlowByExpirySource(_UnusualWhalesBase):
    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        ticker = subject.ticker.upper()
        endpoint = f"/api/stock/{urllib.parse.quote(ticker)}/flow-per-expiry"
        rows = self._get(endpoint)
        start, end = _coverage(rows, ("date", "timestamp", "updated_at", "created_at"))
        yield IntakePayload(
            payload=rows,
            evidence_type="OPTIONS_FLOW_BY_EXPIRY",
            artifact_type="NORMALIZED_DATASET",
            source_identity="UNUSUAL_WHALES_FLOW_BY_EXPIRY",
            coverage_start=start,
            coverage_end=end,
            row_count=len(rows),
            schema=_schema(rows),
            provenance={
                "provider": "Unusual Whales",
                "endpoint": endpoint,
                "scope": "TICKER",
                "ticker": ticker,
                "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
            },
            neutral_semantics=("Provider-defined options activity grouped by contract expiration for the requested ticker, including provider-returned call/put, premium, side, volume, trade-count, and related expiry-level fields where available. Ask-side, bid-side, call, put, premium, volume, and out-of-the-money classifications are observations under provider definitions; they do not by themselves establish opening or closing intent, economic direction, bullishness, bearishness, causation, predictiveness, or trade utility."),
        )


class FinraWeeklyOffExchangeSource:
    token_url = "https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token?grant_type=client_credentials"
    data_url = "https://api.finra.org/data/group/otcMarket/name/weeklySummary"

    def __init__(self, client_id: str | None = None, client_secret: str | None = None) -> None:
        self.client_id = (client_id if client_id is not None else os.environ.get("FINRA_API_CLIENT_ID", "")).strip()
        self.client_secret = (client_secret if client_secret is not None else os.environ.get("FINRA_API_CLIENT_SECRET", "")).strip()
        if not self.client_id or not self.client_secret:
            raise LiveSourceError("FINRA_API_CLIENT_ID and FINRA_API_CLIENT_SECRET are required")

    def _token(self) -> str:
        basic = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        document, _ = _json_request(self.token_url, headers={"Authorization": f"Basic {basic}", "Accept": "application/json"}, data=b"")
        if not isinstance(document, Mapping) or not str(document.get("access_token", "")).strip():
            raise LiveSourceError("FINRA token response lacked access_token")
        return str(document["access_token"])

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        fields = ["issueSymbolIdentifier", "issueName", "MPID", "marketParticipantName", "tierIdentifier", "summaryStartDate", "weekStartDate", "totalWeeklyTradeCount", "totalWeeklyShareQuantity", "productTypeCode", "summaryTypeCode", "lastUpdateDate", "initialPublishedDate", "lastReportedDate"]
        output: list[dict[str, object]] = []
        token = self._token()
        for summary_type in ("ATS_W_SMBL", "OTC_W_SMBL", "ATS_W_SMBL_FIRM"):
            body = json.dumps({"fields": fields, "compareFilters": [{"compareType": "EQUAL", "fieldName": "summaryTypeCode", "fieldValue": summary_type}, {"compareType": "EQUAL", "fieldName": "issueSymbolIdentifier", "fieldValue": subject.ticker.upper()}], "limit": 5000, "offset": 0}).encode()
            document, _ = _json_request(self.data_url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "application/json", "Data-API-Version": "1"}, data=body)
            if not isinstance(document, list):
                raise LiveSourceError("FINRA weeklySummary response was not a list")
            output.extend(dict(row) for row in document if isinstance(row, Mapping))
        start, end = _coverage(output, ("weekStartDate", "summaryStartDate"))
        yield IntakePayload(
            payload=output,
            evidence_type="FINRA_OTC_TRANSPARENCY_WEEKLY",
            artifact_type="NORMALIZED_DATASET",
            source_identity="FINRA_OTC_TRANSPARENCY_WEEKLY_SUMMARY",
            coverage_start=start,
            coverage_end=end,
            row_count=len(output),
            schema=_schema(output),
            provenance={"provider": "FINRA", "dataset": "weeklySummary", "summary_types": ["ATS_W_SMBL", "OTC_W_SMBL", "ATS_W_SMBL_FIRM"], "acquired_at_utc": datetime.now(timezone.utc).isoformat()},
            neutral_semantics=("FINRA OTC Transparency weekly summaries report source-defined ATS and non-ATS OTC trade counts and share quantities. ATS activity is a subset of off-exchange activity; non-ATS OTC activity is not a dark pool. These records do not identify economic buyer/seller intent, institutional ownership, accumulation, distribution, bullishness, bearishness, or causation."),
        )


def standard_live_market_source() -> CompositeEvidenceSource:
    return CompositeEvidenceSource(
        YFinanceDailyOhlcvSource(),
        UnusualWhalesDarkPoolSource(),
        UnusualWhalesFlowAlertsSource(),
        UnusualWhalesGreekExposureByExpirySource(),
        UnusualWhalesFlowByExpirySource(),
        FinraWeeklyOffExchangeSource(),
    )
