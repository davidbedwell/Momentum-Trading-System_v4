from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile

from MTS_V4.batch_campaign_reconstruction import reconstruct_batched_campaign
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.bootstrap import build_batch_runtime
from MTS_V4.contracts import ResearchPhase
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.retrospective_recovery import SolRetrospectiveRecoveryResearchDirector
from MTS_V4.retrospective_resume import interpret_reconstructed_retrospective_boundary


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


def _prior_sol_spend(path: Path) -> float:
    if not path.is_file():
        raise RuntimeError(f"missing prior Sol telemetry: {path}")
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
    if not cumulative:
        raise RuntimeError("prior Sol telemetry contains no completed-call cumulative spend")
    return max(cumulative)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resume an interrupted retrospective recovery exactly at a completed-batch interpretation boundary. "
            "The resume boundary performs zero Analysis executions before returning the already-completed batch to Sol."
        )
    )
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--total-sol-spend-limit-usd", type=float, default=20.0)
    parser.add_argument("--dry-run", action="store_true")
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
    telemetry_path = state_dir / "sol_transport_telemetry.jsonl"
    for path in (decisions_path, reports_path, nexus_path, context_path):
        if not path.is_file():
            raise RuntimeError(f"required recovery artifact is missing: {path}")
    if not package_store_dir.is_dir():
        raise RuntimeError(f"recovered Research Package store does not exist: {package_store_dir}")

    retrospective_context = json.loads(context_path.read_text(encoding="utf-8"))
    campaign_id = state_dir.name
    subject_ids = []
    document = json.loads(nexus_path.read_text(encoding="utf-8"))
    for raw in document.get("subjects", []):
        value = raw.get("subject_id")
        if isinstance(value, str):
            subject_ids.append(value)
    subject_ids = sorted(set(subject_ids))
    if len(subject_ids) != 1:
        raise RuntimeError(f"expected exactly one Nexus subject, found: {subject_ids}")
    subject_id = subject_ids[0]

    with tempfile.TemporaryDirectory(prefix="mts-v4-retro-resume-verify-") as temporary:
        reconstructed = reconstruct_batched_campaign(
            decisions_jsonl=decisions_path,
            reports_jsonl=reports_path,
            nexus_json=nexus_path,
            package_store_dir=Path(temporary) / "research_packages",
            campaign_id=campaign_id,
            subject_id=subject_id,
        )

    recovered_store = JsonResearchPackageStore(package_store_dir)
    reconstructed_ids = sorted(
        {package.rp_id for decision in reconstructed.decisions for package in decision.research_packages}
    )
    recovered_ids = sorted(recovered_store.list_ids())
    if recovered_ids != reconstructed_ids:
        raise RuntimeError(
            "recovered Research Package identity mismatch: "
            f"store={recovered_ids} reconstructed={reconstructed_ids}"
        )

    prior_spend = _prior_sol_spend(telemetry_path)
    remaining = args.total_sol_spend_limit_usd - prior_spend
    if remaining <= 0:
        raise RuntimeError("no Sol authorization remains under the requested total subject ceiling")

    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"CAMPAIGN_ID={campaign_id}", flush=True)
    print(f"SUBJECT={subject_id}", flush=True)
    print(f"DECISIONS_REPLAYED={len(reconstructed.decisions)}", flush=True)
    print(f"REPORTS_REPLAYED={len(reconstructed.reports)}", flush=True)
    print(f"RESULTS_RECOVERED={len(reconstructed.results_by_analysis_id)}", flush=True)
    print(f"LATEST_REPORT_RECORDS={len(reconstructed.latest_report.records)}", flush=True)
    print(f"PRIOR_SOL_SPEND_USD={prior_spend:.6f}", flush=True)
    print(f"REMAINING_SOL_AUTHORIZATION_USD={remaining:.6f}", flush=True)
    print("ANALYSIS_EXECUTIONS_BEFORE_INTERPRETATION=0", flush=True)

    if args.dry_run:
        print("DRY_RUN=True", flush=True)
        print("SOL_CALLS=0", flush=True)
        return 0

    decision_path = state_dir / "resume_interpretation_decision.json"
    decision_log_path = state_dir / "resumed_batch_decisions.jsonl"
    if decision_path.exists() or (decision_log_path.exists() and decision_log_path.stat().st_size > 0):
        raise RuntimeError("resume output already exists; refusing to spend again at the same boundary")

    os.environ["MTS_SOL_TELEMETRY_PATH"] = str(state_dir / "resume_sol_transport_telemetry.jsonl")
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
    runtime = build_batch_runtime(rd=rd, mission=RETROSPECTIVE_MISSION, nexus_path=nexus_path)

    decision = interpret_reconstructed_retrospective_boundary(
        rd=rd,
        reconstructed=reconstructed,
        nexus=runtime.nexus,
        mission=RETROSPECTIVE_MISSION,
        available_methods=runtime.catalog.capability_payloads(),
        research_concepts=runtime.concepts.payloads(),
    )

    recorder = BatchCampaignResearchRecorder(package_store=recovered_store)
    recorder.record_plan(campaign_id=campaign_id, subject=reconstructed.subject, decision=decision)
    recorder.record_predictive_hypothesis_updates(
        decision,
        current_report=reconstructed.latest_report,
    )
    recorder.record_closures(decision)
    for finding in decision.promote_findings:
        runtime.nexus.publish_finding(finding)

    payload = asdict(decision)
    decision_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    _append_jsonl(
        decision_log_path,
        {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "decision_sequence": len(reconstructed.decisions) + 1,
            "analyses_executed": reconstructed.analyses_executed,
            "analysis_executions_before_interpretation": 0,
            "resumed_from_completed_batch": len(reconstructed.reports),
            "decision": payload,
        },
    )

    spend = rd.sol_spend_snapshot()
    resume_spend = 0.0 if spend is None else spend.actual_spend_usd
    print("RESUME_INTERPRETATION_ACCEPTED=True", flush=True)
    print("ANALYSIS_EXECUTIONS_BEFORE_INTERPRETATION=0", flush=True)
    print(f"RESUME_SOL_SPEND_USD={resume_spend:.6f}", flush=True)
    print(f"TOTAL_SUBJECT_SOL_SPEND_USD={prior_spend + resume_spend:.6f}", flush=True)
    print(f"CONTINUE_RESEARCH={decision.continue_research}", flush=True)
    print(f"RESEARCH_PACKAGES={len(decision.research_packages)}", flush=True)
    print(
        "ANALYSIS_SPECIFICATIONS="
        f"{sum(len(package.analyses) for package in decision.research_packages)}",
        flush=True,
    )
    print(f"PROMOTE_FINDINGS={len(decision.promote_findings)}", flush=True)
    print(f"RP_CLOSURES={len(decision.rp_closures)}", flush=True)
    print(f"DECISION_JSON={decision_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
