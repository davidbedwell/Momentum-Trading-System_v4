from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request


ASKEDGAR_URL = "https://eapi.askedgar.io/v1/historical-float-pro"
DEFAULT_TICKERS = ("AAPL", "GME", "AMC", "MULN")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit AskEdgar point-in-time historical float coverage without wiring it into MTS production Intake."
    )
    parser.add_argument("--tickers", nargs="*", default=None)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", default=None)
    return parser


def _api_key() -> str:
    value = os.getenv("ASKEDGAR_API_KEY", "").strip()
    if not value:
        raise RuntimeError("ASKEDGAR_API_KEY is required for the AskEdgar benchmark")
    return value


def _request(ticker: str, limit: int) -> dict[str, object]:
    query = urllib.parse.urlencode(
        {
            "ticker": ticker,
            "limit": limit,
            "page": 1,
            "is_adr": "false",
        }
    )
    request = urllib.request.Request(
        f"{ASKEDGAR_URL}?{query}",
        headers={
            "API-KEY": _api_key(),
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=60.0) as response:
        document = json.loads(response.read().decode("utf-8"))
    if not isinstance(document, dict):
        raise RuntimeError("AskEdgar response was not an object")
    return document


def _summary(ticker: str, limit: int) -> dict[str, object]:
    document = _request(ticker, limit)
    results = document.get("results")
    if not isinstance(results, list):
        raise RuntimeError("AskEdgar response did not contain a results list")

    rows = [row for row in results if isinstance(row, dict)]
    filed_dates = sorted(str(row.get("filed_at")) for row in rows if row.get("filed_at"))
    reported_dates = sorted(str(row.get("reported_date")) for row in rows if row.get("reported_date"))
    float_rows = [row for row in rows if row.get("float") is not None]
    tradable_rows = [row for row in rows if row.get("tradable_float") is not None]
    outstanding_rows = [row for row in rows if row.get("outstanding_shares") is not None]
    ciks = sorted({str(row.get("cik")) for row in rows if row.get("cik")})
    old_tickers = sorted({str(row.get("oldtickers")) for row in rows if row.get("oldtickers")})
    form_types = sorted({str(row.get("form_type")) for row in rows if row.get("form_type")})

    return {
        "ticker": ticker,
        "row_count": len(rows),
        "has_more": bool(document.get("has_more")),
        "page": document.get("page"),
        "limit": document.get("limit"),
        "filed_at_start": filed_dates[0] if filed_dates else None,
        "filed_at_end": filed_dates[-1] if filed_dates else None,
        "reported_date_start": reported_dates[0] if reported_dates else None,
        "reported_date_end": reported_dates[-1] if reported_dates else None,
        "float_share_observation_count": len(float_rows),
        "tradable_float_share_observation_count": len(tradable_rows),
        "outstanding_share_observation_count": len(outstanding_rows),
        "ciks": ciks,
        "old_tickers": old_tickers,
        "form_types": form_types,
        "sample": rows[:3],
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    tickers = tuple(t.upper() for t in (args.tickers or DEFAULT_TICKERS))
    results: list[dict[str, object]] = []
    for ticker in tickers:
        try:
            results.append(_summary(ticker, args.limit))
        except Exception as exc:
            results.append({"ticker": ticker, "error": f"{type(exc).__name__}: {exc}"})

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output = Path(args.output or f"/home/ubuntu/MTS_V4_ASKEDGAR_HISTORICAL_FLOAT_AUDIT_{stamp}.txt")
    document = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "provider_coverage_and_lineage_benchmark_only",
        "provider": "AskEdgar historical-float-pro",
        "production_intake_wired": False,
        "results": results,
    }
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OUTPUT={output}")
    for row in results:
        print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
