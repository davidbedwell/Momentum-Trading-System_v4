from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile

from MTS_V4.batch_campaign_continuation import (
    ContinuationBaseline,
    RecoveredBatchCampaignContinuation,
)
from MTS_V4.batch_campaign_reconstruction import reconstruct_batched_campaign
from MTS_V4.batch_contracts import BatchExecutionReport
from MTS_V4.batch_rd_codec import BatchResearchDecisionCodec
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.bootstrap import build_batch_runtime
from MTS_V4.contracts import ResearchPhase
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.retrospective_recovery import SolRetrospectiveRecoveryResearchDirector
from MTS_V4.sol_spend_guard import SolSpendAuthorizationRequired


RETROSPECTIVE_MISSION = (
    "Discover reproducible relationships between market information observable at time T and subsequent market "
    "behavior at T+1 onward. This is retrospective recovery of a subject previously processed under deficient "
    "lifecycle logic. All preserved historical subject work is exposed exploratory evidence and must never be counted "
    "as blind validation. AI Research Director owns scientific judgment; deterministic code may only enforce objective "
    "execution and representation contracts."
)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _append_jsonl(path: Path, row: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, default=str, separators=(",", ":")) + "\n")


def _telemetry_spend(path: Path) -> float:
    if not path.is_file():
        return 0.0
    cumulative: list[float] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("event") != "SOL_CALL_COMPLETE":
            continue
        value = row.get("estimated_cumulative_sol_spend_usd")
        if value is not None:
            cumulative.append(float(value))
    return max(cumulative) if cumulative else 0.0


def _decode_decision(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    return BatchResearchDecisionCodec.decode(json.dumps(raw, sort_keys=True, default=str))


def _direct_evidence_ids(decision) -> set[str]:
    return {
        ref.evidence_id
        for package in decision.research_packages
        for analysis in package.analyses
        for ref in analysis.inputs
        if ref.evidence_id is not None
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Continue an interrupted retrospective campaign after its completed batch has been returned to Sol. "
            "The already recovered Analysis results are dependencies only and are never re-executed."
        )
    )
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--total-sol-spend-limit-usd", type=float, default=20.0)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="verify the accepted continuation decision and prior-result boundary without Intake, Analysis, or Sol",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    state_dir = Path(args.state_dir).expanduser().resolve()
    if not state_dir.is_dir():
        raise RuntimeError(f"state directory does not exist: {state_dir}")

    decisions_path = state_dir / "batch_decisions.jsonl"
    reports_path = state_dir / "batch_reports.jsonl"
    nexus_path = state_dir / "research_nexus.json"
    package_store_dir = state_dir / "research_packages"
    context_path = state_dir / "retrospective_context.json"
    resume_decision_path = state_dir / "resume_interpretation_decision.json"
    original_telemetry = state_dir / "sol_transport_telemetry.jsonl"
    resume_telemetry = state_dir / "resume_sol_transport_telemetry.jsonl"
    continuation_telemetry = state_dir / "continuation_sol_transport_telemetry.jsonl"
    summary_path = state_dir / "continuation_summary.json"

    for path in (
        decisions_path,
        reports_path,
        nexus_path,
        context_path,
        resume_decision_path,
    ):
        if not path.is_file():
            raise RuntimeError(f"required continuation artifact is missing: {path}")
    if not package_store_dir.is_dir():
        raise RuntimeError(f"recovered Research Package store does not exist: {package_store_dir}")
    if summary_path.exists():
        raise RuntimeError("continuation summary already exists; refusing to rerun a completed continuation")

    retrospective_context = json.loads(context_path.read_text(encoding="utf-8"))
    initial_decision = _decode_decision(resume_decision_path)
    if not initial_decision.continue_research:
        raise RuntimeError("resume decision already closed the subject; there is nothing to continue")

    campaign_id = state_dir.name
    nexus_document = json.loads(nexus_path.read_text(encoding="utf-8"))
    subject_ids = sorted(
        {
            str(item["subject_id"])
            for item in nexus_document.get("subjects", [])
            if isinstance(item, dict) and isinstance(item.get("subject_id"), str)
        }
    )
    if len(subject_ids) != 1:
        raise RuntimeError(f"expected exactly one Nexus subject, found: {subject_ids}")
    subject_id = subject_ids[0]

    with tempfile.TemporaryDirectory(prefix="mts-v4-retro-continue-verify-") as temporary:
        reconstructed = reconstruct_batched_campaign(
            decisions_jsonl=decisions_path,
            reports_jsonl=reports_path,
            nexus_json=nexus_path,
            package_store_dir=Path(temporary) / "research_packages",
            campaign_id=campaign_id,
            subject_id=subject_id,
        )

    prior_spend = _telemetry_spend(original_telemetry) + _telemetry_spend(resume_telemetry)
    remaining = args.total_sol_spend_limit_usd - prior_spend
    if remaining <= 0:
        raise RuntimeError("no Sol authorization remains under the requested total subject ceiling")

    baseline = ContinuationBaseline(
        decisions=len(reconstructed.decisions) + 1,
        batches_executed=len(reconstructed.reports),
        analyses_executed=reconstructed.analyses_executed,
    )
    requested_analysis_ids = [
        analysis.analysis_id
        for package in initial_decision.research_packages
        for analysis in package.analyses
    ]
    collisions = sorted(set(requested_analysis_ids).intersection(reconstructed.results_by_analysis_id))
    if collisions:
        raise RuntimeError(
            "resume decision attempts to reuse completed analysis_id(s): " + ", ".join(collisions)
        )

    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"CAMPAIGN_ID={campaign_id}", flush=True)
    print(f"SUBJECT={subject_id}", flush=True)
    print(f"RECOVERED_RESULTS={len(reconstructed.results_by_analysis_id)}", flush=True)
    print(f"RESUMED_ANALYSIS_SPECIFICATIONS={len(requested_analysis_ids)}", flush=True)
    print("RESUMED_ANALYSIS_IDS=" + ",".join(requested_analysis_ids), flush=True)
    print(f"PRIOR_SOL_SPEND_USD={prior_spend:.6f}", flush=True)
    print(f"REMAINING_SOL_AUTHORIZATION_USD={remaining:.6f}", flush=True)
    print("PRIOR_ANALYSIS_REEXECUTION_ALLOWED=False", flush=True)

    if args.dry_run:
        print("DRY_RUN=True", flush=True)
        print("INTAKE_CALLS=0", flush=True)
        print("ANALYSIS_EXECUTIONS=0", flush=True)
        print("SOL_CALLS=0", flush=True)
        return 0

    recovered_store = JsonResearchPackageStore(package_store_dir)
    os.environ["MTS_SOL_TELEMETRY_PATH"] = str(continuation_telemetry)
    rd = SolRetrospectiveRecoveryResearchDirector(
        research_package_store=recovered_store,
        retrospective_context=retrospective_context,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        required_subject_id=subject_id,
        required_research_phase=ResearchPhase.EXPLORATION,
        sol_spend_limit_usd=remaining,
    )
    runtime = build_batch_runtime(
        rd=rd,
        mission=RETROSPECTIVE_MISSION,
        nexus_path=nexus_path,
    )

    evidence = IntakeEngine(runtime.cache).ingest(
        subject=reconstructed.subject,
        source=standard_live_market_source(),
    )
    fresh_ids = {item.evidence_id for item in evidence}
    required_direct = _direct_evidence_ids(initial_decision)
    missing_direct = sorted(required_direct - fresh_ids)
    if missing_direct:
        raise RuntimeError(
            "cannot execute the accepted Sol decision without substituting evidence. "
            "Fresh Intake did not reproduce required evidence_id(s): " + ", ".join(missing_direct)
        )

    recorder = BatchCampaignResearchRecorder(package_store=recovered_store)
    continued_report_path = state_dir / "continuation_batch_reports.jsonl"
    continued_decision_path = state_dir / "continuation_batch_decisions.jsonl"
    latest_report: BatchExecutionReport | None = None

    def accepted(request):
        recorder.record_accepted_request(
            campaign_id=campaign_id,
            subject=reconstructed.subject,
            request=request,
        )

    def on_report(report, decisions, analyses):
        nonlocal latest_report
        latest_report = report
        recorder.record_report(report)
        _append_jsonl(
            continued_report_path,
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
            subject=reconstructed.subject,
            decision=decision,
        )
        recorder.record_predictive_hypothesis_updates(
            decision,
            current_report=latest_report,
        )
        recorder.record_closures(decision)
        _append_jsonl(
            continued_decision_path,
            {
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "decision_sequence": decisions,
                "analyses_executed": analyses,
                "decision": asdict(decision),
            },
        )

    continuation = RecoveredBatchCampaignContinuation(
        mission=RETROSPECTIVE_MISSION,
        rd=rd,
        validator=runtime.validator,
        analysis=runtime.analysis,
        nexus=runtime.nexus,
        cache=runtime.cache,
        available_methods=runtime.catalog.capability_payloads(),
        research_concepts=runtime.concepts.payloads(),
    )

    try:
        outcome = continuation.continue_from_decision(
            subject=reconstructed.subject,
            evidence=evidence,
            initial_decision=initial_decision,
            prior_results_by_analysis_id=reconstructed.results_by_analysis_id,
            baseline=baseline,
            decision_callback=on_decision,
            report_callback=on_report,
            accepted_request_callback=accepted,
        )
    except SolSpendAuthorizationRequired as exc:
        artifact = state_dir / "continuation_sol_spend_authorization_required.json"
        artifact.write_text(
            json.dumps(asdict(exc.snapshot), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("HUMAN_SOL_SPEND_AUTHORIZATION_REQUIRED=True", flush=True)
        print(f"AUTHORIZATION_ARTIFACT={artifact}", flush=True)
        return 2

    spend = rd.sol_spend_snapshot()
    continuation_spend = 0.0 if spend is None else spend.actual_spend_usd
    continuation_analyses = outcome.analyses_executed - baseline.analyses_executed
    continuation_batches = outcome.batches_executed - baseline.batches_executed
    summary = {
        "campaign_id": campaign_id,
        "subject_id": subject_id,
        "historical_exposure_status": "EXPOSED",
        "blind_validation_claim_allowed": False,
        "recovered_results": len(reconstructed.results_by_analysis_id),
        "prior_analysis_reexecution_allowed": False,
        "continuation_batches_executed": continuation_batches,
        "continuation_analyses_executed": continuation_analyses,
        "total_decisions": outcome.decisions,
        "total_batches_executed": outcome.batches_executed,
        "total_analyses_executed": outcome.analyses_executed,
        "closed": outcome.closed,
        "close_reason": outcome.close_reason,
        "prior_sol_spend_usd": prior_spend,
        "continuation_sol_spend_usd": continuation_spend,
        "total_subject_sol_spend_usd": prior_spend + continuation_spend,
        "final_decision": asdict(outcome.final_decision),
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )

    print(f"CONTINUATION_BATCHES={continuation_batches}", flush=True)
    print(f"CONTINUATION_ANALYSES={continuation_analyses}", flush=True)
    print(f"TOTAL_ANALYSES={outcome.analyses_executed}", flush=True)
    print(f"CLOSED={outcome.closed}", flush=True)
    print(f"CLOSE_REASON={outcome.close_reason}", flush=True)
    print(f"CONTINUATION_SOL_SPEND_USD={continuation_spend:.6f}", flush=True)
    print(f"TOTAL_SUBJECT_SOL_SPEND_USD={prior_spend + continuation_spend:.6f}", flush=True)
    print(f"SUMMARY={summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
