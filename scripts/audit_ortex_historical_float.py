from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.parse
import urllib.request


ORTEX_BASE_URL = "https://api.ortex.com/api/v1/stock"
ORTEX_API_KEY = "TEST"

DEFAULT_MATRIX = (
    ("GME", None, "high_turnover_retail_interest"),
    ("AMC", None, "dilution_and_reverse_split_history"),
    ("MULN", "2023-01-03", "historical_ticker_resolution"),
    ("FUBO", None, "small_cap_control"),
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark ORTEX historical Free Float and Shares Outstanding using the public TEST key. "
            "This script is standalone and does not wire ORTEX into production Intake."
        )
    )
    parser.add_argument("--tickers", nargs="*", default=None)
    parser.add_argument("--from-date", default="2009-01-01")
    parser.add_argument("--to-date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--output", default=None)
    return parser


def _request(
    *,
    ticker: str,
    endpoint: str,
    from_date: str,
    to_date: str,
    page_size: int,
    ticker_as_of_date: str | None,
) -> object:
    params: dict[str, object] = {
        "from_date": from_date,
        "to_date": to_date,
        "page": 1,
        "page_size": page_size,
    }
    if ticker_as_of_date:
        params["ticker_as_of_date"] = ticker_as_of_date

    query = urllib.parse.urlencode(params)
    url = f"{ORTEX_BASE_URL}/us/{urllib.parse.quote(ticker)}/{endpoint}?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "Ortex-Api-Key": ORTEX_API_KEY,
            "Accept": "application/json",
            "User-Agent": "Momentum-Trading-System-v4 ORTEX provider benchmark",
        },
    )
    with urllib.request.urlopen(request, timeout=60.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _rows(document: object) -> list[dict[str, object]]:
    if isinstance(document, list):
        return [row for row in document if isinstance(row, dict)]
    if not isinstance(document, dict):
        return []
    for key in ("results", "data", "items", "rows"):
        value = document.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def _meta(document: object) -> object:
    if not isinstance(document, dict):
        return None
    for key in ("meta", "restriction", "restrictions"):
        if key in document:
            return document.get(key)
    return None


def _date_values(rows: list[dict[str, object]]) -> list[str]:
    values: list[str] = []
    for row in rows:
        for key in ("date", "effective_date", "from_date", "as_of_date"):
            value = row.get(key)
            if value not in (None, ""):
                values.append(str(value))
                break
    return sorted(values)


def _field_candidates(rows: list[dict[str, object]], tokens: tuple[str, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for key, value in row.items():
            normalized = key.lower().replace("_", "")
            if any(token in normalized for token in tokens) and value is not None:
                counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _endpoint_summary(document: object, endpoint: str) -> dict[str, object]:
    rows = _rows(document)
    dates = _date_values(rows)
    schema_keys = sorted({str(key) for row in rows for key in row.keys()})
    return {
        "endpoint": endpoint,
        "row_count": len(rows),
        "date_start": dates[0] if dates else None,
        "date_end": dates[-1] if dates else None,
        "trial_restriction_metadata": _meta(document),
        "schema_keys": schema_keys,
        "float_field_observation_counts": _field_candidates(rows, ("float",)),
        "shares_outstanding_field_observation_counts": _field_candidates(rows, ("sharesoutstanding", "outstandingshares")),
        "sample": rows[:3],
    }


def _summary(
    *,
    ticker: str,
    ticker_as_of_date: str | None,
    category: str,
    from_date: str,
    to_date: str,
    page_size: int,
) -> dict[str, object]:
    result: dict[str, object] = {
        "ticker": ticker,
        "test_category": category,
        "ticker_as_of_date": ticker_as_of_date,
        "requested_from_date": from_date,
        "requested_to_date": to_date,
        "api_key_mode": "PUBLIC_TEST_KEY",
    }

    for endpoint in ("free_float", "shares_outstanding"):
        try:
            document = _request(
                ticker=ticker,
                endpoint=endpoint,
                from_date=from_date,
                to_date=to_date,
                page_size=page_size,
                ticker_as_of_date=ticker_as_of_date,
            )
            result[endpoint] = _endpoint_summary(document, endpoint)
        except Exception as exc:
            result[endpoint] = {"error": f"{type(exc).__name__}: {exc}"}
    return result


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.tickers:
        matrix = tuple((ticker.upper(), None, "user_selected") for ticker in args.tickers)
    else:
        matrix = DEFAULT_MATRIX

    results = [
        _summary(
            ticker=ticker,
            ticker_as_of_date=ticker_as_of_date,
            category=category,
            from_date=args.from_date,
            to_date=args.to_date,
            page_size=args.page_size,
        )
        for ticker, ticker_as_of_date, category in matrix
    ]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output = Path(args.output or f"/home/ubuntu/MTS_V4_ORTEX_HISTORICAL_FLOAT_AUDIT_{stamp}.txt")
    document = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "provider_coverage_and_temporal_semantics_benchmark_only",
        "provider": "ORTEX",
        "credential": "public TEST key",
        "production_intake_wired": False,
        "scientific_interpretation_performed": False,
        "known_at_status": (
            "UNPROVEN: ORTEX documents the row date as the starting/effective date for Free Float and "
            "Shares Outstanding. This benchmark does not treat that date as market-known-at provenance."
        ),
        "results": results,
    }
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OUTPUT={output}")
    for row in results:
        print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
