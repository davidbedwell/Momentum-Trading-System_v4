from __future__ import annotations

import argparse
import json
from pathlib import Path

from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore
from MTS_V4.universe_scientific_partition import ScientificCohort, create_frozen_partition, write_frozen_partition


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Freeze an exact deterministic discovery/verification partition from a populated derived universe.")
    parser.add_argument("--derived-market-root", required=True)
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--feature-set-id", required=True)
    parser.add_argument("--feature-set-version", required=True)
    parser.add_argument("--discovery-count", type=int, required=True)
    parser.add_argument("--verification-a-count", type=int, required=True)
    parser.add_argument("--verification-b-count", type=int, required=True)
    parser.add_argument("--salt", required=True)
    parser.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    store = ParquetDerivedMarketStore(Path(args.derived_market_root).expanduser().resolve())
    rows = store.query(DerivedMarketQuery(
        universe_id=args.universe_id,
        feature_set_id=args.feature_set_id,
        feature_set_version=args.feature_set_version,
    ))
    security_ids = sorted({str(row["security_id"]) for row in rows})
    partition = create_frozen_partition(
        universe_id=args.universe_id,
        security_ids=security_ids,
        cohort_sizes={
            ScientificCohort.DISCOVERY: args.discovery_count,
            ScientificCohort.VERIFICATION_A: args.verification_a_count,
            ScientificCohort.VERIFICATION_B: args.verification_b_count,
        },
        salt=args.salt,
    )
    write_frozen_partition(args.output, partition)
    print(json.dumps({
        "PARTITION_ID": partition.partition_id,
        "UNIVERSE_ID": partition.universe_id,
        "DISCOVERY": len(partition.members(ScientificCohort.DISCOVERY)),
        "VERIFICATION_A": len(partition.members(ScientificCohort.VERIFICATION_A)),
        "VERIFICATION_B": len(partition.members(ScientificCohort.VERIFICATION_B)),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
