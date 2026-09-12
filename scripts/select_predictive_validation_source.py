from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector
from MTS_V4.validation_source_selection import select_validation_source


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Use one Sol scientific-reasoning call to choose the blind-validation source route for an already-frozen predictive hypothesis."
        )
    )
    parser.add_argument("--research-package-dir", required=True)
    parser.add_argument("--rp-id", required=True)
    parser.add_argument("--hypothesis-id", required=True)
    parser.add_argument("--source-subject-id", required=True)
    parser.add_argument(
        "--historically-exposed-subject-id",
        action="append",
        default=[],
        help="repeatable objective exposure identifier; exposed subjects cannot be called retrospectively blind",
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--telemetry", required=True)
    parser.add_argument("--sol-spend-limit-usd", type=float, default=5.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output = Path(args.output)
    if output.exists():
        raise RuntimeError(f"refusing duplicate Sol spend because output already exists: {output}")
    if args.sol_spend_limit_usd <= 0:
        raise RuntimeError("--sol-spend-limit-usd must be positive")

    store = JsonResearchPackageStore(Path(args.research_package_dir))
    package = store.load(args.rp_id)
    if package is None:
        raise RuntimeError(f"Research Package does not exist: {args.rp_id}")
    matches = [
        item for item in package.predictive_hypotheses if item.hypothesis_id == args.hypothesis_id
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"RP {args.rp_id} must contain exactly one {args.hypothesis_id}: found {len(matches)}"
        )
    hypothesis = matches[0]

    os.environ["MTS_SOL_TELEMETRY_PATH"] = args.telemetry
    rd = SolBatchResearchDirector(
        research_package_store=store,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        sol_spend_limit_usd=args.sol_spend_limit_usd,
    )
    selection = select_validation_source(
        rd=rd,
        hypothesis=hypothesis,
        source_subject_id=args.source_subject_id,
        historically_exposed_subject_ids=args.historically_exposed_subject_id,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(selection.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    spend = rd.sol_spend_snapshot()
    print(f"HYPOTHESIS={selection.hypothesis_id}")
    print(f"VALIDATION_ROUTE={selection.route}")
    print(f"RATIONALE={selection.rationale}")
    print(f"EXTERNAL_SUBJECT_CRITERIA={selection.external_subject_criteria}")
    print(f"PROPOSED_EXTERNAL_SUBJECT_ID={selection.proposed_external_subject_id}")
    print("ADDITIONAL_INFORMATION_REQUIRED=" + json.dumps(list(selection.additional_information_required)))
    if spend is not None:
        print(f"SOL_SPEND_USD={spend.actual_spend_usd:.6f}")
    print(f"OUTPUT={output}")
    print(f"TELEMETRY={args.telemetry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
