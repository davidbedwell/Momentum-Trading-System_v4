from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

from .contracts import SubjectMetadata
from .intake import IntakePayload


MARKET_STRUCTURE_SCHEMA = (
    "as_of_utc",
    "ticker",
    "float_shares",
    "shares_outstanding",
    "average_volume_10d",
    "average_volume_3m",
    "market_cap",
    "short_percent_of_float",
)

CATALYST_SCHEMA = (
    "event_time",
    "event_date",
    "event_type",
    "event_count",
    "headline",
    "publisher",
    "source_url",
    "eps_estimate",
    "reported_eps",
    "surprise_pct",
)

INTRADAY_SCHEMA = (
    "timestamp",
    "date",
    "market_time",
    "session",
    "open",
    "high",
    "low",
    "close",
    "volume",
)


def _schema(rows: Sequence[Mapping[str, object]], fallback: Sequence[str]) -> tuple[str, ...]:
    if not rows:
        return tuple(fallback)
    names: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            name = str(key)
            if name not in seen:
                seen.add(name)
                names.append(name)
    return tuple(names)


def _coverage(rows: Sequence[Mapping[str, object]], field: str) -> tuple[str | None, str | None]:
    values = [str(row[field]) for row in rows if row.get(field) not in (None, "")]
    return (min(values), max(values)) if values else (None, None)


def _scalar(value: object) -> object:
    if value is None:
        return None
    try:
        if value != value:
            return None
    except Exception:
        pass
    if hasattr(value, "item"):
        try:
            return value.item()  # type: ignore[union-attr]
        except Exception:
            pass
    return value


def _iso_time(value: object) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    return text or None


@dataclass(frozen=True, slots=True)
class YFinanceMarketStructureSource:
    """Acquire a current ticker-structure snapshot, including public float.

    The snapshot is deliberately separate from historical OHLCV. Current float
    must not be projected backward across historical observations unless the AI
    Research Director explicitly chooses and justifies that approximation.
    """

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError("yfinance is required for YFinanceMarketStructureSource") from exc

        acquired_at = datetime.now(timezone.utc).isoformat()
        rows: list[dict[str, object]] = []
        acquisition_error: str | None = None
        try:
            info = yf.Ticker(subject.ticker).get_info() or {}
            if isinstance(info, Mapping):
                rows.append(
                    {
                        "as_of_utc": acquired_at,
                        "ticker": subject.ticker.upper(),
                        "float_shares": _scalar(info.get("floatShares")),
                        "shares_outstanding": _scalar(info.get("sharesOutstanding")),
                        "average_volume_10d": _scalar(info.get("averageDailyVolume10Day")),
                        "average_volume_3m": _scalar(info.get("averageVolume")),
                        "market_cap": _scalar(info.get("marketCap")),
                        "short_percent_of_float": _scalar(info.get("shortPercentOfFloat")),
                    }
                )
        except Exception as exc:
            acquisition_error = f"{type(exc).__name__}: {exc}"

        yield IntakePayload(
            payload=rows,
            evidence_type="MARKET_STRUCTURE_SNAPSHOT",
            artifact_type="NORMALIZED_DATASET",
            source_identity="YFINANCE_MARKET_STRUCTURE",
            coverage_start=acquired_at if rows else None,
            coverage_end=acquired_at if rows else None,
            row_count=len(rows),
            schema=_schema(rows, MARKET_STRUCTURE_SCHEMA),
            provenance={
                "provider": "yfinance",
                "scope": "CURRENT_SNAPSHOT",
                "ticker": subject.ticker.upper(),
                "acquired_at_utc": acquired_at,
                "acquisition_error": acquisition_error,
            },
            neutral_semantics=(
                "Point-in-time ticker structure from yfinance, including public float and shares outstanding when "
                "available. Float is a current snapshot, not a historical series. It may support current-session "
                "turnover calculations, but must not be silently back-projected into earlier dates. These values do "
                "not establish direction, momentum, causation, catalyst significance, predictiveness, or trade utility."
            ),
        )


@dataclass(frozen=True, slots=True)
class YFinanceCatalystEventsSource:
    """Acquire provider-available earnings events and recent ticker news."""

    earnings_limit: int = 100

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError("yfinance is required for YFinanceCatalystEventsSource") from exc

        ticker = yf.Ticker(subject.ticker)
        rows: list[dict[str, object]] = []
        errors: list[str] = []

        try:
            earnings = ticker.get_earnings_dates(limit=self.earnings_limit)
            if earnings is not None and not earnings.empty:
                for index, record in earnings.iterrows():
                    event_time = _iso_time(index)
                    rows.append(
                        {
                            "event_time": event_time,
                            "event_date": event_time[:10] if event_time else None,
                            "event_type": "EARNINGS",
                            "event_count": 1,
                            "headline": None,
                            "publisher": "yfinance",
                            "source_url": None,
                            "eps_estimate": _scalar(record.get("EPS Estimate")),
                            "reported_eps": _scalar(record.get("Reported EPS")),
                            "surprise_pct": _scalar(record.get("Surprise(%)")),
                        }
                    )
        except Exception as exc:
            errors.append(f"earnings:{type(exc).__name__}:{exc}")

        try:
            news = ticker.news or []
            for item in news:
                if not isinstance(item, Mapping):
                    continue
                content = item.get("content") if isinstance(item.get("content"), Mapping) else item
                assert isinstance(content, Mapping)
                event_time = _iso_time(
                    content.get("pubDate")
                    or content.get("displayTime")
                    or item.get("providerPublishTime")
                )
                provider = content.get("provider")
                publisher = provider.get("displayName") if isinstance(provider, Mapping) else item.get("publisher")
                canonical = content.get("canonicalUrl")
                source_url = canonical.get("url") if isinstance(canonical, Mapping) else item.get("link")
                rows.append(
                    {
                        "event_time": event_time,
                        "event_date": event_time[:10] if event_time else None,
                        "event_type": "NEWS",
                        "event_count": 1,
                        "headline": content.get("title") or item.get("title"),
                        "publisher": publisher,
                        "source_url": source_url,
                        "eps_estimate": None,
                        "reported_eps": None,
                        "surprise_pct": None,
                    }
                )
        except Exception as exc:
            errors.append(f"news:{type(exc).__name__}:{exc}")

        rows.sort(key=lambda row: str(row.get("event_time") or ""))
        start, end = _coverage(rows, "event_time")
        acquired_at = datetime.now(timezone.utc).isoformat()
        yield IntakePayload(
            payload=rows,
            evidence_type="CORPORATE_EVENT_AND_NEWS",
            artifact_type="NORMALIZED_DATASET",
            source_identity="YFINANCE_CATALYST_EVENTS",
            coverage_start=start,
            coverage_end=end,
            row_count=len(rows),
            schema=_schema(rows, CATALYST_SCHEMA),
            provenance={
                "provider": "yfinance",
                "ticker": subject.ticker.upper(),
                "earnings_limit": self.earnings_limit,
                "news_scope": "PROVIDER_AVAILABLE_RECENT_NEWS_NOT_GUARANTEED_COMPLETE_HISTORICAL_COVERAGE",
                "acquired_at_utc": acquired_at,
                "partial_acquisition_errors": errors,
            },
            neutral_semantics=(
                "Timestamped provider-available earnings records and recent news items. Event presence is not proof that "
                "the event caused a market move, and NEWS is not a deterministic catalyst classification. Coverage, "
                "especially news history, may be incomplete. The AI Research Director retains authority to classify, "
                "test, reject, combine, or ignore candidate catalyst relationships."
            ),
        )


@dataclass(frozen=True, slots=True)
class YFinanceIntradaySource:
    """Acquire recent 5-minute bars including pre/post-market observations.

    Intraday provider history is intentionally separate from the 20-year daily
    series. It supports neutral measurement of premarket structure, opening
    ranges, VWAP, and volume trajectory without implying those ideas work.
    """

    period: str = "60d"
    interval: str = "5m"
    prepost: bool = True

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError("yfinance is required for YFinanceIntradaySource") from exc

        frame = yf.download(
            subject.ticker,
            period=self.period,
            interval=self.interval,
            auto_adjust=False,
            prepost=self.prepost,
            progress=False,
            threads=False,
        )
        rows: list[dict[str, object]] = []
        acquisition_error: str | None = None
        try:
            if not frame.empty:
                if getattr(frame.columns, "nlevels", 1) > 1:
                    frame.columns = [str(item[0]).lower() for item in frame.columns]
                else:
                    frame.columns = [str(item).lower() for item in frame.columns]
                eastern = ZoneInfo("America/New_York")
                for stamp, record in frame.iterrows():
                    dt = stamp.to_pydatetime() if hasattr(stamp, "to_pydatetime") else stamp
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    local = dt.astimezone(eastern)
                    hhmm = local.hour * 60 + local.minute
                    session = (
                        "PREMARKET" if 240 <= hhmm < 570 else
                        "REGULAR" if 570 <= hhmm < 960 else
                        "AFTER_HOURS"
                    )
                    rows.append(
                        {
                            "timestamp": dt.astimezone(timezone.utc).isoformat(),
                            "date": local.date().isoformat(),
                            "market_time": local.strftime("%H:%M"),
                            "session": session,
                            "open": _scalar(record.get("open")),
                            "high": _scalar(record.get("high")),
                            "low": _scalar(record.get("low")),
                            "close": _scalar(record.get("close")),
                            "volume": _scalar(record.get("volume")),
                        }
                    )
        except Exception as exc:
            acquisition_error = f"{type(exc).__name__}: {exc}"

        start, end = _coverage(rows, "timestamp")
        yield IntakePayload(
            payload=rows,
            evidence_type="INTRADAY_OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="YFINANCE_INTRADAY_5M",
            coverage_start=start,
            coverage_end=end,
            row_count=len(rows),
            schema=_schema(rows, INTRADAY_SCHEMA),
            provenance={
                "provider": "yfinance",
                "period": self.period,
                "interval": self.interval,
                "prepost": self.prepost,
                "market_timezone": "America/New_York",
                "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
                "acquisition_error": acquisition_error,
            },
            neutral_semantics=(
                "Recent provider-available five-minute OHLCV including extended hours. Session labels are mechanical "
                "clock classifications only. Premarket highs, opening ranges, VWAP, and related measurements are not "
                "signals or evidence of predictiveness until interpreted and tested by the AI Research Director."
            ),
        )


def standard_market_source_with_research_leads():
    """Existing live evidence plus neutral participation/catalyst/intraday inputs."""
    from .live_sources import CompositeEvidenceSource, standard_live_market_source

    return CompositeEvidenceSource(
        standard_live_market_source(),
        YFinanceMarketStructureSource(),
        YFinanceCatalystEventsSource(),
        YFinanceIntradaySource(),
    )
