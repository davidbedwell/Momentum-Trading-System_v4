from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from MTS_V4.prospective_validation import JsonProspectiveValidationStore
from MTS_V4.prospective_validation_runtime import (
    advance_matching_runtime,
    build_public_condition_feed,
    load_authoritative_sessions,
    save_public_condition_feed,
)
from MTS_V4.research_package_store import JsonResearchPackageStore


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Advance one frozen prospective validation using an authoritative "
            "Nasdaq-NOCP custodian snapshot. Raw prices remain outside the public "
            "matching feed."
        )
    )
    parser.add_argument("--validation-state", required=True)
    parser.add_argument("--research-package-dir", required=True)
    parser.add_argument("--rp-id", required=True)
    parser.add_argument("--authoritative-snapshot", required=True)
    parser.add_argument("--public-condition-feed", required=True)
    parser.add_argument(
        "--as-of-utc",
        default=None,
        help="ISO-8601 custody cutoff; defaults to current UTC time",
    )
    args = parser.parse_args()

    validation_store = JsonProspectiveValidationStore(args.validation_state)
    protocol, _ = validation_store.load()
    as_of = args.as_of_utc or datetime.now(timezone.utc).isoformat()
    sessions = load_authoritative_sessions(args.authoritative_snapshot)
    conditions = build_public_condition_feed(
        protocol=protocol,
        sessions=sessions,
        as_of_utc=as_of,
    )
    save_public_condition_feed(
        args.public_condition_feed,
        protocol=protocol,
        as_of_utc=as_of,
        conditions=conditions,
    )
    result = advance_matching_runtime(
        protocol_store=validation_store,
        research_package_store=JsonResearchPackageStore(args.research_package_dir),
        rp_id=args.rp_id,
        conditions=conditions,
    )

    print(f"PROTOCOL_ID={protocol.protocol_id}")
    print(f"PROTOCOL_FINGERPRINT={protocol.fingerprint}")
    print(f"AS_OF_UTC={as_of}")
    print(f"OFFICIAL_SESSIONS_RECEIVED={len(sessions)}")
    print(f"PUBLIC_CONDITIONS={len(conditions)}")
    print("RAW_PRICES_EXPOSED_TO_MATCHING=False")
    print("OUTCOMES_EXPOSED=False")
    print(f"NEW_TRIAL_LOCKS={len(result.newly_locked_trials)}")
    print("LOCKED_TRIAL_IDS=" + ",".join(result.newly_locked_trials))
    print(f"NEXT_TRIAL_ID={result.next_trial_id}")
    print(f"FRONTIER_STATE={result.frontier_state}")
    print(
        "GATE_CLOSED_THROUGH_SESSION_INDEX="
        + str(result.gate_closed_through_session_index)
    )
    print(f"PUBLIC_CONDITION_FEED={Path(args.public_condition_feed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
