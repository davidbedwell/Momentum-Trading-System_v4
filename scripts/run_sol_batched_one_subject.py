from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from MTS_V4.batch_contracts import BatchExecutionReport
from MTS_V4.batch_orchestrator import HumanSafetyBudget
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.bootstrap import DEFAULT_MISSION, build_batch_runtime
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _append_jsonl(path: Path, payload) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")) + "\n")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run one live MTS v4 subject through the batched Sol Research Director path. "
            "Sol may author as many scientifically relevant RPs and Analysis Specifications as warranted; "
            "the runtime returns only after each authorized batch completes."
        )
    )
    parser.add_argument("--ticker", required=True, help="equity ticker, e.g. AMD")
    parser.add_argument("--state-dir", default=None)
    parser.add_argument(
        "--human-safety-max-analyses",
        type=int,
        default=None,
        help=(
            "optional explicit human operational ceiling for total Analysis executions in this run; "
            "if a complete Sol-authored batch would exceed it, none of that batch executes and human "
            "authorization is required. This is not a scientific batch-size limit."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate CLI/configuration shape without Intake or Sol API calls",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    ticker = args.ticker.strip().upper()
    if not ticker:
        raise RuntimeError("ticker cannot be blank")
    if args.human_safety_max_analyses is not None and args.human_safety_max_analyses <= 0:
        raise RuntimeError("--human-safety-max-analyses must be positive when supplied")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    state_dir = Path(args.state_dir or f"/home/ubuntu/mts-v4-sol-batched-{ticker.lower()}-{stamp}")
    if args.dry_run:
        print(
            f"DRY_RUN=True TICKER={ticker} HUMAN_SAFETY_MAX_ANALYSES="
            f"{args.human_safety_max_analyses} STATE_DIR={state_dir}"
        )
        return 0

    state_dir.mkdir(parents=True, exist_ok=False)
    os.environ.setdefault(
        "MTS_SOL_TELEMETRY_PATH",
        str(state_dir / "sol_transport_telemetry.jsonl"),
    )
    subject = SubjectMetadata(subject_id=f"equity:{ticker}", ticker=ticker)
    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    recorder = BatchCampaignResearchRecorder(package_store=package_store)
    rd = SolBatchResearchDirector(
        research_package_store=package_store,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        required_subject_id=subject.subject_id,
        required_research_phase=ResearchPhase.EXPLORATION,
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
    campaign_id = f"mts-v4-sol-batched-{ticker.lower()}-{stamp}"

    decision_path = state_dir / "batch_decisions.jsonl"
    report_path = state_dir / "batch_reports.jsonl"
    latest_report: BatchExecutionReport | None = None

    def accepted(request):
        recorder.record_accepted_request(
            campaign_id=campaign_id,
            subject=subject,
            request=request,
        )

    def on_report(report, decisions, analyses):
        nonlocal latest_report
        latest_report = report
        recorder.record_report(report)
        _append_jsonl(
            report_path,
            {
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "decisions": decisions,
                "analyses_executed": analyses,
                "report": asdict(report),
            },
        )

    def on_decision(decision, decisions, analyses):
        recorder.record_plan(
            campaign_id=campaign_id,
            subject=subject,
            decision=decision,
        )
        recorder.record_predictive_hypothesis_updates(
            decision,
            current_report=latest_report,
        )
        recorder.record_closures(decision)
        _append_jsonl(
            decision_path,
            {
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "decision_sequence": decisions,
                "analyses_executed": analyses,
                "decision": asdict(decision),
            },
        )

    human_safety_budget = (
        HumanSafetyBudget(max_analysis_executions=args.human_safety_max_analyses)
        if args.human_safety_max_analyses is not None
        else None
    )
    outcome = runtime.orchestrator.run(
        subject=subject,
        evidence=evidence,
        human_safety_budget=human_safety_budget,
        decision_callback=on_decision,
        report_callback=on_report,
        accepted_request_callback=accepted,
    )

    summary = {
        "campaign_id": campaign_id,
        "subject_id": subject.subject_id,
        "decisions": outcome.decisions,
        "batches_executed": outcome.batches_executed,
        "analyses_executed": outcome.analyses_executed,
        "findings_promoted": outcome.findings_promoted,
        "closed": outcome.closed,
        "close_reason": outcome.close_reason,
        "human_authorization_required": outcome.human_authorization_required,
        "pending_batch_analysis_count": outcome.pending_batch_analysis_count,
        "human_safety_limit": outcome.human_safety_limit,
        "sol_transport_telemetry": str(state_dir / "sol_transport_telemetry.jsonl"),
    }
    (state_dir / "run_summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"CAMPAIGN_ID={campaign_id}", flush=True)
    print(f"SUBJECT={subject.subject_id}", flush=True)
    print(f"DECISIONS={outcome.decisions}", flush=True)
    print(f"BATCHES={outcome.batches_executed}", flush=True)
    print(f"ANALYSES={outcome.analyses_executed}", flush=True)
    print(f"CLOSED={outcome.closed}", flush=True)
    print(f"CLOSE_REASON={outcome.close_reason}", flush=True)
    print(f"HUMAN_AUTHORIZATION_REQUIRED={outcome.human_authorization_required}", flush=True)
    print(f"PENDING_BATCH_ANALYSES={outcome.pending_batch_analysis_count}", flush=True)
    print(f"SOL_TELEMETRY={state_dir / 'sol_transport_telemetry.jsonl'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
