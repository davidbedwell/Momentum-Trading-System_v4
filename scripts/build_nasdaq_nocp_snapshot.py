from __future__ import annotations

import argparse
from pathlib import Path

from MTS_V4.nasdaq_nocp_adapter import (
    build_authoritative_snapshot,
    load_share_multipliers,
    save_snapshot,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build an authoritative Nasdaq NOCP/XNAS-session snapshot for one "
            "prospective validation subject."
        )
    )
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--source-subject-id", required=True)
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--output", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--share-multipliers-json",
        help=(
            "JSON object keyed by effective XNAS session date with exact mandatory "
            "share multipliers."
        ),
    )
    group.add_argument(
        "--confirm-no-mandatory-share-actions",
        action="store_true",
        help=(
            "Explicitly assert that no mandatory share-count transformation is "
            "effective inside the snapshot window."
        ),
    )
    args = parser.parse_args()

    multipliers = load_share_multipliers(args.share_multipliers_json)
    snapshot = build_authoritative_snapshot(
        ticker=args.ticker,
        source_subject_id=args.source_subject_id,
        start_date=args.start_date,
        end_date=args.end_date,
        share_multipliers=multipliers,
    )
    if args.confirm_no_mandatory_share_actions:
        snapshot["corporate_action_policy"] = {
            **dict(snapshot["corporate_action_policy"]),
            "assertion_basis": "CLI_CONFIRM_NO_MANDATORY_SHARE_ACTIONS",
        }
    else:
        snapshot["corporate_action_policy"] = {
            **dict(snapshot["corporate_action_policy"]),
            "assertion_basis": "EXPLICIT_MULTIPLIER_FILE",
        }
    save_snapshot(args.output, snapshot)

    sessions = snapshot["sessions"]
    with_prices = sum(1 for item in sessions if item["nocp"] is not None)
    without_prices = len(sessions) - with_prices
    print(f"TICKER={snapshot['ticker']}")
    print(f"SOURCE_SUBJECT_ID={snapshot['source_subject_id']}")
    print(f"SOURCE_IDENTITY={snapshot['source_identity']}")
    print(f"COVERAGE_START={snapshot['coverage_start']}")
    print(f"COVERAGE_END={snapshot['coverage_end']}")
    print(f"XNAS_SESSIONS={len(sessions)}")
    print(f"NOCP_ROWS_PRESENT={with_prices}")
    print(f"NOCP_ROWS_MISSING={without_prices}")
    print(f"OUTPUT={Path(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
