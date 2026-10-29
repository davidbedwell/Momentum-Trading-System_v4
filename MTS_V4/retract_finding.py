from __future__ import annotations

import argparse

from .nexus_json import JsonResearchNexus


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Quarantine explicitly identified Nexus findings from active research "
            "memory while preserving their original records and a durable audit trail."
        )
    )
    parser.add_argument("--nexus", required=True, help="Path to research_nexus.json")
    parser.add_argument(
        "--finding-id",
        action="append",
        required=True,
        dest="finding_ids",
        help="Finding ID to retract. Repeat for multiple findings.",
    )
    parser.add_argument("--reason", required=True, help="Explicit contamination/retraction reason")
    parser.add_argument("--initiated-by", required=True, help="Human or RD initiator identity")
    parser.add_argument(
        "--replacement-finding-id",
        default=None,
        help="Optional replacement finding ID when one already exists",
    )
    args = parser.parse_args()

    nexus = JsonResearchNexus(args.nexus)
    for finding_id in args.finding_ids:
        retraction = nexus.retract_finding(
            finding_id,
            reason=args.reason,
            initiated_by=args.initiated_by,
            replacement_finding_id=args.replacement_finding_id,
        )
        print(
            "RETRACTED_FINDING="
            f"{retraction.finding_id}|{retraction.retracted_at_utc}|{retraction.initiated_by}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
