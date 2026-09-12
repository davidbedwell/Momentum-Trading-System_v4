from __future__ import annotations

import argparse
import json
from pathlib import Path

from MTS_V4.predictive_provenance import relocate_predictive_hypothesis
from MTS_V4.research_package_store import JsonResearchPackageStore


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Relocate one frozen predictive hypothesis to the correct durable Research Package "
            "without changing its scientific definition, source results, validation history, or status."
        )
    )
    parser.add_argument("--research-package-dir", required=True)
    parser.add_argument("--hypothesis-id", required=True)
    parser.add_argument("--source-rp-id", required=True)
    parser.add_argument("--target-rp-id", required=True)
    parser.add_argument("--target-objective", required=True)
    parser.add_argument("--target-rationale", required=True)
    parser.add_argument("--parent-rp-id", default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    store = JsonResearchPackageStore(Path(args.research_package_dir))
    source = store.load(args.source_rp_id)
    if source is None:
        raise RuntimeError(f"source RP does not exist: {args.source_rp_id}")
    matches = [
        item for item in source.predictive_hypotheses if item.hypothesis_id == args.hypothesis_id
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"source RP must contain exactly one {args.hypothesis_id}: found {len(matches)}"
        )
    hypothesis = matches[0]

    print(f"HYPOTHESIS={hypothesis.hypothesis_id}")
    print(f"SOURCE_RP={args.source_rp_id}")
    print(f"TARGET_RP={args.target_rp_id}")
    print(f"SOURCE_RESULT_IDS={len(hypothesis.source_result_ids)}")
    print(f"TRIALS={len(hypothesis.trials)}")
    print(f"STATUS={hypothesis.status}")
    print("SCIENTIFIC_DEFINITION_CHANGED=False")
    if args.dry_run:
        print("DRY_RUN=True")
        return 0

    repaired_source, repaired_target = relocate_predictive_hypothesis(
        store=store,
        hypothesis_id=args.hypothesis_id,
        source_rp_id=args.source_rp_id,
        target_rp_id=args.target_rp_id,
        target_objective=args.target_objective,
        target_rationale=args.target_rationale,
        parent_rp_id=args.parent_rp_id,
    )
    target_hypothesis = next(
        item
        for item in repaired_target.predictive_hypotheses
        if item.hypothesis_id == args.hypothesis_id
    )
    print("REPAIR_APPLIED=True")
    print(f"SOURCE_HYPOTHESES_AFTER={len(repaired_source.predictive_hypotheses)}")
    print(f"TARGET_HYPOTHESES_AFTER={len(repaired_target.predictive_hypotheses)}")
    print(
        "TARGET_HYPOTHESIS="
        + json.dumps(
            {
                "hypothesis_id": target_hypothesis.hypothesis_id,
                "statement": target_hypothesis.statement,
                "success_definition": target_hypothesis.success_definition,
                "minimum_required_trials": target_hypothesis.minimum_required_trials,
                "source_result_ids": list(target_hypothesis.source_result_ids),
                "status": target_hypothesis.status,
                "trial_count": len(target_hypothesis.trials),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
