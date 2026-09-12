from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from MTS_V4.bootstrap import DEFAULT_MISSION, build_batch_runtime
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector
from MTS_V4.sol_spend_guard import DEFAULT_AUTHORIZED_SOL_SPEND_USD


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Make exactly one Sol batched Research Director planning call for one ticker, "
            "persist/print the returned scientific plan, and stop before Analysis execution."
        )
    )
    parser.add_argument("--ticker", required=True, help="equity ticker, e.g. AMD")
    parser.add_argument("--state-dir", default=None)
    parser.add_argument(
        "--sol-spend-limit-usd",
        type=float,
        default=DEFAULT_AUTHORIZED_SOL_SPEND_USD,
        help="human authorization for this single Sol planning call; default $20",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate configuration shape without Intake or Sol API calls",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    ticker = args.ticker.strip().upper()
    if not ticker:
        raise RuntimeError("ticker cannot be blank")
    if args.sol_spend_limit_usd <= 0:
        raise RuntimeError("--sol-spend-limit-usd must be positive")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    state_dir = Path(args.state_dir or f"/home/ubuntu/mts-v4-sol-planning-probe-{ticker.lower()}-{stamp}")
    if args.dry_run:
        print(
            f"DRY_RUN=True TICKER={ticker} SOL_SPEND_LIMIT_USD={args.sol_spend_limit_usd:.2f} "
            f"STATE_DIR={state_dir} SOL_CALLS=0 ANALYSIS_EXECUTIONS=0"
        )
        return 0

    state_dir.mkdir(parents=True, exist_ok=False)
    os.environ.setdefault("MTS_SOL_TELEMETRY_PATH", str(state_dir / "sol_transport_telemetry.jsonl"))

    subject = SubjectMetadata(subject_id=f"equity:{ticker}", ticker=ticker)
    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    rd = SolBatchResearchDirector(
        research_package_store=package_store,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        required_subject_id=subject.subject_id,
        required_research_phase=ResearchPhase.EXPLORATION,
        sol_spend_limit_usd=args.sol_spend_limit_usd,
        human_spend_authorization_callback=None,
    )
    runtime = build_batch_runtime(
        rd=rd,
        mission=DEFAULT_MISSION,
        nexus_path=state_dir / "research_nexus.json",
    )
    evidence = IntakeEngine(runtime.cache).ingest(
        subject=subject,
        source=standard_live_market_source(),
    )

    decision = rd.begin_batch_research(
        mission=DEFAULT_MISSION,
        subject=subject,
        evidence=evidence,
        available_methods=runtime.catalog.capability_payloads(),
        nexus_context={
            "subject": subject,
            "evidence_metadata": tuple(item.durable_metadata() for item in evidence),
            "significant_findings": (),
            "historical_analysis_result_metadata": (),
            "research_concepts": runtime.concepts.payloads(),
            "campaign_analysis_result_catalog": (),
            "planning_probe": {
                "purpose": (
                    "Design the complete scientifically justified investigation that can be specified now. "
                    "Include all currently justified RPs and analyses whose justification does not depend on "
                    "an unseen intermediate result. Mark contingent work with explicit decision boundaries."
                ),
                "analysis_execution_enabled": False,
                "return_after_this_decision": True,
            },
        },
    )

    payload = asdict(decision)
    output_path = state_dir / "planning_probe_decision.json"
    output_path.write_text(json.dumps(payload, sort_keys=True, indent=2, default=str) + "\n", encoding="utf-8")

    spend = rd.sol_spend_snapshot()
    rp_count = len(decision.research_packages)
    analysis_count = sum(len(package.analyses) for package in decision.research_packages)
    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"SUBJECT={subject.subject_id}", flush=True)
    print("SOL_CALLS=1", flush=True)
    print("ANALYSIS_EXECUTIONS=0", flush=True)
    print(f"RESEARCH_PACKAGES={rp_count}", flush=True)
    print(f"ANALYSIS_SPECIFICATIONS={analysis_count}", flush=True)
    if decision.research_progress is not None:
        print(
            f"ESTIMATED_PERCENT_COMPLETE={decision.research_progress.estimated_percent_complete}",
            flush=True,
        )
        print(
            f"ESTIMATED_REMAINING_BATCHES={decision.research_progress.estimated_remaining_batches}",
            flush=True,
        )
        print(
            f"ESTIMATED_REMAINING_SOL_CALLS={decision.research_progress.estimated_remaining_sol_calls}",
            flush=True,
        )
    if spend is not None:
        print(f"SOL_SPEND_USD={spend.actual_spend_usd:.4f}", flush=True)
    print(f"PLAN={output_path}", flush=True)
    print("--- SOL PLAN JSON ---", flush=True)
    print(json.dumps(payload, sort_keys=True, indent=2, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
