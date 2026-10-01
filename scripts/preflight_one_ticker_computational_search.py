from __future__ import annotations

import argparse
from pathlib import Path

from MTS_V4.derived_market_store import ParquetDerivedMarketStore
from MTS_V4.universe_membership import load_membership_csv
from MTS_V4.universe_scientific_partition import ScientificCohort, load_frozen_partition


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description="Fail-closed preflight for one-ticker computational search.")
    p.add_argument("--ticker", required=True)
    p.add_argument("--derived-market-root", required=True)
    p.add_argument("--universe-id", required=True)
    p.add_argument("--membership-csv", required=True)
    p.add_argument("--scientific-partition-manifest", required=True)
    p.add_argument("--require-predictor-v2", action="store_true")
    args=p.parse_args(argv)

    for label,value in (
        ("DERIVED_MARKET_ROOT",args.derived_market_root),
        ("MEMBERSHIP_CSV",args.membership_csv),
        ("SCIENTIFIC_PARTITION_MANIFEST",args.scientific_partition_manifest),
    ):
        if not Path(value).exists():
            raise SystemExit(f"PREFLIGHT_FAIL={label}_MISSING PATH={value}")

    membership=load_membership_csv(args.membership_csv)
    ticker=args.ticker.upper().strip()
    security_ids={x.security_id for x in membership.intervals() if x.ticker.upper()==ticker}
    if len(security_ids)!=1:
        raise SystemExit(f"PREFLIGHT_FAIL=TICKER_IDENTITY_AMBIGUOUS TICKER={ticker} IDS={sorted(security_ids)}")
    security_id=next(iter(security_ids))

    partition=load_frozen_partition(args.scientific_partition_manifest)
    if partition.universe_id != args.universe_id:
        raise SystemExit(f"PREFLIGHT_FAIL=UNIVERSE_MISMATCH PARTITION={partition.universe_id} REQUESTED={args.universe_id}")
    matching_cohorts = tuple(
        cohort for cohort in ScientificCohort
        if security_id in partition.members(cohort)
    )
    if len(matching_cohorts) != 1:
        raise SystemExit(
            f"PREFLIGHT_FAIL=PARTITION_MEMBERSHIP_INVALID SECURITY_ID={security_id} "
            f"COHORTS={[cohort.value for cohort in matching_cohorts]}"
        )
    cohort = matching_cohorts[0]
    if cohort != ScientificCohort.DISCOVERY:
        raise SystemExit(f"PREFLIGHT_FAIL=ADAPTIVE_SEARCH_PROHIBITED COHORT={cohort.value}")

    store=ParquetDerivedMarketStore(args.derived_market_root)
    predictor_v1=store.get_feature_set("mts_market_predictors","v1")
    predictor_v2=store.get_feature_set("mts_market_predictors","v2")
    outcome_v1=store.get_feature_set("mts_historical_outcomes","v1")
    if outcome_v1 is None:
        raise SystemExit("PREFLIGHT_FAIL=OUTCOME_V1_MISSING")
    if args.require_predictor_v2 and predictor_v2 is None:
        raise SystemExit("PREFLIGHT_FAIL=PREDICTOR_V2_MISSING ACTION=BUILD_V2")
    print("PREFLIGHT_PASS=True")
    print(f"TICKER={ticker}")
    print(f"SECURITY_ID={security_id}")
    print(f"COHORT={cohort.value}")
    print(f"PARTITION_ID={partition.partition_id}")
    print(f"PREDICTOR_V1_PRESENT={predictor_v1 is not None}")
    print(f"PREDICTOR_V2_PRESENT={predictor_v2 is not None}")
    print(f"OUTCOME_V1_PRESENT={outcome_v1 is not None}")
    print("ADAPTIVE_SEARCH_AUTHORIZED=True")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
