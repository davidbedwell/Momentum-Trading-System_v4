from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

from MTS_V4.acceptance_control_store import (
    NEGATIVE_CONTROL_FEATURE_SET_ID,
    NEGATIVE_CONTROL_FEATURE_SET_VERSION,
    build_negative_control_rows,
    negative_control_feature_set,
)
from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build/update the isolated identity/date-hash negative-control feature set from an existing derived-store row identity surface. No market values are copied into the control set.")
    parser.add_argument("--derived-market-root", required=True)
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--source-feature-set-id", required=True)
    parser.add_argument("--source-feature-set-version", required=True)
    parser.add_argument("--through-date", default=None)
    parser.add_argument("--update-id", required=True)
    args = parser.parse_args(argv)

    store = ParquetDerivedMarketStore(Path(args.derived_market_root))
    if store.get_universe(args.universe_id) is None:
        raise RuntimeError(f"unknown universe: {args.universe_id}")
    if store.get_feature_set(args.source_feature_set_id, args.source_feature_set_version) is None:
        raise RuntimeError("unknown source feature set")
    definition = negative_control_feature_set()
    store.register_feature_set(definition)
    state = store.state(args.universe_id, NEGATIVE_CONTROL_FEATURE_SET_ID, NEGATIVE_CONTROL_FEATURE_SET_VERSION)
    start_date = None
    if state.high_water_mark:
        start_date = (date.fromisoformat(state.high_water_mark) + timedelta(days=1)).isoformat()
    source_rows = store.query(
        DerivedMarketQuery(
            universe_id=args.universe_id,
            feature_set_id=args.source_feature_set_id,
            feature_set_version=args.source_feature_set_version,
            start_date=start_date,
            end_date=args.through_date,
        )
    )
    if not source_rows:
        print("ROWS_APPENDED=0")
        print(f"HIGH_WATER_MARK={state.high_water_mark}")
        return 0
    rows = build_negative_control_rows(source_rows)
    record = store.append_update(
        universe_id=args.universe_id,
        feature_set_id=NEGATIVE_CONTROL_FEATURE_SET_ID,
        feature_set_version=NEGATIVE_CONTROL_FEATURE_SET_VERSION,
        update_id=args.update_id,
        rows=rows,
        source_lineage={
            "identity_source_feature_set": f"{args.source_feature_set_id}:{args.source_feature_set_version}",
            "market_values_copied": False,
            "construction": "SHA256_SECURITY_ID_EFFECTIVE_DATE",
        },
    )
    print(f"ROWS_APPENDED={record.row_count}")
    print(f"HIGH_WATER_MARK={record.last_effective_date}")
    print("MARKET_VALUES_COPIED=False")
    print("SOL_CALLS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
