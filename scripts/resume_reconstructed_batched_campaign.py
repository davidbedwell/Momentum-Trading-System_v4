from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile

from MTS_V4.batch_campaign_reconstruction import reconstruct_batched_campaign
from MTS_V4.batch_campaign_resume import recovered_evidence_descriptors, recovered_nexus_context
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.bootstrap import DEFAULT_MISSION, build_batch_runtime
from MTS_V4.contracts import ResearchPhase
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector


DEFAULT_PRIOR_AMD_SOL_SPEND_USD = 9.1917232


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _append_jsonl(path: Path, row: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, default=str, separators=(",", ":")) + "\n")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resume a reconstructed batched campaign exactly at its completed-batch interpretation boundary. "
            "This command performs no Analysis execution. A live run makes one INTERPRET_BATCH_RESULTS operation; "
            "the provider may make representation-repair calls only if Sol returns invalid representation."
        )
    )
    parser.add_argument("--decisions-jsonl", required=True)
    parser.add_argument("--reports-jsonl", required=True)
    parser.add_argument("--nexus-json", required=True)
    parser.add_argument("--recovered-state-dir", required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--subject-id", required=True)
    parser.add_argument("--total-sol-spend-limit-usd", type=float, default=20.0)
    parser.add_argument("--prior-sol-spend-usd", type=float, default=DEFAULT_PRIOR_AMD_SOL_SPEND_USD)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="verify the reconstructed boundary and recovered durable package store with zero Sol calls",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    state_dir = Path(args.recovered_state_dir)
    package_store_dir = state_dir / "research_packages"
    if not package_store_dir.exists():
        raise RuntimeError(f"recovered Research Package store does not exist: {package_store_dir}")
    if args.total_sol_spend_limit_usd <= 0:
        raise RuntimeError("--total-sol-spend-limit-usd must be positive")
    if args.prior_sol_spend_usd < 0:
        raise RuntimeError("--prior-sol-spend-usd cannot be negative")
    remaining_authorization = args.total_sol_spend_limit_usd - args.prior_sol_spend_usd
    if remaining_authorization <= 0:
        raise RuntimeError("no Sol authorization remains under the requested total subject ceiling")

    with tempfile.TemporaryDirectory(prefix="mts-v4-resume-verify-") as temporary:
        reconstructed = reconstruct_batched_campaign(
            decisions_jsonl=args.decisions_jsonl,
            reports_jsonl=args.reports_jsonl,
            nexus_json=args.nexus_json,
            package_store_dir=Path(temporary) / "research_packages",
            campaign_id=args.campaign_id,
            subject_id=args.subject_id,
        )

    recovered_store = JsonResearchPackageStore(package_store_dir)
    recovered_ids = tuple(recovered_store.list_ids())
    if not recovered_ids:
        raise RuntimeError("recovered Research Package store is empty")
    reconstructed_ids = sorted(
        {package.rp_id for decision in reconstructed.decisions for package in decision.research_packages}
    )
    if sorted(recovered_ids) != reconstructed_ids:
        raise RuntimeError(
            "recovered Research Package identity mismatch: "
            f"store={sorted(recovered_ids)} reconstructed={reconstructed_ids}"
        )

    print(f"SUBJECT={reconstructed.subject.subject_id}", flush=True)
    print(f"DECISIONS_REPLAYED={len(reconstructed.decisions)}", flush=True)
    print(f"REPORTS_REPLAYED={len(reconstructed.reports)}", flush=True)
    print(f"RESULTS_RECOVERED={len(reconstructed.results_by_analysis_id)}", flush=True)
    print(f"LATEST_REPORT_RECORDS={len(reconstructed.latest_report.records)}", flush=True)
    print("READY_FOR_INTERPRETATION=True", flush=True)
    print(f"PRIOR_SOL_SPEND_USD={args.prior_sol_spend_usd:.6f}", flush=True)
    print(f"TOTAL_SOL_SPEND_LIMIT_USD={args.total_sol_spend_limit_usd:.2f}", flush=True)
    print(f"REMAINING_SOL_AUTHORIZATION_USD={remaining_authorization:.6f}", flush=True)

    if args.dry_run:
        print("DRY_RUN=True", flush=True)
        print("SOL_CALLS=0", flush=True)
        print("ANALYSIS_EXECUTIONS=0", flush=True)
        return 0

    decision_path = state_dir / "resume_interpretation_decision.json"
    decision_log_path = state_dir / "resumed_batch_decisions.jsonl"
    if decision_path.exists() or (decision_log_path.exists() and decision_log_path.stat().st_size > 0):
        raise RuntimeError(
            "resume interpretation output already exists; refusing to spend again at the same boundary"
        )

    os.environ.setdefault(
        "MTS_SOL_TELEMETRY_PATH",
        str(state_dir / "resume_sol_transport_telemetry.jsonl"),
    )

    rd = SolBatchResearchDirector(
        research_package_store=recovered_store,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        required_subject_id=reconstructed.subject.subject_id,
        required_research_phase=ResearchPhase.EXPLORATION,
        sol_spend_limit_usd=remaining_authorization,
    )
    runtime = build_batch_runtime(
        rd=rd,
        mission=DEFAULT_MISSION,
        nexus_path=args.nexus_json,
    )
    evidence = recovered_evidence_descriptors(
        nexus=runtime.nexus,
        subject_id=reconstructed.subject.subject_id,
    )
    context = recovered_nexus_context(
        reconstructed=reconstructed,
        nexus=runtime.nexus,
        research_concepts=runtime.concepts.payloads(),
    )

    decision = rd.interpret_batch_results(
        mission=DEFAULT_MISSION,
        subject=reconstructed.subject,
        prior_decision=reconstructed.latest_decision,
        report=reconstructed.latest_report,
        evidence=evidence,
        available_methods=runtime.catalog.capability_payloads(),
        nexus_context=context,
    )

    recorder = BatchCampaignResearchRecorder(package_store=recovered_store)
    recorder.record_plan(
        campaign_id=args.campaign_id,
        subject=reconstructed.subject,
        decision=decision,
    )
    recorder.record_predictive_hypothesis_updates(
        decision,
        current_report=reconstructed.latest_report,
    )
    recorder.record_closures(decision)
    for finding in decision.promote_findings:
        runtime.nexus.publish_finding(finding)

    decision_payload = asdict(decision)
    decision_path.write_text(
        json.dumps(decision_payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    _append_jsonl(
        decision_log_path,
        {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "decision_sequence": len(reconstructed.decisions) + 1,
            "analyses_executed": reconstructed.analyses_executed,
            "decision": decision_payload,
            "resumed_from_completed_batch": len(reconstructed.reports),
            "analysis_executions_during_resume": 0,
        },
    )

    spend = rd.sol_spend_snapshot()
    resumed_spend = 0.0 if spend is None else spend.actual_spend_usd
    total_spend = args.prior_sol_spend_usd + resumed_spend
    print("RESUME_INTERPRETATION_ACCEPTED=True", flush=True)
    print("ANALYSIS_EXECUTIONS=0", flush=True)
    print(f"RESUME_SOL_SPEND_USD={resumed_spend:.6f}", flush=True)
    print(f"TOTAL_SUBJECT_SOL_SPEND_USD={total_spend:.6f}", flush=True)
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
    print(f"DECISION_LOG={decision_log_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
