from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from MTS_V4.derived_market_store import ParquetDerivedMarketStore, UniverseDefinition
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource, maintain_standard_market_store
from MTS_V4.universe_membership import load_membership_csv


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a corrected derived-market generation in a NEW root; never mutate the published historical generation in place.")
    parser.add_argument("--new-derived-market-root", required=True)
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--universe-description", required=True)
    parser.add_argument("--membership-csv", required=True)
    parser.add_argument("--membership-source", required=True)
    parser.add_argument("--initial-start-date", required=True)
    parser.add_argument("--through-date", required=True)
    parser.add_argument("--rebuild-reason", required=True)
    args = parser.parse_args(argv)

    root = Path(args.new_derived_market_root)
    if root.exists() and any(root.iterdir()):
        raise RuntimeError("copy-on-write rebuild requires an empty/new derived-market root")
    membership = load_membership_csv(args.membership_csv, source_identity=args.membership_source)
    universe = UniverseDefinition(
        args.universe_id,
        args.universe_description,
        args.membership_source,
        True,
        attributes={"rebuild_reason": args.rebuild_reason, "copy_on_write_generation": True},
    )
    result = maintain_standard_market_store(
        store=ParquetDerivedMarketStore(root),
        universe=universe,
        membership=membership,
        source=YFinanceDailyMarketSource(),
        through_date=args.through_date,
        initial_start_date=args.initial_start_date,
        update_id_prefix="rebuild",
        publish_outcomes=True,
    )
    audit = {"policy": "COPY_ON_WRITE_NO_PUBLISHED_HISTORY_MUTATED", "rebuild_reason": args.rebuild_reason, "result": asdict(result)}
    (root / "REBUILD_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, sort_keys=True))
    print("PUBLISHED_POINTER_CHANGED=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
