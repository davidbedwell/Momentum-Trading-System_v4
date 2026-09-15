#!/usr/bin/env python3
"""PIPELINE_TEST_NONSCIENTIFIC engineering harness.

Runs recovered CSV histories through production deterministic feature/Analysis
math while keeping all test persistence outside canonical Nexus.  This is an
engineering market-perception test only: no Sol/Qwen, no promotion, no
scientific validation/generalization credit.
"""
from __future__ import annotations

import argparse
import csv
import gc
import json
import os
import re
import resource
import shutil
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from MTS_V4.cross_sectional_analysis import cross_sectional_rank
from MTS_V4.derived_feature_factory import build_matured_outcome_rows, build_predictor_rows

MODE = "PIPELINE_TEST_NONSCIENTIFIC"
DEFAULT_SOURCE = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/David/Trading/Momentum-Trading-System-History/01_Raw"
CANONICAL_TOKENS = ("nexus", "derived_market_store")


def rss_mb() -> float:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value / (1024.0 * 1024.0) if sys.platform == "darwin" else value / 1024.0


def ticker_from_path(path: Path) -> str:
    match = re.search(r"BATS_([^,]+)", path.name)
    return (match.group(1) if match else path.stem).strip().upper()


def normalized_rows(path: Path):
    ticker = ticker_from_path(path)
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"time", "open", "high", "low", "close", "ICS Dollar Volume"}
        missing = required.difference(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
        for row in reader:
            close = float(row["close"])
            dollar_volume = float(row["ICS Dollar Volume"])
            stamp = datetime.fromtimestamp(int(float(row["time"])), tz=timezone.utc)
            yield {
                "security_id": f"TEST:{ticker}",
                "ticker": ticker,
                "date": stamp.date().isoformat(),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": close,
                "volume": (dollar_volume / close) if close else 0.0,
                "eligible": True,
                "sector_id": "TEST_UNVERIFIED",
                "industry_id": "TEST_UNVERIFIED",
            }


def write_rows(path: Path, rows) -> int:
    rows = list(rows)
    if not rows:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")
    return len(rows)


def read_parquets(paths):
    for path in paths:
        table = pq.read_table(path)
        for batch in table.to_batches(max_chunksize=2048):
            yield from batch.to_pylist()
        del table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--ticker-limit", type=int, default=0)
    parser.add_argument("--security-batch-size", type=int, default=3)
    parser.add_argument("--date-batch-size", type=int, default=20)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    out = args.output_root.expanduser().resolve()
    if MODE.lower() not in str(out).lower():
        raise SystemExit(f"FAIL_CLOSED: output-root must contain {MODE}")
    # Test root must never resolve inside the repository's canonical data roots.
    repo = Path(__file__).resolve().parents[1]
    if out == repo or repo in out.parents:
        raise SystemExit("FAIL_CLOSED: test persistence must be outside repository/canonical Nexus")
    if args.reset and out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "MODE.txt").write_text(
        f"{MODE}\nNO_SOL\nNO_QWEN\nNO_CANONICAL_NEXUS\nNO_PROMOTION\nENGINEERING_ONLY\n",
        encoding="utf-8",
    )

    files = sorted(args.source_dir.expanduser().glob("*.csv"))
    # Exact duplicate ticker exports are deliberately reduced to one input for this machinery test.
    unique = {}
    for path in files:
        unique.setdefault(ticker_from_path(path), path)
    files = list(unique.values())
    if args.ticker_limit > 0:
        files = files[: args.ticker_limit]
    if not files:
        raise SystemExit(f"No CSV files found under {args.source_dir}")

    manifest_path = out / "checkpoint.json"
    checkpoint = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"completed_tickers": []}
    completed = set(checkpoint.get("completed_tickers", []))
    predictor_dir = out / "predictor_security_partitions"
    outcome_dir = out / "outcome_security_partitions"

    print(f"MODE={MODE}", flush=True)
    print("SOL_CALLS=0 QWEN_CALLS=0 CANONICAL_NEXUS_WRITES=0", flush=True)
    print(f"INPUT_SECURITIES={len(files)} SECURITY_BATCH_SIZE={args.security_batch_size}", flush=True)

    # Security-history batches: production feature math, immediately persisted per security.
    for start in range(0, len(files), max(1, args.security_batch_size)):
        batch = files[start : start + max(1, args.security_batch_size)]
        for source in batch:
            ticker = ticker_from_path(source)
            if ticker in completed:
                continue
            raw = list(normalized_rows(source))
            predictors = build_predictor_rows(raw)
            outcomes = build_matured_outcome_rows(raw)
            write_rows(predictor_dir / f"{ticker}.parquet", predictors)
            write_rows(outcome_dir / f"{ticker}.parquet", outcomes)
            completed.add(ticker)
            checkpoint.update({"mode": MODE, "completed_tickers": sorted(completed), "last_ticker": ticker, "rss_peak_mb": rss_mb()})
            manifest_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True), encoding="utf-8")
            del raw, predictors, outcomes
            gc.collect()
            print(f"SECURITY_COMPLETE={ticker} COUNT={len(completed)}/{len(files)} RSS_PEAK_MB={rss_mb():.1f}", flush=True)

    # Cross-section pass. Read persisted per-security results, partition by bounded date windows,
    # and invoke production deterministic Analysis rank math on each market-date slice.
    predictor_paths = sorted(predictor_dir.glob("*.parquet"))
    date_index = defaultdict(list)
    for path in predictor_paths:
        table = pq.read_table(path, columns=["effective_date"])
        dates = table.column("effective_date").to_pylist()
        for date in dates:
            date_index[str(date)].append(path)
        del table, dates
        gc.collect()
    dates = sorted(date_index)
    market_dir = out / "market_cross_sections"
    market_dir.mkdir(exist_ok=True)
    profile_rows = []
    for date_start in range(0, len(dates), max(1, args.date_batch_size)):
        date_chunk = dates[date_start : date_start + max(1, args.date_batch_size)]
        for date in date_chunk:
            rows = []
            for path in date_index[date]:
                table = pq.read_table(path)
                # One matching row per security/date; filter without retaining whole history.
                for row in table.to_pylist():
                    if str(row.get("effective_date")) == date:
                        rows.append(row)
                        break
                del table
            if not rows:
                continue
            ranked = cross_sectional_rank(
                {"test_market": rows},
                {"value_column": "return_20__v1", "output_column": "test_return_20_percentile", "group_by": ["effective_date"], "ascending": True},
            )
            ranked_rows = ranked["derived_datasets"]["cross_sectional_ranked_dataset"]
            write_rows(market_dir / f"market_{date}.parquet", ranked_rows)
            usable = [r for r in ranked_rows if r.get("return_20__v1") is not None]
            profile_rows.append({"effective_date": date, "security_count": len(rows), "ranked_return20_count": len(usable)})
            del rows, ranked, ranked_rows, usable
            gc.collect()
        print(f"MARKET_DATES_COMPLETE={min(date_start + len(date_chunk), len(dates))}/{len(dates)} RSS_PEAK_MB={rss_mb():.1f}", flush=True)

    write_rows(out / "market_profile_index.parquet", profile_rows)
    report = {
        "mode": MODE,
        "scientific_status": "NONSCIENTIFIC_ENGINEERING_TEST",
        "sol_calls": 0,
        "qwen_calls": 0,
        "canonical_nexus_writes": 0,
        "security_count": len(files),
        "market_date_count": len(dates),
        "rss_peak_mb": rss_mb(),
        "limitations": [
            "Recovered selected TradingView exports; not a historical point-in-time market universe.",
            "Survivorship, selection, source, and adjustment semantics are unverified.",
            "Outputs demonstrate engineering behavior only; no predictive/scientific validity or generalization credit.",
        ],
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out / "FINAL_ENGINEERING_REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("PIPELINE_TEST_COMPLETE", flush=True)
    print(json.dumps(report, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
