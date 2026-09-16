from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import time
from zoneinfo import ZoneInfo

import pyarrow.dataset as ds

from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.contracts import SubjectMetadata
from MTS_V4.derived_market_store import ParquetDerivedMarketStore
from MTS_V4.earnings_event_features import (
    EARNINGS_FEATURE_SET_ID,
    EARNINGS_FEATURE_SET_VERSION,
    build_earnings_event_rows,
    earnings_event_feature_set,
)
from MTS_V4.eodhd_earnings_source import EODHDEarningsCalendarSource
from MTS_V4.intake import IntakeEngine
from MTS_V4.universe_membership import load_membership_csv


NY = ZoneInfo("America/New_York")
KNOWN_TIMINGS = {"BeforeMarket", "AfterMarket"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Acquire EODHD earnings through Intake, audit coverage, and optionally publish an event-context stream.")
    parser.add_argument("--derived-market-root", required=True)
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--membership-csv", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--through-date", default=date.today().isoformat())
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--attempts", type=int, default=4)
    parser.add_argument("--cache-root", default=None)
    parser.add_argument("--audit-output", required=True)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--update-id", default=None)
    parser.add_argument("--minimum-security-coverage", type=float, default=0.95)
    parser.add_argument("--minimum-known-timing-rate", type=float, default=0.98)
    return parser


def _cache_path(root: Path, security_id: str, ticker: str) -> Path:
    digest = hashlib.sha256(f"{security_id}|{ticker}".encode()).hexdigest()[:24]
    return root / f"{digest}.json.gz"


def _acquire_one(*, interval, token: str, start: str, end: str, cache_root: Path, attempts: int):
    target = _cache_path(cache_root, interval.security_id, interval.ticker)
    if target.exists():
        with gzip.open(target, "rt", encoding="utf-8") as handle:
            document = json.load(handle)
        return document, True
    subject = SubjectMetadata(
        subject_id=f"equity:{interval.ticker}", ticker=interval.ticker,
        attributes={"security_id": interval.security_id},
    )
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            cache = TemporaryResearchCache()
            descriptor = IntakeEngine(cache).ingest(
                subject=subject,
                source=EODHDEarningsCalendarSource(token, start, end),
            )[0]
            document = {
                "ticker": interval.ticker,
                "security_id": interval.security_id,
                "descriptor": {
                    "evidence_id": descriptor.evidence_id,
                    "content_identity": descriptor.content_identity,
                    "coverage_start": descriptor.coverage_start,
                    "coverage_end": descriptor.coverage_end,
                    "row_count": descriptor.row_count,
                    "source_identity": descriptor.source_identity,
                    "provenance": dict(descriptor.provenance),
                },
                "rows": cache.get(descriptor.cache_key),
            }
            temporary = target.with_suffix(".json.gz.tmp")
            with gzip.open(temporary, "wt", encoding="utf-8") as handle:
                json.dump(document, handle, sort_keys=True, separators=(",", ":"))
            temporary.replace(target)
            return document, False
        except Exception as exc:  # bounded retry is intentionally provider-agnostic
            last_error = exc
            if attempt < attempts:
                print(f"EARNINGS_ACQUISITION_RETRY TICKER={interval.ticker} ATTEMPT={attempt + 1}/{attempts} ERROR={type(exc).__name__}", flush=True)
                time.sleep(min(2 ** (attempt - 1), 8))
    raise RuntimeError(f"earnings acquisition failed after {attempts} attempts for {interval.ticker}") from last_error


def _market_closes(root: Path, universe_id: str) -> dict[str, tuple[datetime, ...]]:
    manifest = json.loads((root / "manifest.json").read_text())
    key = f"{universe_id}|mts_market_predictors:v1"
    stream = manifest.get("streams", {}).get(key)
    if not stream:
        raise RuntimeError(f"predictor stream is absent: {key}")
    files = [str(root / item["file_name"]) for item in stream["updates"]]
    table = ds.dataset(files, format="parquet").to_table(columns=["security_id", "effective_date", "eligible"])
    closes: dict[str, list[datetime]] = {}
    for row in table.to_pylist():
        if row["eligible"]:
            day = date.fromisoformat(row["effective_date"])
            closes.setdefault(row["security_id"], []).append(datetime(day.year, day.month, day.day, 16, tzinfo=NY))
    return {security_id: tuple(sorted(set(values))) for security_id, values in closes.items()}


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.workers < 1 or args.attempts < 1:
        raise RuntimeError("--workers and --attempts must be >= 1")
    token = os.environ.get("EODHD_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("required environment variable is not set: EODHD_API_TOKEN")
    root = Path(args.derived_market_root)
    cache_root = Path(args.cache_root or root / ".temporary-earnings-acquisition-cache")
    cache_root.mkdir(parents=True, exist_ok=True)
    intervals = load_membership_csv(args.membership_csv).intervals()
    if len({item.security_id for item in intervals}) != len(intervals):
        raise RuntimeError("earnings updater requires one current calibration interval per security")

    documents = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = {
            executor.submit(_acquire_one, interval=item, token=token, start=args.start_date, end=args.through_date, cache_root=cache_root, attempts=args.attempts): item
            for item in intervals
        }
        for completed, future in enumerate(as_completed(pending), start=1):
            item = pending[future]
            document, cache_hit = future.result()
            documents.append(document)
            print(f"EARNINGS_ACQUISITION_{'CACHE_HIT' if cache_hit else 'COMPLETED'}={completed}/{len(intervals)} TICKER={item.ticker} ROWS={len(document['rows'])}", flush=True)

    all_rows = [row for document in documents for row in document["rows"]]
    timing_counts = Counter(row.get("availability_class") or "UNKNOWN" for row in all_rows)
    securities_with_records = {row["security_id"] for row in all_rows}
    known_rows = [row for row in all_rows if row.get("availability_class") in KNOWN_TIMINGS]
    missing_estimate = sum(row.get("eps_estimate") is None for row in all_rows)
    missing_surprise = sum(row.get("surprise_pct") is None for row in all_rows)
    security_coverage = len(securities_with_records) / len(intervals)
    known_timing_rate = len(known_rows) / len(all_rows) if all_rows else 0.0
    coverage_pass = security_coverage >= args.minimum_security_coverage
    timing_pass = known_timing_rate >= args.minimum_known_timing_rate
    audit = {
        "format": "MTS_V4_EODHD_EARNINGS_UNIVERSE_AUDIT_V1",
        "universe_id": args.universe_id,
        "requested_start": args.start_date,
        "requested_end": args.through_date,
        "security_count": len(intervals),
        "securities_with_reported_records": len(securities_with_records),
        "security_coverage_rate": security_coverage,
        "total_reported_records": len(all_rows),
        "known_timing_records": len(known_rows),
        "known_timing_rate": known_timing_rate,
        "timing_counts": dict(sorted(timing_counts.items())),
        "missing_estimate_records": missing_estimate,
        "missing_surprise_records": missing_surprise,
        "securities_without_records": sorted(item.ticker for item in intervals if item.security_id not in securities_with_records),
        "thresholds": {"minimum_security_coverage": args.minimum_security_coverage, "minimum_known_timing_rate": args.minimum_known_timing_rate},
        "checks": {"security_coverage": coverage_pass, "known_timing_rate": timing_pass},
        "passed": coverage_pass and timing_pass,
        "unknown_timing_policy": "EXCLUDED_FROM_DERIVED_PREDICTORS_NOT_GUESSED",
        "token_persisted": False,
        "sol_calls": 0,
    }
    audit_path = Path(args.audit_output)
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps(audit, indent=2, sort_keys=True))
    print(f"EARNINGS_AUDIT_OUTPUT={audit_path}")
    if not args.publish:
        print("EARNINGS_PUBLISHED=False")
        print("SOL_CALLS=0")
        return 0 if audit["passed"] else 1
    if not audit["passed"]:
        raise RuntimeError("refusing earnings publication because coverage audit failed")

    closes = _market_closes(root, args.universe_id)
    derived_rows = build_earnings_event_rows(known_rows, market_close_times_by_security=closes)
    if not derived_rows:
        raise RuntimeError("no earnings event rows align to observed predictor sessions")
    update_id = args.update_id or f"eodhd-earnings-{min(row['effective_date'] for row in derived_rows)}-{max(row['effective_date'] for row in derived_rows)}"
    store = ParquetDerivedMarketStore(root)
    lock_path = root / ".maintenance.lock"
    with lock_path.open("a+") as lock_handle:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"another derived-market writer holds {lock_path}") from exc
        store.register_feature_set(earnings_event_feature_set())
        record = store.append_update(
            universe_id=args.universe_id,
            feature_set_id=EARNINGS_FEATURE_SET_ID,
            feature_set_version=EARNINGS_FEATURE_SET_VERSION,
            update_id=update_id,
            rows=derived_rows,
            source_lineage={
                "provider": "EODHD", "endpoint": "/api/calendar/earnings",
                "audit": str(audit_path), "reported_records": len(all_rows),
                "published_records": len(derived_rows), "unknown_timing_records_excluded": len(all_rows) - len(known_rows),
                "token_persisted": False,
            },
        )
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
    print(f"EARNINGS_PUBLISHED=True")
    print(f"EARNINGS_UPDATE_ID={record.update_id}")
    print(f"EARNINGS_ROWS={record.row_count}")
    print("SOL_CALLS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
