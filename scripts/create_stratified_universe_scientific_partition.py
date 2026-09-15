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
    create_stratified_frozen_partition,
    write_frozen_partition,
)


SIZE_BANDS = (
    "LOWER_CURRENT_MARKET_CAP_TERCILE",
    "MIDDLE_CURRENT_MARKET_CAP_TERCILE",
    "UPPER_CURRENT_MARKET_CAP_TERCILE",
)


def _read_market_caps(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    output: dict[str, float] = {}
    for row in rows:
        security_id = str(row.get("security_id", "")).strip()
        market_cap = float(row.get("market_cap", ""))
        if not security_id or market_cap <= 0 or security_id in output:
            raise RuntimeError("market-cap CSV must contain unique IDs and positive market caps")
        output[security_id] = market_cap
    return output


def _marginal(partition, labels: dict[str, str]) -> dict[str, dict[str, int]]:
    values = sorted(set(labels.values()))
    return {
        value: {
            cohort.value: sum(
                labels[security_id] == value
                for security_id in partition.members(cohort)
            )
            for cohort in ScientificCohort
        }
        for value in values
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Freeze an exact sector/current-market-cap stratified scientific partition."
    )
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--membership-csv", required=True)
    parser.add_argument("--market-cap-csv", required=True)
    parser.add_argument("--discovery-count", type=int, required=True)
    parser.add_argument("--verification-a-count", type=int, required=True)
    parser.add_argument("--verification-b-count", type=int, required=True)
    salt = parser.add_mutually_exclusive_group(required=True)
    salt.add_argument("--salt")
    salt.add_argument("--generate-random-salt", action="store_true")
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit-output", required=True)
    args = parser.parse_args(argv)
    output = Path(args.output).expanduser().resolve()
    audit_output = Path(args.audit_output).expanduser().resolve()
    if output.exists() or audit_output.exists():
        raise RuntimeError("refusing to replace an existing frozen partition or balance audit")

    membership_path = Path(args.membership_csv).expanduser().resolve()
    market_cap_path = Path(args.market_cap_csv).expanduser().resolve()
    membership = load_membership_csv(membership_path)
    intervals = membership.intervals()
    by_security = {interval.security_id: interval for interval in intervals}
    if len(by_security) != len(intervals):
        raise RuntimeError("stratified current-universe partition requires one interval per security")
    market_caps = _read_market_caps(market_cap_path)
    if set(by_security) != set(market_caps):
        raise RuntimeError("membership and market-cap evidence must cover identical security IDs")

    ordered_caps = sorted(market_caps, key=lambda item: (market_caps[item], item))
    size_band: dict[str, str] = {}
    total = len(ordered_caps)
    for index, security_id in enumerate(ordered_caps):
        band_index = min(2, index * 3 // total)
        size_band[security_id] = SIZE_BANDS[band_index]
    sectors = {
        security_id: str(interval.sector_id or "UNCLASSIFIED")
        for security_id, interval in by_security.items()
    }
    strata = {
        security_id: (sectors[security_id], size_band[security_id])
        for security_id in by_security
    }
    raw_salt = secrets.token_hex(32) if args.generate_random_salt else str(args.salt)
    partition, allocation_audit = create_stratified_frozen_partition(
        universe_id=args.universe_id,
        security_ids=tuple(sorted(by_security)),
        cohort_sizes={
            ScientificCohort.DISCOVERY: args.discovery_count,
            ScientificCohort.VERIFICATION_A: args.verification_a_count,
            ScientificCohort.VERIFICATION_B: args.verification_b_count,
        },
        strata=strata,
        salt=raw_salt,
    )
    write_frozen_partition(output, partition)
    audit = {
        "format": "MTS_V4_STRATIFIED_UNIVERSE_PARTITION_BALANCE_AUDIT_V1",
        "partition_id": partition.partition_id,
        "universe_id": partition.universe_id,
        "cohort_sizes": {
            cohort.value: len(partition.members(cohort)) for cohort in ScientificCohort
        },
        "stratification": {
            "dimensions": ["CURRENT_GICS_SECTOR", "RELATIVE_CURRENT_MARKET_CAP_TERCILE"],
            "market_cap_is_historical_pit": False,
            "market_cap_is_scientific_predictor": False,
            "assignment_uses_outcomes": False,
            "allocation": allocation_audit,
        },
        "sector_balance": _marginal(partition, sectors),
        "current_market_cap_tercile_balance": _marginal(partition, size_band),
        "evidence": {
            "membership_csv": str(membership_path),
            "membership_csv_sha256": hashlib.sha256(membership_path.read_bytes()).hexdigest(),
            "market_cap_csv": str(market_cap_path),
            "market_cap_csv_sha256": hashlib.sha256(market_cap_path.read_bytes()).hexdigest(),
        },
        "sol_calls": 0,
    }
    audit_output.parent.mkdir(parents=True, exist_ok=True)
    temporary = audit_output.with_suffix(audit_output.suffix + ".tmp")
    temporary.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(audit_output)
    print(json.dumps({
        "PARTITION_ID": partition.partition_id,
        "DISCOVERY": len(partition.members(ScientificCohort.DISCOVERY)),
        "VERIFICATION_A": len(partition.members(ScientificCohort.VERIFICATION_A)),
        "VERIFICATION_B": len(partition.members(ScientificCohort.VERIFICATION_B)),
        "STRATA": allocation_audit["stratum_count"],
        "PARTITION": str(output),
        "BALANCE_AUDIT": str(audit_output),
        "SOL_CALLS": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
