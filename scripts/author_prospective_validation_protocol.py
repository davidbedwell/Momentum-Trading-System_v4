from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from MTS_V4.prospective_validation import (
    JsonProspectiveValidationStore,
    ProspectiveValidationFrontier,
)
from MTS_V4.prospective_validation_authoring import author_prospective_validation_protocol
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Use one Sol scientific-reasoning call to author and freeze the prospective validation protocol for an already-frozen hypothesis."
        )
    )
    parser.add_argument("--research-package-dir", required=True)
    parser.add_argument("--rp-id", required=True)
    parser.add_argument("--hypothesis-id", required=True)
    parser.add_argument("--source-subject-id", required=True)
    parser.add_argument("--validation-source-selection", required=True)
    parser.add_argument("--last-historical-exposure-utc", required=True)
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
    selection = json.loads(Path(args.validation_source_selection).read_text(encoding="utf-8"))

    os.environ["MTS_SOL_TELEMETRY_PATH"] = args.telemetry
    rd = SolBatchResearchDirector(
        research_package_store=store,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        sol_spend_limit_usd=args.sol_spend_limit_usd,
    )
    protocol = author_prospective_validation_protocol(
        rd=rd,
        hypothesis=hypothesis,
        source_subject_id=args.source_subject_id,
        validation_source_selection=selection,
        last_historical_exposure_utc=args.last_historical_exposure_utc,
    )
    frontier = ProspectiveValidationFrontier.arm(protocol)
    JsonProspectiveValidationStore(output).save(protocol=protocol, frontier=frontier)

    spend = rd.sol_spend_snapshot()
    print(f"HYPOTHESIS={protocol.hypothesis_id}")
    print(f"PROTOCOL_ID={protocol.protocol_id}")
    print(f"PROTOCOL_FINGERPRINT={protocol.fingerprint}")
    print(f"COLLECTION_START_UTC={protocol.collection_start_utc}")
    print(f"OUTCOME_HORIZON_SESSIONS={protocol.outcome_horizon_sessions}")
    print(f"NON_OVERLAP_SCOPE={protocol.non_overlap_scope}")
    print(f"REQUIRED_TRIALS={protocol.minimum_required_trials}")
    print(f"FRONTIER_STATE={frontier.state}")
    print(f"NEXT_TRIAL_ID={protocol.hypothesis_id}-T01")
    if spend is not None:
        print(f"SOL_SPEND_USD={spend.actual_spend_usd:.6f}")
    print(f"OUTPUT={output}")
    print(f"TELEMETRY={args.telemetry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
