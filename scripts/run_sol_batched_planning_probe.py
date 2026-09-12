from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from MTS_V4.batch_contracts import BatchExecutionReport, BatchResearchDecision
from MTS_V4.bootstrap import DEFAULT_MISSION, build_batch_runtime
from MTS_V4.contracts import EvidenceDescriptor, ResearchPhase, SubjectMetadata
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector
from MTS_V4.sol_spend_guard import (
    DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    SolSpendAuthorizationRequired,
    SolSpendAuthorizationSnapshot,
)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _format_money(value: float | None) -> str:
    return "unknown" if value is None else f"${value:.2f}"


def _interactive_spend_authorization(snapshot: SolSpendAuthorizationSnapshot) -> float | None:
    print("\nHUMAN SOL SPEND AUTHORIZATION REQUIRED", flush=True)
    print(f"AUTHORIZED={_format_money(snapshot.authorized_spend_usd)}", flush=True)
    print(f"ACTUAL_SPEND={_format_money(snapshot.actual_spend_usd)}", flush=True)
    print(f"SOL_CALLS_COMPLETED={snapshot.completed_sol_calls}", flush=True)
    print(f"ESTIMATED_PERCENT_COMPLETE={snapshot.estimated_percent_complete}", flush=True)
    print(f"ESTIMATED_REMAINING_BATCHES={snapshot.estimated_remaining_batches}", flush=True)
    print(f"ESTIMATED_REMAINING_SOL_CALLS={snapshot.estimated_remaining_sol_calls}", flush=True)
    print(
        "ESTIMATED_ADDITIONAL_SPEND="
        f"{_format_money(snapshot.estimated_additional_spend_low_usd)}-"
        f"{_format_money(snapshot.estimated_additional_spend_high_usd)}",
        flush=True,
    )
    print(
        "ESTIMATED_TOTAL_SPEND="
        f"{_format_money(snapshot.estimated_total_spend_low_usd)}-"
        f"{_format_money(snapshot.estimated_total_spend_high_usd)}",
        flush=True,
    )
    print(f"ESTIMATE_CONFIDENCE={snapshot.estimate_confidence}", flush=True)
    print(f"ESTIMATE_RATIONALE={snapshot.estimate_rationale}", flush=True)
    print(
        f"RECOMMENDED_NEW_CEILING={_format_money(snapshot.recommended_authorized_ceiling_usd)}",
        flush=True,
    )
    try:
        raw = input(
            "Enter a new total Sol spend ceiling in USD to authorize more, or press Enter to stop: "
        ).strip()
    except EOFError:
        return None
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        print("Authorization was not numeric; stopping before another Sol call.", flush=True)
        return None
    if value <= snapshot.authorized_spend_usd:
        print("New authorization must exceed the current ceiling; stopping.", flush=True)
        return None
    return value


class _SeededPlanningDirector:
    """Return one already-authored Sol decision, then delegate all interpretation to Sol.

    This prevents the normal orchestrator from paying for a second BEGIN_RESEARCH call
    after the planning probe has already produced a valid scientific batch. The seeded
    decision is returned unchanged exactly once.
    """

    def __init__(self, delegate: SolBatchResearchDirector) -> None:
        self._delegate = delegate
        self._seed: BatchResearchDecision | None = None
        self._seed_consumed = False

    def seed(self, decision: BatchResearchDecision) -> None:
        if self._seed is not None or self._seed_consumed:
            raise RuntimeError("planning decision has already been seeded or consumed")
        self._seed = decision

    def begin_batch_research(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> BatchResearchDecision:
        del mission, subject, evidence, available_methods, nexus_context
        if self._seed is None or self._seed_consumed:
            raise RuntimeError("no unconsumed planning decision is available")
        self._seed_consumed = True
        return self._seed

    def interpret_batch_results(self, **kwargs) -> BatchResearchDecision:
        return self._delegate.interpret_batch_results(**kwargs)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Make exactly one Sol batched Research Director planning call for one ticker, "
            "persist/print the returned scientific plan, then optionally execute that exact plan "
            "without paying for a second BEGIN_RESEARCH call."
        )
    )
    parser.add_argument("--ticker", required=True, help="equity ticker, e.g. AMD")
    parser.add_argument("--state-dir", default=None)
    parser.add_argument(
        "--sol-spend-limit-usd",
        type=float,
        default=DEFAULT_AUTHORIZED_SOL_SPEND_USD,
        help="initial human Sol spend authorization; default $20",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "after printing/saving the one-call Sol plan, execute that exact plan and continue the "
            "normal Analysis -> consolidated results -> Sol loop without another initial planning call"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate configuration shape without Intake, Sol, or Analysis calls",
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
            f"STATE_DIR={state_dir} SOL_CALLS=0 ANALYSIS_EXECUTIONS=0 EXECUTE={args.execute}"
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
        human_spend_authorization_callback=_interactive_spend_authorization,
    )
    seeded_rd = _SeededPlanningDirector(rd)
    runtime = build_batch_runtime(
        rd=seeded_rd,
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
                "approved_plan_may_be_executed_unchanged": True,
            },
        },
    )

    payload = asdict(decision)
    output_path = state_dir / "planning_probe_decision.json"
    output_path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

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

    if not args.execute:
        print("PLAN_EXECUTED=False", flush=True)
        print(
            "Re-run with --execute only when you want this same process to execute the exact plan immediately; "
            "a later process cannot reuse the in-memory Intake cache yet.",
            flush=True,
        )
        return 0

    if not decision.continue_research:
        print("PLAN_EXECUTED=False", flush=True)
        print("PLAN_CLOSED_RESEARCH=True", flush=True)
        return 0

    try:
        approval = input("Execute this exact Sol-authored plan now? [y/N]: ").strip().lower()
    except EOFError:
        approval = ""
    if approval not in {"y", "yes"}:
        print("PLAN_EXECUTED=False", flush=True)
        print("STOPPED_AFTER_PLANNING=True", flush=True)
        return 0

    seeded_rd.seed(decision)
    decision_path = state_dir / "continued_batch_decisions.jsonl"
    report_path = state_dir / "continued_batch_reports.jsonl"
    latest_report: BatchExecutionReport | None = None

    def _append_jsonl(path: Path, row: Mapping[str, object]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, default=str, separators=(",", ":")) + "\n")

    def on_report(report: BatchExecutionReport, decisions: int, analyses: int) -> None:
        nonlocal latest_report
        latest_report = report
        _append_jsonl(
            report_path,
            {
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "decisions": decisions,
                "analyses_executed": analyses,
                "report": asdict(report),
            },
        )

    def on_decision(current: BatchResearchDecision, decisions: int, analyses: int) -> None:
        _append_jsonl(
            decision_path,
            {
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "decision_sequence": decisions,
                "analyses_executed": analyses,
                "decision": asdict(current),
                "seeded_from_planning_probe": decisions == 1,
                "prior_report_available": latest_report is not None,
            },
        )

    try:
        outcome = runtime.orchestrator.run(
            subject=subject,
            evidence=evidence,
            decision_callback=on_decision,
            report_callback=on_report,
        )
    except SolSpendAuthorizationRequired as exc:
        artifact = state_dir / "sol_spend_authorization_required.json"
        artifact.write_text(
            json.dumps(asdict(exc.snapshot), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        print("PLAN_EXECUTED=True", flush=True)
        print("HUMAN_SOL_SPEND_AUTHORIZATION_REQUIRED=True", flush=True)
        print(f"AUTHORIZATION_ARTIFACT={artifact}", flush=True)
        return 2

    final_spend = rd.sol_spend_snapshot()
    summary = {
        "subject_id": subject.subject_id,
        "planning_probe_reused_as_initial_decision": True,
        "initial_sol_calls_before_analysis": 1,
        "decisions_in_execution_loop": outcome.decisions,
        "batches_executed": outcome.batches_executed,
        "analyses_executed": outcome.analyses_executed,
        "findings_promoted": outcome.findings_promoted,
        "closed": outcome.closed,
        "close_reason": outcome.close_reason,
        "sol_spend": asdict(final_spend) if final_spend is not None else None,
    }
    summary_path = state_dir / "continued_run_summary.json"
    summary_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    print("PLAN_EXECUTED=True", flush=True)
    print("PLANNING_PROBE_REUSED=True", flush=True)
    print(f"BATCHES={outcome.batches_executed}", flush=True)
    print(f"ANALYSES={outcome.analyses_executed}", flush=True)
    print(f"CLOSED={outcome.closed}", flush=True)
    print(f"CLOSE_REASON={outcome.close_reason}", flush=True)
    if final_spend is not None:
        print(f"SOL_SPEND_USD={final_spend.actual_spend_usd:.4f}", flush=True)
        print(f"SOL_AUTHORIZED_USD={final_spend.authorized_spend_usd:.2f}", flush=True)
    print(f"SUMMARY={summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
