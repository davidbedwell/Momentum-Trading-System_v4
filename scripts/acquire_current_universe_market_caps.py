from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.intake import IntakeEngine
from MTS_V4.research_scope import universe_scope
from MTS_V4.universe_membership import load_membership_csv
from MTS_V4.universe_sources import CurrentUniverseMarketCapSource


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Acquire and freeze current market caps through Intake for cohort stratification."
    )
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--membership-csv", required=True)
    parser.add_argument("--as-of-date", required=True)
    parser.add_argument("--download-workers", type=int, default=6)
    parser.add_argument("--download-attempts", type=int, default=4)
    parser.add_argument("--acquisition-cache-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    output = Path(args.output).expanduser().resolve()
    if output.exists() or output.with_suffix(".audit.json").exists():
        raise RuntimeError(f"refusing to replace frozen current market-cap evidence: {output}")

    membership = load_membership_csv(args.membership_csv)
    members = tuple(
        {"security_id": interval.security_id, "ticker": interval.ticker}
        for interval in membership.intervals()
    )
    subject = universe_scope(args.universe_id).to_subject_metadata(
        display_ticker=args.universe_id.upper()
    )
    cache = TemporaryResearchCache()
    descriptors = IntakeEngine(cache).ingest(
        subject=subject,
        source=CurrentUniverseMarketCapSource(
            members=members,
            as_of_date=args.as_of_date,
            download_workers=args.download_workers,
            download_attempts=args.download_attempts,
            acquisition_cache_root=args.acquisition_cache_root,
        ),
    )
    if len(descriptors) != 1:
        raise RuntimeError("expected exactly one current market-cap evidence artifact")
    descriptor = descriptors[0]
    rows = cache.get(descriptor.cache_key)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=("security_id", "ticker", "as_of_date", "market_cap")
        )
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    audit = {
        "format": "MTS_V4_CURRENT_MARKET_CAP_GOVERNANCE_INTAKE_V1",
        "universe_id": args.universe_id,
        "membership_csv": str(Path(args.membership_csv).expanduser().resolve()),
        "market_cap_csv": str(output),
        "market_cap_csv_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "evidence": asdict(descriptor.durable_metadata()),
        "row_count": len(rows),
        "minimum_market_cap": min(float(row["market_cap"]) for row in rows),
        "maximum_market_cap": max(float(row["market_cap"]) for row in rows),
        "sol_calls": 0,
    }
    output.with_suffix(".audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit, indent=2, sort_keys=True))
    print("INTAKE_ENGINE_USED=True")
    print("MARKET_CAP_USE=GOVERNANCE_STRATIFICATION_ONLY")
    print("SOL_CALLS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
