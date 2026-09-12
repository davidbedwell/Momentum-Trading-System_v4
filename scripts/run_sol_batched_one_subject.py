from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from MTS_V4.batch_contracts import BatchExecutionReport
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.bootstrap import DEFAULT_MISSION, build_batch_runtime
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_spend_guard import (
    DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    SolSpendAuthorizationRequired,
    SolSpendAuthorizationSnapshot,
)
from MTS_V4.subject_scientific_context import (
    SubjectContextSolBatchResearchDirector,
    load_subject_scientific_context,
)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _append_jsonl(path: Path, payload) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")) + "\n")


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


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run one live MTS v4 subject through the batched Sol Research Director path with permanent "
            "cross-subject scientific memory/frontier and prior durable subject science."
        )
    )
    parser.add_argument("--ticker", required=True, help="equity ticker, e.g. AMD")
    parser.add_argument("--root", default="/home/ubuntu")
    parser.add_argument("--state-dir", default=None)
    parser.add_argument(
        "--sol-spend-limit-usd",
        type=float,
        default=DEFAULT_AUTHORIZED_SOL_SPEND_USD,
        help=(
            "initial human authorization for Sol API spend for this subject; default is $20. "
            "When Sol's own remaining-work estimate projects more spend, the runner stops before "
            "the next Sol call and requests human authorization for a higher dollar ceiling."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate CLI/configuration and scientific context without Intake or Sol API calls",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    ticker = args.ticker.strip().upper()
    if not ticker:
        raise RuntimeError("ticker cannot be blank")
    if args.sol_spend_limit_usd <= 0:
        raise RuntimeError("--sol-spend-limit-usd must be positive")

    root = Path(args.root).expanduser().resolve()
    subject = SubjectMetadata(subject_id=f"equity:{ticker}", ticker=ticker)
    scientific_context = load_subject_scientific_context(root, active_subject_id=subject.subject_id)
    prior_package_count = sum(
        len(item.get("research_packages", []))
        for item in scientific_context.prior_subject_science.get("subjects", [])
        if isinstance(item, dict)
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    state_dir = Path(args.state_dir or f"/home/ubuntu/mts-v4-sol-batched-{ticker.lower()}-{stamp}")
    frontier = scientific_context.memory_selection.store.frontier()
    if args.dry_run:
        print(f"DRY_RUN=True")
        print(f"TICKER={ticker}")
        print(f"STATE_DIR={state_dir}")
        print(f"SOL_SPEND_LIMIT_USD={args.sol_spend_limit_usd:.2f}")
        print(f"CANONICAL_MEMORY_SOURCE={scientific_context.memory_selection.source_path}")
        print(f"CANONICAL_MEMORY_RECORDS={len(scientific_context.memory_selection.store.records())}")
        print(f"CANONICAL_MEMORY_FRONTIER_VERSION={frontier.version if frontier is not None else 0}")
        print(f"PRIOR_SUBJECT_SCIENTIFIC_PACKAGES={prior_package_count}")
        print("CROSS_SUBJECT_CONTEXT_AUTOMATIC=True")
        print("SOL_CALLS=0")
        return 0

    state_dir.mkdir(parents=True, exist_ok=False)
    os.environ.setdefault(
        "MTS_SOL_TELEMETRY_PATH",
        str(state_dir / "sol_transport_telemetry.jsonl"),
    )
    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    recorder = BatchCampaignResearchRecorder(package_store=package_store)
    rd = SubjectContextSolBatchResearchDirector(
        research_package_store=package_store,
        prior_subject_scientific_context=scientific_context.prior_subject_science,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        required_subject_id=subject.subject_id,
        required_research_phase=ResearchPhase.EXPLORATION,
        sol_spend_limit_usd=args.sol_spend_limit_usd,
        human_spend_authorization_callback=_interactive_spend_authorization,
    )
    runtime = build_batch_runtime(
        rd=rd,
        mission=DEFAULT_MISSION,
        nexus_path=state_dir / "research_nexus.json",
        scientific_memory=scientific_context.memory_selection.store,
    )
    evidence = IntakeEngine(runtime.cache).ingest(
        subject=subject,
        source=standard_live_market_source(),
    )
    campaign_id = f"mts-v4-sol-batched-{ticker.lower()}-{stamp}"

    (state_dir / "subject_scientific_context.json").write_text(
        json.dumps(
            {
                "active_subject_id": subject.subject_id,
                "canonical_memory_source": str(scientific_context.memory_selection.source_path),
                "canonical_memory_superseded_paths": [
                    str(path) for path in scientific_context.memory_selection.superseded_paths
                ],
                "canonical_memory_frontier_version": frontier.version if frontier is not None else 0,
                "canonical_memory_record_count": len(scientific_context.memory_selection.store.records()),
                "prior_subject_scientific_context": scientific_context.prior_subject_science,
            },
            sort_keys=True,
            indent=2,
            default=str,
        ) + "\n",
        encoding="utf-8",
    )

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

    try:
        outcome = runtime.orchestrator.run(
            subject=subject,
            evidence=evidence,
            decision_callback=on_decision,
            report_callback=on_report,
            accepted_request_callback=accepted,
        )
    except SolSpendAuthorizationRequired as exc:
        artifact = state_dir / "sol_spend_authorization_required.json"
        artifact.write_text(
            json.dumps(asdict(exc.snapshot), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"STATE_DIR={state_dir}", flush=True)
        print("HUMAN_SOL_SPEND_AUTHORIZATION_REQUIRED=True", flush=True)
        print(f"AUTHORIZATION_ARTIFACT={artifact}", flush=True)
        return 2

    spend = rd.sol_spend_snapshot()
    summary = {
        "campaign_id": campaign_id,
        "subject_id": subject.subject_id,
        "cross_subject_context_automatic": True,
        "canonical_cross_subject_memory_source": str(scientific_context.memory_selection.source_path),
        "canonical_cross_subject_memory_record_count": len(scientific_context.memory_selection.store.records()),
        "canonical_cross_subject_frontier_version": frontier.version if frontier is not None else 0,
        "prior_subject_scientific_packages_exposed": prior_package_count,
        "decisions": outcome.decisions,
        "batches_executed": outcome.batches_executed,
        "analyses_executed": outcome.analyses_executed,
        "findings_promoted": outcome.findings_promoted,
        "closed": outcome.closed,
        "close_reason": outcome.close_reason,
        "sol_spend": asdict(spend) if spend is not None else None,
        "sol_transport_telemetry": str(state_dir / "sol_transport_telemetry.jsonl"),
    }
    (state_dir / "run_summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"CAMPAIGN_ID={campaign_id}", flush=True)
    print(f"SUBJECT={subject.subject_id}", flush=True)
    print("CROSS_SUBJECT_CONTEXT_AUTOMATIC=True", flush=True)
    print(f"PRIOR_SUBJECT_SCIENTIFIC_PACKAGES={prior_package_count}", flush=True)
    print(f"DECISIONS={outcome.decisions}", flush=True)
    print(f"BATCHES={outcome.batches_executed}", flush=True)
    print(f"ANALYSES={outcome.analyses_executed}", flush=True)
    print(f"CLOSED={outcome.closed}", flush=True)
    print(f"CLOSE_REASON={outcome.close_reason}", flush=True)
    if spend is not None:
        print(f"SOL_SPEND_USD={spend.actual_spend_usd:.4f}", flush=True)
        print(f"SOL_AUTHORIZED_USD={spend.authorized_spend_usd:.2f}", flush=True)
    print(f"SOL_TELEMETRY={state_dir / 'sol_transport_telemetry.jsonl'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
