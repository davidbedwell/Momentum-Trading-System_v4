from __future__ import annotations

import argparse

from MTS_V4.future_cohort_waiting import evaluate_waiting_manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Re-evaluate every ticker marked WAITING_FOR_FUTURE_COHORTS against its "
            "already-frozen prospective-validation protocol. Entries remain waiting "
            "until the protocol frontier resolves. No AI Research Director call is made."
        )
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument(
        "--as-of-utc",
        default=None,
        help="ISO-8601 daily evaluation cutoff; defaults to current UTC time",
    )
    args = parser.parse_args()

    result = evaluate_waiting_manifest(args.manifest, as_of_utc=args.as_of_utc)
    print(f"WAITING_ENTRIES_EVALUATED={result.evaluated}")
    print(f"WAITING_ENTRIES_REMAINING={result.still_waiting}")
    print(f"WAITING_ENTRIES_RESOLVED={result.resolved}")
    print(f"WAITING_OBJECTIVE_DEFECTS={result.objective_defects}")
    print(f"WAITING_MANIFEST={args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
