from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date
from pathlib import Path


SOURCE_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SOURCE_KIND = "WIKIPEDIA_CURRENT_SP500_CONSTITUENTS_CALIBRATION_ONLY_NOT_AUTHORITATIVE_PIT"


def _ticker_for_yfinance(value: object) -> str:
    return str(value).strip().upper().replace(".", "-")


def _security_id_from_cik(value: object) -> str:
    raw = str(value).strip()
    if raw.endswith(".0"):
        raw = raw[:-2]
    if not raw.isdigit():
        raise ValueError(f"invalid CIK: {value!r}")
    return f"SEC_CIK_{int(raw):010d}"


def _effective_start(value: object, *, acquisition_floor: str) -> str:
    raw = str(value).strip()
    if not raw or raw.lower() in {"nan", "none", "nat"}:
        return acquisition_floor
    parsed = date.fromisoformat(raw[:10]).isoformat()
    return max(parsed, acquisition_floor)


def build_rows(records: list[dict[str, object]], *, acquisition_floor: str, source_identity: str) -> list[dict[str, str]]:
    rows = []
    for record in records:
        rows.append({
            "security_id": _security_id_from_cik(record["CIK"]),
            "ticker": _ticker_for_yfinance(record["Symbol"]),
            "start_date": _effective_start(record.get("Date added", ""), acquisition_floor=acquisition_floor),
            "end_date": "",
            "sector_id": str(record.get("GICS Sector", "")).strip(),
            "industry_id": str(record.get("GICS Sub-Industry", "")).strip(),
            "source_identity": source_identity,
        })
    rows.sort(key=lambda item: item["security_id"])
    security_ids = [item["security_id"] for item in rows]
    tickers = [item["ticker"] for item in rows]
    if len(security_ids) != len(set(security_ids)):
        raise ValueError("current constituent source contains duplicate CIK identities")
    if len(tickers) != len(set(tickers)):
        raise ValueError("current constituent source contains duplicate normalized tickers")
    if not 490 <= len(rows) <= 510:
        raise ValueError(f"unexpected current S&P constituent count: {len(rows)}")
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Freeze current S&P 500 membership for engineering/AI calibration only; never authoritative PIT science.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--as-of-date", default=date.today().isoformat())
    parser.add_argument("--acquisition-floor", required=True, help="earliest date needed for source lookback, YYYY-MM-DD")
    args = parser.parse_args(argv)
    date.fromisoformat(args.as_of_date)
    date.fromisoformat(args.acquisition_floor)

    import pandas as pd

    tables = pd.read_html(SOURCE_URL)
    required = {"Symbol", "GICS Sector", "GICS Sub-Industry", "Date added", "CIK"}
    candidates = [table for table in tables if required.issubset(set(str(column) for column in table.columns))]
    if len(candidates) != 1:
        raise RuntimeError(f"expected exactly one S&P constituent table; found {len(candidates)}")
    source_identity = f"{SOURCE_KIND}_AS_OF_{args.as_of_date}"
    records = candidates[0].to_dict(orient="records")
    rows = build_rows(records, acquisition_floor=args.acquisition_floor, source_identity=source_identity)

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise RuntimeError(f"refusing to replace frozen membership file: {output}")
    fieldnames = ["security_id", "ticker", "start_date", "end_date", "sector_id", "industry_id", "source_identity"]
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)

    payload = output.read_bytes()
    audit = {
        "format": "MTS_V4_CURRENT_SP500_CALIBRATION_MEMBERSHIP_AUDIT_V1",
        "source_url": SOURCE_URL,
        "source_identity": source_identity,
        "as_of_date": args.as_of_date,
        "acquisition_floor": args.acquisition_floor,
        "membership_intervals": len(rows),
        "unique_security_ids": len({item["security_id"] for item in rows}),
        "unique_tickers": len({item["ticker"] for item in rows}),
        "earliest_effective_start": min(item["start_date"] for item in rows),
        "latest_effective_start": max(item["start_date"] for item in rows),
        "membership_csv": str(output),
        "membership_csv_sha256": hashlib.sha256(payload).hexdigest(),
        "scientific_status": "ENGINEERING_AND_AI_CALIBRATION_ONLY_SURVIVORSHIP_BIASED_NOT_AUTHORITATIVE_PIT",
    }
    audit_path = output.with_suffix(".audit.json")
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, sort_keys=True))
    print("MARKET_DOWNLOADS=0")
    print("SOL_CALLS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
