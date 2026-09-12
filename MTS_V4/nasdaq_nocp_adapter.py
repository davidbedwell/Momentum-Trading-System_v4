from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from html import unescape
import json
from pathlib import Path
import re
from typing import Iterable, Mapping
import urllib.parse
import urllib.request

from .prospective_validation import ProspectiveValidationError
from .prospective_validation_runtime import AuthoritativeSession


_NASDAQ_NOCP_URL = "https://api.nasdaq.com/api/company/{ticker}/historical-nocp"
_NASDAQ_CALENDAR_URL = "https://www.nasdaqtrader.com/Trader.aspx?id=calendar"
_DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MTS-V4-Prospective-Validation/1.0)",
    "Accept": "application/json,text/html,application/xhtml+xml",
    "Referer": "https://www.nasdaq.com/market-activity/quotes/historical-nocp",
}


class NasdaqNocpAdapterError(ProspectiveValidationError):
    pass


def _request(url: str, *, timeout: float = 30.0) -> bytes:
    request = urllib.request.Request(url, headers=_DEFAULT_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except Exception as exc:
        raise NasdaqNocpAdapterError(
            f"Nasdaq request failed for {url}: {type(exc).__name__}: {exc}"
        ) from exc


def _parse_price(value: object) -> str | None:
    if value in (None, "", "N/A", "n/a"):
        return None
    text = str(value).strip().replace("$", "").replace(",", "")
    try:
        number = float(text)
    except ValueError as exc:
        raise NasdaqNocpAdapterError(f"invalid NOCP value: {value!r}") from exc
    if number <= 0:
        raise NasdaqNocpAdapterError(f"NOCP must be positive: {value!r}")
    return text


def _parse_date(value: object) -> str:
    text = str(value).strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    raise NasdaqNocpAdapterError(f"invalid Nasdaq date: {value!r}")


def _find_rows(document: object) -> list[Mapping[str, object]]:
    if isinstance(document, Mapping):
        rows = document.get("rows")
        if isinstance(rows, list):
            return [item for item in rows if isinstance(item, Mapping)]
        for key in ("data", "table", "historicalNocp", "historicalNOCP"):
            child = document.get(key)
            if child is not None:
                found = _find_rows(child)
                if found:
                    return found
        for child in document.values():
            found = _find_rows(child)
            if found:
                return found
    elif isinstance(document, list):
        if document and all(isinstance(item, Mapping) for item in document):
            return list(document)
        for child in document:
            found = _find_rows(child)
            if found:
                return found
    return []


def fetch_historical_nocp(
    ticker: str, *, timeframe: str = "Y1", limit: int = 5000
) -> dict[str, str | None]:
    """Fetch Nasdaq-published historical NOCP values for one Nasdaq-listed symbol.

    The endpoint is the JSON service backing Nasdaq's Historical NOCP page. The
    parser deliberately accepts several envelope shapes but requires an explicit
    date field and an explicit NOCP/close field in each usable row.
    """

    symbol = ticker.strip().upper()
    if not re.fullmatch(r"[A-Z0-9.\-]+", symbol):
        raise NasdaqNocpAdapterError(f"invalid ticker: {ticker!r}")
    query = urllib.parse.urlencode({"timeframe": timeframe, "limit": int(limit)})
    url = _NASDAQ_NOCP_URL.format(ticker=urllib.parse.quote(symbol)) + "?" + query
    raw = _request(url)
    try:
        document = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise NasdaqNocpAdapterError("Nasdaq NOCP response was not valid JSON") from exc
    rows = _find_rows(document)
    if not rows:
        raise NasdaqNocpAdapterError("Nasdaq NOCP response contained no table rows")

    result: dict[str, str | None] = {}
    for row in rows:
        lowered = {str(k).lower().replace(" ", ""): v for k, v in row.items()}
        date_value = next(
            (lowered[key] for key in ("date", "tradedate", "asofdate") if key in lowered),
            None,
        )
        if date_value is None:
            continue
        price_value = next(
            (
                lowered[key]
                for key in (
                    "nocp",
                    "officialclose",
                    "officialclosingprice",
                    "close",
                    "close/last",
                    "closeprice",
                )
                if key in lowered
            ),
            None,
        )
        if price_value is None:
            continue
        session_date = _parse_date(date_value)
        value = _parse_price(price_value)
        if session_date in result and result[session_date] != value:
            raise NasdaqNocpAdapterError(
                f"conflicting Nasdaq NOCP values for {session_date}"
            )
        result[session_date] = value
    if not result:
        raise NasdaqNocpAdapterError(
            "Nasdaq NOCP response did not contain recognizable date/NOCP columns"
        )
    return result


def _strip_html(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def fetch_nasdaq_closed_dates(*, years: Iterable[int]) -> set[str]:
    """Fetch official NasdaqTrader holiday schedule and return Closed dates.

    Early-close dates remain valid XNAS sessions and are intentionally not
    removed. If a requested year is absent from the official page, fail closed.
    """

    html = _request(_NASDAQ_CALENDAR_URL).decode("utf-8", errors="replace")
    plain = _strip_html(html)
    requested = sorted(set(int(y) for y in years))
    closed: set[str] = set()
    for match in re.finditer(
        r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})\s+[^|]{0,120}?\s+Closed\b",
        plain,
    ):
        try:
            parsed = datetime.strptime(match.group(1), "%B %d, %Y").date()
        except ValueError:
            continue
        if parsed.year in requested:
            closed.add(parsed.isoformat())
    for year in requested:
        if not any(item.startswith(f"{year:04d}-") for item in closed):
            raise NasdaqNocpAdapterError(
                f"official NasdaqTrader calendar did not expose Closed dates for {year}"
            )
    return closed


def xnas_sessions(start: str, end: str, *, closed_dates: set[str]) -> tuple[str, ...]:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    if end_date < start_date:
        raise NasdaqNocpAdapterError("calendar end precedes start")
    sessions: list[str] = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5 and current.isoformat() not in closed_dates:
            sessions.append(current.isoformat())
        current += timedelta(days=1)
    return tuple(sessions)


def load_share_multipliers(path: str | Path | None) -> dict[str, str]:
    """Load exact mandatory share multipliers keyed by effective session date.

    The file is optional only because an empty mapping means no mandatory share
    transformation is effective inside the requested snapshot window. The
    adapter records that assertion explicitly in snapshot provenance.
    """

    if path is None:
        return {}
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise NasdaqNocpAdapterError("share multiplier file must be a JSON object")
    result: dict[str, str] = {}
    for key, value in raw.items():
        session_date = date.fromisoformat(str(key)).isoformat()
        text = str(value)
        try:
            if float(text) <= 0:
                raise ValueError
        except ValueError as exc:
            raise NasdaqNocpAdapterError(
                f"invalid mandatory share multiplier for {session_date}: {value!r}"
            ) from exc
        result[session_date] = text
    return result


def build_authoritative_snapshot(
    *,
    ticker: str,
    source_subject_id: str,
    start_date: str,
    end_date: str,
    share_multipliers: Mapping[str, str] | None = None,
) -> dict[str, object]:
    """Build the raw-price custody snapshot consumed by prospective validation."""

    years = range(date.fromisoformat(start_date).year, date.fromisoformat(end_date).year + 1)
    closed = fetch_nasdaq_closed_dates(years=years)
    calendar = xnas_sessions(start_date, end_date, closed_dates=closed)
    nocp = fetch_historical_nocp(ticker)
    multipliers = dict(share_multipliers or {})

    sessions: list[AuthoritativeSession] = []
    for index, session_date in enumerate(calendar):
        sessions.append(
            AuthoritativeSession(
                session_index=index,
                session_date=session_date,
                source_subject_id=source_subject_id,
                source_identity="NASDAQ_NOCP",
                nocp=nocp.get(session_date),
                mandatory_share_multiplier=multipliers.get(session_date, "1"),
            )
        )
    if not sessions:
        raise NasdaqNocpAdapterError("no XNAS sessions in requested snapshot range")

    return {
        "format": "MTS_V4_NASDAQ_NOCP_AUTHORITATIVE_SNAPSHOT_V1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "ticker": ticker.upper(),
        "source_subject_id": source_subject_id,
        "source_identity": "NASDAQ_NOCP",
        "nocp_source": _NASDAQ_NOCP_URL.format(ticker=ticker.upper()),
        "calendar_source": _NASDAQ_CALENDAR_URL,
        "corporate_action_policy": {
            "representation": "mandatory_share_multiplier effective by XNAS session",
            "explicit_multipliers": multipliers,
            "no_unlisted_actions_asserted": True,
        },
        "coverage_start": sessions[0].session_date,
        "coverage_end": sessions[-1].session_date,
        "sessions": [asdict(item) for item in sessions],
    }


def save_snapshot(path: str | Path, snapshot: Mapping[str, object]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(snapshot), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(target)
