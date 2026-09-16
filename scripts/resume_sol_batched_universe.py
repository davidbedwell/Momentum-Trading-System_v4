from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile

from MTS_V4.batch_campaign_continuation import ContinuationBaseline
from MTS_V4.batch_campaign_reconstruction import reconstruct_batched_campaign
from MTS_V4.batch_rd_codec import BatchResearchDecisionCodec
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.bootstrap import build_batch_runtime
from MTS_V4.control_readiness import require_ready_control
from MTS_V4.derived_market_evidence import derived_market_evidence_descriptor
from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore
from MTS_V4.qwen_shadow_gate import ReplayCapturingSubjectContextSolBatchResearchDirector
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_spend_guard import SolSpendAuthorizationRequired
from MTS_V4.subject_scientific_context import load_subject_scientific_context
from MTS_V4.universe_scientific_partition import ScientificCohort, load_frozen_partition

from resume_fresh_subject import (
    CrossSubjectRecoveredBatchCampaignContinuation,
    _decision_fingerprint,
    _load_analysis_checkpoints,
    _load_latest_continuation_decision,
    _recover_campaign_id,
    _telemetry_spend,
)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _append_jsonl(path: Path, payload) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")) + "\n")


def _decode_decision(path: Path):
    return BatchResearchDecisionCodec.decode(
        json.dumps(json.loads(path.read_text(encoding="utf-8")), sort_keys=True)
    )


def _query(raw: dict[str, object]) -> DerivedMarketQuery:
    return DerivedMarketQuery(
        universe_id=str(raw["universe_id"]),
        feature_set_id=str(raw["feature_set_id"]),
        feature_set_version=str(raw["feature_set_version"]),
        start_date=raw.get("start_date"),
        end_date=raw.get("end_date"),
        security_ids=tuple(str(value) for value in raw.get("security_ids", ())),
        feature_columns=tuple(str(value) for value in raw.get("feature_columns", ())),
        include_ineligible=bool(raw.get("include_ineligible", False)),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resume a governed Sol universe control at its durable completed-batch boundary."
    )
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--derived-market-root", required=True)
    parser.add_argument("--scientific-partition-manifest", required=True)
    parser.add_argument("--control-readiness-report", required=True)
    parser.add_argument("--root", default="/home/ubuntu")
    parser.add_argument("--total-sol-spend-limit-usd", required=True, type=float)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    state_dir = Path(args.state_dir).expanduser().resolve()
    if not state_dir.is_dir():
        raise RuntimeError(f"state directory does not exist: {state_dir}")

    context_path = state_dir / "universe_scientific_context.json"
    decisions_path = state_dir / "batch_decisions.jsonl"
    reports_path = state_dir / "batch_reports.jsonl"
    nexus_path = state_dir / "research_nexus.json"
    package_dir = state_dir / "research_packages"
    original_telemetry = state_dir / "sol_transport_telemetry.jsonl"
    resume_telemetry = state_dir / "resume_sol_transport_telemetry.jsonl"
    for required in (context_path, decisions_path, reports_path, nexus_path, original_telemetry):
        if not required.is_file():
            raise RuntimeError(f"required universe resume artifact is missing: {required}")
    if not package_dir.is_dir():
        raise RuntimeError(f"Research Package store is missing: {package_dir}")

    context = json.loads(context_path.read_text(encoding="utf-8"))
    control_id = str(context.get("calibration_control_id", "")).strip()
    if not control_id:
        raise RuntimeError("state is not a calibration control")
    require_ready_control(args.control_readiness_report, control_id)

    primary_query = _query(context["primary_query"])
    outcome_query = _query(context["outcome_query"])
    if primary_query.universe_id != outcome_query.universe_id:
        raise RuntimeError("recorded primary/outcome universe mismatch")
    partition = load_frozen_partition(Path(args.scientific_partition_manifest).expanduser().resolve())
    if partition.universe_id != primary_query.universe_id:
        raise RuntimeError("scientific partition universe mismatch")
    if tuple(outcome_query.security_ids) != partition.members(ScientificCohort.DISCOVERY):
        raise RuntimeError("recorded outcome query is not the exact frozen DISCOVERY cohort")
    recorded_partition = context.get("scientific_partition")
    if not isinstance(recorded_partition, dict) or recorded_partition.get("partition_id") != partition.partition_id:
        raise RuntimeError("recorded scientific partition identity mismatch")
    if context.get("verification_cohorts_exposed") is not False:
        raise RuntimeError("verification exposure invariant is not false")

    subject_id = str(context["active_scope_id"])
    campaign_id = _recover_campaign_id(package_dir, subject_id=subject_id)
    with tempfile.TemporaryDirectory(prefix="mts-v4-universe-resume-verify-") as temporary:
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
        raise RuntimeError("no Sol authorization remains under the requested total control ceiling")

    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"CONTROL_ID={control_id}", flush=True)
    print(f"DECISIONS_RECONSTRUCTED={len(reconstructed.decisions)}", flush=True)
    print(f"BATCHES_RECONSTRUCTED={len(reconstructed.reports)}", flush=True)
    print(f"RESULTS_RECOVERED={len(reconstructed.results_by_analysis_id)}", flush=True)
    print(f"PRIOR_SOL_SPEND_USD={prior_spend:.6f}", flush=True)
    print(f"TOTAL_SOL_SPEND_LIMIT_USD={args.total_sol_spend_limit_usd:.6f}", flush=True)
    print(f"REMAINING_SOL_AUTHORIZATION_USD={remaining:.6f}", flush=True)
    print("PRIOR_ANALYSIS_REEXECUTION_ALLOWED=False", flush=True)
    if args.dry_run:
        print("DRY_RUN=True", flush=True)
        print("SOL_CALLS=0", flush=True)
        return 0

    root = Path(args.root).expanduser().resolve()
    scientific_context = load_subject_scientific_context(
        root, active_subject_id=subject_id, include_same_subject_prior_science=True
    )
    recorded_memory = str(context.get("canonical_memory_source", ""))
    if str(scientific_context.memory_selection.source_path) != recorded_memory:
        raise RuntimeError("canonical scientific-memory source changed since the original control")
    frontier = scientific_context.memory_selection.store.frontier()
    if (frontier.version if frontier is not None else 0) != int(context.get("canonical_memory_frontier_version", 0)):
        raise RuntimeError("canonical scientific-memory frontier changed since the original control")

    os.environ["MTS_SOL_TELEMETRY_PATH"] = str(resume_telemetry)
    recovered_store = JsonResearchPackageStore(package_dir)
    rd = ReplayCapturingSubjectContextSolBatchResearchDirector(
        research_package_store=recovered_store,
        prior_subject_scientific_context=scientific_context.prior_subject_science,
        same_subject_prior_scientific_context=scientific_context.same_subject_prior_science,
        replay_capture_path=state_dir / "resume_sol_replay_envelopes.jsonl",
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        required_subject_id=subject_id,
        required_research_phase=reconstructed.latest_decision.research_packages[0].analyses[0].research_phase,
        sol_spend_limit_usd=remaining,
        human_spend_authorization_callback=None,
    )
    mission = str(context["mission"])
    runtime = build_batch_runtime(
        rd=rd,
        mission=mission,
        nexus_path=nexus_path,
        derived_market_root=Path(args.derived_market_root).expanduser().resolve(),
        scientific_memory=scientific_context.memory_selection.store,
    )
    evidence = (
        derived_market_evidence_descriptor(
            store=runtime.nexus.derived_market_store, cache=runtime.cache,
            subject=reconstructed.subject, query=primary_query, allow_future_outcomes=False,
        ),
        derived_market_evidence_descriptor(
            store=runtime.nexus.derived_market_store, cache=runtime.cache,
            subject=reconstructed.subject, query=outcome_query, allow_future_outcomes=True,
        ),
    )

    decision_path = state_dir / "universe_resume_decision.json"
    pending_path = state_dir / "universe_resume_decision.pending.json"
    decision_log = state_dir / "resumed_batch_decisions.jsonl"
    report_log = state_dir / "resumed_batch_reports.jsonl"
    checkpoint_path = state_dir / "resume_analysis_checkpoints.jsonl"
    summary_path = state_dir / "run_summary.json"
    recorder = BatchCampaignResearchRecorder(package_store=recovered_store)

    latest_continuation = _load_latest_continuation_decision(decision_log)
    if latest_continuation is not None:
        active_sequence, decision = latest_continuation
    elif decision_path.is_file():
        active_sequence = len(reconstructed.decisions) + 1
        decision = _decode_decision(decision_path)
    elif pending_path.is_file():
        active_sequence = len(reconstructed.decisions) + 1
        decision = _decode_decision(pending_path)
    else:
        active_sequence = len(reconstructed.decisions) + 1
        decision = rd.interpret_batch_results(
            mission=mission,
            subject=reconstructed.subject,
            prior_decision=reconstructed.latest_decision,
            report=reconstructed.latest_report,
            evidence=evidence,
            available_methods=runtime.catalog.capability_payloads(),
            nexus_context=runtime.orchestrator._nexus_context(
                subject_id, reconstructed.results_by_analysis_id
            ),
        )
        pending_path.write_text(json.dumps(asdict(decision), indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    recorder.record_plan(campaign_id=campaign_id, subject=reconstructed.subject, decision=decision)
    recorder.record_predictive_hypothesis_updates(decision, current_report=reconstructed.latest_report)
    recorder.record_closures(decision)
    for finding in decision.promote_findings:
        runtime.nexus.publish_finding(finding)
    decision_path.write_text(json.dumps(asdict(decision), indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    pending_path.unlink(missing_ok=True)

    fingerprint = _decision_fingerprint(decision)
    accepted_ids = {
        analysis.analysis_id
        for package in decision.research_packages
        for analysis in package.analyses
    }
    checkpoints = _load_analysis_checkpoints(
        checkpoint_path,
        decision_fingerprint=fingerprint,
        decision_sequence=active_sequence,
        accepted_analysis_ids=accepted_ids,
    )
    active = {
        "sequence": active_sequence,
        "fingerprint": fingerprint,
        "report": reconstructed.latest_report,
    }

    continuation = CrossSubjectRecoveredBatchCampaignContinuation(
        scientific_memory=scientific_context.memory_selection.store,
        mission=mission, rd=rd, validator=runtime.validator, analysis=runtime.analysis,
        nexus=runtime.nexus, cache=runtime.cache,
        available_methods=runtime.catalog.capability_payloads(),
        research_concepts=runtime.concepts.payloads(),
    )

    def on_decision(item, decisions, analyses):
        recorder.record_plan(campaign_id=campaign_id, subject=reconstructed.subject, decision=item)
        recorder.record_predictive_hypothesis_updates(item, current_report=active["report"])
        recorder.record_closures(item)
        _append_jsonl(decision_log, {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "decision_sequence": decisions, "analyses_executed": analyses,
            "decision": asdict(item),
        })
        active["sequence"] = decisions
        active["fingerprint"] = _decision_fingerprint(item)

    def on_report(report, decisions, analyses):
        _append_jsonl(report_log, {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "decision_sequence": decisions, "analyses_executed": analyses,
            "report": asdict(report),
        })
        active["report"] = report

    def on_checkpoint(record, decisions, analyses):
        _append_jsonl(checkpoint_path, {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "decision_sequence": active["sequence"],
            "decision_fingerprint": active["fingerprint"],
            "record": asdict(record),
        })

    try:
        outcome = continuation.continue_from_decision(
            subject=reconstructed.subject,
            evidence=evidence,
            initial_decision=decision,
            prior_results_by_analysis_id=reconstructed.results_by_analysis_id,
            baseline=ContinuationBaseline(
                decisions=len(reconstructed.decisions) + 1,
                batches_executed=len(reconstructed.reports),
                analyses_executed=reconstructed.analyses_executed,
                findings_promoted=(
                    reconstructed.findings_promoted + len(decision.promote_findings)
                ),
            ),
            decision_callback=on_decision,
            report_callback=on_report,
            accepted_request_callback=lambda request: recorder.record_accepted_request(
                campaign_id=campaign_id, subject=reconstructed.subject, request=request
            ),
            checkpointed_records_by_analysis_id=checkpoints,
            analysis_checkpoint_callback=on_checkpoint,
        )
    except SolSpendAuthorizationRequired as exc:
        payload = asdict(exc.snapshot)
        payload["prior_sol_spend_usd"] = prior_spend
        payload["total_actual_spend_usd"] = prior_spend + exc.snapshot.actual_spend_usd
        (state_dir / "resume_sol_spend_authorization_required.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print("HUMAN_SOL_SPEND_AUTHORIZATION_REQUIRED=True", flush=True)
        return 2

    resumed_spend = (rd.sol_spend_snapshot().actual_spend_usd if rd.sol_spend_snapshot() else 0.0)
    total_spend = prior_spend + resumed_spend
    summary = {
        "campaign_id": campaign_id,
        "scope_id": subject_id,
        "universe_id": primary_query.universe_id,
        "calibration_control_id": control_id,
        "decisions": outcome.decisions,
        "batches_executed": outcome.batches_executed,
        "analyses_executed": outcome.analyses_executed,
        "findings_promoted": outcome.findings_promoted,
        "closed": outcome.closed,
        "close_reason": outcome.close_reason,
        "sol_spend": {
            "authorized_spend_usd": args.total_sol_spend_limit_usd,
            "actual_spend_usd": total_spend,
            "prior_spend_usd": prior_spend,
            "resumed_spend_usd": resumed_spend,
        },
        "qwen_replay_capture": str(state_dir / "resume_sol_replay_envelopes.jsonl"),
        "resumed": True,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(f"CLOSED={outcome.closed}", flush=True)
    print(f"TOTAL_SOL_SPEND_USD={total_spend:.6f}", flush=True)
    print(f"RUN_SUMMARY={summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
