from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import secrets

from MTS_V4.universe_membership import load_membership_csv
from MTS_V4.universe_scientific_partition import (
    ScientificCohort,
    load_frozen_partition,
    repair_partition_prior_exposure,
    write_frozen_partition,
)


SIZE_BANDS = (
    "LOWER_CURRENT_MARKET_CAP_TERCILE",
    "MIDDLE_CURRENT_MARKET_CAP_TERCILE",
    "UPPER_CURRENT_MARKET_CAP_TERCILE",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Supersede a partition by swapping prior-Sol-exposed reserved members in kind."
    )
    parser.add_argument("--partition", required=True)
    parser.add_argument("--membership-csv", required=True)
    parser.add_argument("--market-cap-csv", required=True)
    parser.add_argument("--prior-exposed-ticker", action="append", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit-output", required=True)
    args = parser.parse_args(argv)
    output = Path(args.output).expanduser().resolve()
    audit_output = Path(args.audit_output).expanduser().resolve()
    if output.exists() or audit_output.exists():
        raise RuntimeError("refusing to replace a partition or supersession audit")

    partition_path = Path(args.partition).expanduser().resolve()
    membership_path = Path(args.membership_csv).expanduser().resolve()
    market_cap_path = Path(args.market_cap_csv).expanduser().resolve()
    partition = load_frozen_partition(partition_path)
    intervals = load_membership_csv(membership_path).intervals()
    by_security = {interval.security_id: interval for interval in intervals}
    if set(by_security) != set(partition.all_security_ids):
        raise RuntimeError("membership evidence does not exactly cover the partition")
    by_ticker = {interval.ticker.upper(): interval.security_id for interval in intervals}
    requested_tickers = tuple(sorted({ticker.strip().upper() for ticker in args.prior_exposed_ticker}))
    missing_tickers = sorted(set(requested_tickers).difference(by_ticker))
    if missing_tickers:
        raise RuntimeError(f"prior-exposed tickers are absent from membership evidence: {missing_tickers}")

    with market_cap_path.open("r", encoding="utf-8", newline="") as handle:
        cap_rows = tuple(csv.DictReader(handle))
    market_caps = {str(row["security_id"]): float(row["market_cap"]) for row in cap_rows}
    if set(market_caps) != set(partition.all_security_ids) or any(value <= 0 for value in market_caps.values()):
        raise RuntimeError("market-cap evidence must positively cover every partition identity")
    ordered = sorted(market_caps, key=lambda item: (market_caps[item], item))
    size_band = {
        security_id: SIZE_BANDS[min(2, index * 3 // len(ordered))]
        for index, security_id in enumerate(ordered)
    }
    strata = {
        security_id: (str(by_security[security_id].sector_id or "UNCLASSIFIED"), size_band[security_id])
        for security_id in partition.all_security_ids
    }
    exposed_ids = tuple(by_ticker[ticker] for ticker in requested_tickers)
    repaired, repair_audit = repair_partition_prior_exposure(
        partition=partition,
        strata=strata,
        prior_exposed_security_ids=exposed_ids,
        salt=secrets.token_hex(32),
    )
    write_frozen_partition(output, repaired)
    audit = {
        "format": "MTS_V4_UNIVERSE_PARTITION_PRIOR_SOL_EXPOSURE_REPAIR_V1",
        "status": "SUPERSEDED_BEFORE_UNIVERSE_OUTCOME_EXPOSURE",
        "old_partition": str(partition_path),
        "old_partition_id": partition.partition_id,
        "new_partition": str(output),
        "new_partition_id": repaired.partition_id,
        "prior_exposed_tickers": list(requested_tickers),
        "prior_exposed_security_ids": list(exposed_ids),
        "repair": repair_audit,
        "evidence": {
            "membership_csv_sha256": hashlib.sha256(membership_path.read_bytes()).hexdigest(),
            "market_cap_csv_sha256": hashlib.sha256(market_cap_path.read_bytes()).hexdigest(),
        },
        "cohort_sizes": {
            cohort.value: len(repaired.members(cohort)) for cohort in ScientificCohort
        },
        "sol_calls": 0,
    }
    audit_output.parent.mkdir(parents=True, exist_ok=True)
    temporary = audit_output.with_suffix(audit_output.suffix + ".tmp")
    temporary.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(audit_output)
    print(json.dumps({
        "OLD_PARTITION_ID": partition.partition_id,
        "NEW_PARTITION_ID": repaired.partition_id,
        "PRIOR_EXPOSED_TICKERS": list(requested_tickers),
        "SWAPS": repair_audit["swap_count"],
        "DISCOVERY": len(repaired.members(ScientificCohort.DISCOVERY)),
        "VERIFICATION_A": len(repaired.members(ScientificCohort.VERIFICATION_A)),
        "VERIFICATION_B": len(repaired.members(ScientificCohort.VERIFICATION_B)),
        "AUDIT": str(audit_output),
        "SOL_CALLS": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
