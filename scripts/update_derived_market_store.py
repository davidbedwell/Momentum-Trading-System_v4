from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import date
import json
from pathlib import Path

from MTS_V4.derived_market_store import ParquetDerivedMarketStore, UniverseDefinition
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource, maintain_standard_market_store
from MTS_V4.universe_membership import load_membership_csv


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Incrementally extend the Nexus-derived market store from explicit point-in-time membership and reacquirable daily market data."
    )
    parser.add_argument("--derived-market-root", required=True)
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--universe-description", required=True)
    parser.add_argument("--membership-csv", required=True)
    parser.add_argument("--membership-source", required=True)
    parser.add_argument("--through-date", default=date.today().isoformat())
    parser.add_argument("--initial-start-date", default=None)
    parser.add_argument("--update-id-prefix", default="weekly")
    parser.add_argument("--no-outcomes", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    membership = load_membership_csv(args.membership_csv, source_identity=args.membership_source)
    universe = UniverseDefinition(
        universe_id=args.universe_id,
        description=args.universe_description,
        membership_source=args.membership_source,
        point_in_time_membership_required=True,
    )
    store = ParquetDerivedMarketStore(Path(args.derived_market_root))
    if args.dry_run:
        existing = store.get_universe(args.universe_id)
        print("DRY_RUN=True")
        print(f"UNIVERSE_ID={args.universe_id}")
        print(f"MEMBERSHIP_INTERVALS={len(membership.intervals())}")
        print(f"EXISTING_UNIVERSE={existing is not None}")
        print("MARKET_DOWNLOADS=0")
        print("SOL_CALLS=0")
        return 0
    result = maintain_standard_market_store(
        store=store,
        universe=universe,
        membership=membership,
        source=YFinanceDailyMarketSource(),
        through_date=args.through_date,
        initial_start_date=args.initial_start_date,
        update_id_prefix=args.update_id_prefix,
        publish_outcomes=not args.no_outcomes,
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    print("SOL_CALLS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
