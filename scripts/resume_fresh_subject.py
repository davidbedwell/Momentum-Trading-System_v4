from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Mapping

from MTS_V4.batch_campaign_continuation import (
    ContinuationBaseline,
    RecoveredBatchCampaignContinuation,
)
from MTS_V4.batch_campaign_reconstruction import (
    decode_batch_execution_report,
    reconstruct_batched_campaign,
)
from MTS_V4.batch_campaign_resume import (
    recovered_evidence_descriptors,
    recovered_nexus_context,
)
from MTS_V4.batch_contracts import BatchExecutionReport
from MTS_V4.batch_rd_codec import BatchResearchDecisionCodec
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.bootstrap import DEFAULT_MISSION, build_batch_runtime
from MTS_V4.contracts import AnalysisResult, ResearchPhase
from MTS_V4.cross_subject_context import build_cross_subject_context
from MTS_V4.cross_subject_memory import CrossSubjectScientificMemory
from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_spend_guard import SolSpendAuthorizationRequired
from MTS_V4.subject_scientific_context import SubjectContextSolBatchResearchDirector


SUBJECT_MISSION = DEFAULT_MISSION + (
    " The AI Research Director receives canonical cross-subject scientific memory/frontier and compact durable "
    "prior-subject scientific findings as nonbinding context. Actively consider transferability, contradictions, "
    "conditional structure, and falsifiable generalization pathways when scientifically useful, but do not assume "
    "that any prior relationship generalizes. Deterministic code does not choose variables, methods, thresholds, "
    "normalizations, horizons, hypotheses, or generalizations."
)


class CrossSubjectRecoveredBatchCampaignContinuation(
    RecoveredBatchCampaignContinuation
):
    def __init__(
        self,
        *,
        scientific_memory: CrossSubjectScientificMemory,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._scientific_memory = scientific_memory

    def _nexus_context(
        self,
        subject_id: str,
        results_by_analysis_id: Mapping[str, AnalysisResult],
    ) -> Mapping[str, object]:
        context = dict(
            super()._nexus_context(subject_id, results_by_analysis_id)
        )
        context["cross_subject_scientific_memory"] = build_cross_subject_context(
            self._scientific_memory,
            active_subject_id=subject_id,
        )
        return context


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _append_jsonl(path: Path, row: Mapping[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                dict(row),
                sort_keys=True,
                default=str,
                separators=(",", ":"),
            )
            + "\n"
        )


def _telemetry_spend(path: Path) -> float:
    if not path.is_file():
        return 0.0

    values: list[float] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("event") != "SOL_CALL_COMPLETE":
            continue
        value = row.get("estimated_cumulative_sol_spend_usd")
        if value is not None:
            values.append(float(value))

    return max(values) if values else 0.0


def _decode_decision(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    return BatchResearchDecisionCodec.decode(
        json.dumps(raw, sort_keys=True, default=str)
    )


def _direct_evidence_ids(decision) -> set[str]:
    return {
        ref.evidence_id
        for package in decision.research_packages
        for analysis in package.analyses
        for ref in analysis.inputs
        if ref.evidence_id is not None
    }


def _decision_fingerprint(decision) -> str:
    payload = json.dumps(
        asdict(decision),
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _load_analysis_checkpoints(
    path: Path,
    *,
    decision_fingerprint: str,
    decision_sequence: int,
    accepted_analysis_ids: set[str],
    allow_legacy_fingerprint_mismatch: bool = False,
):
    if not path.is_file():
        return {}

    checkpoints = {}
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        row = json.loads(line)

        recorded_sequence = row.get("decision_sequence")
        raw_record = row.get("record")
        if not isinstance(raw_record, dict):
            raise RuntimeError(
                f"continuation checkpoint lacks record object at {path}:{line_number}"
            )

        report = decode_batch_execution_report(
            {"records": [raw_record]}
        )
        if len(report.records) != 1:
            raise RuntimeError(
                f"invalid continuation checkpoint at {path}:{line_number}"
            )

        record = report.records[0]

        if recorded_sequence != decision_sequence:
            continue

        if record.analysis_id not in accepted_analysis_ids:
            raise RuntimeError(
                "continuation checkpoint analysis_id is not a member of "
                f"decision sequence {decision_sequence}: {record.analysis_id}"
            )

        recorded_fingerprint = row.get("decision_fingerprint")
        if (
            recorded_fingerprint != decision_fingerprint
            and not allow_legacy_fingerprint_mismatch
        ):
            raise RuntimeError(
                "continuation checkpoint decision fingerprint mismatch at "
                f"{path}:{line_number}"
            )

        prior = checkpoints.get(record.analysis_id)

        if prior is not None and prior != record:
            raise RuntimeError(
                "conflicting continuation checkpoints for analysis_id: "
                f"{record.analysis_id}"
            )

        checkpoints[record.analysis_id] = record

    return checkpoints


def _load_latest_continuation_decision(path: Path):
    if not path.is_file():
        return None

    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        return None

    latest = rows[-1]
    sequence = latest.get("decision_sequence")
    raw = latest.get("decision")

    if not isinstance(sequence, int) or not isinstance(raw, dict):
        raise RuntimeError(
            "latest continuation decision record is malformed"
        )

    decision = BatchResearchDecisionCodec.decode(
        json.dumps(raw, sort_keys=True, default=str)
    )
    return sequence, decision


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resume an interrupted FRESH_FULL_SUBJECT campaign at its durable "
            "completed-batch boundary without re-executing completed Analysis."
        )
    )
    parser.add_argument("--state-dir", required=True)
    parser.add_argument(
        "--total-sol-spend-limit-usd",
        type=float,
        default=20.0,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--interpret-only",
        action="store_true",
        help=(
            "Return the completed batch to Sol and durably save its next decision "
            "without executing newly authorized Analysis."
        ),
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
    scientific_context_path = state_dir / "subject_scientific_context.json"

    original_telemetry = state_dir / "sol_transport_telemetry.jsonl"
    resume_telemetry = state_dir / "resume_sol_transport_telemetry.jsonl"
    continuation_telemetry = (
        state_dir / "continuation_sol_transport_telemetry.jsonl"
    )

    resume_decision_path = state_dir / "resume_interpretation_decision.json"
    resume_decision_log = state_dir / "resumed_batch_decisions.jsonl"
    continuation_decision_log = (
        state_dir / "continuation_batch_decisions.jsonl"
    )
    continuation_report_log = (
        state_dir / "continuation_batch_reports.jsonl"
    )
    summary_path = state_dir / "resume_summary.json"

    for required in (
        decisions_path,
        reports_path,
        nexus_path,
        scientific_context_path,
        original_telemetry,
    ):
        if not required.is_file():
            raise RuntimeError(
                f"required fresh-subject resume artifact is missing: {required}"
            )

    if not package_store_dir.is_dir():
        raise RuntimeError(
            f"Research Package store is missing: {package_store_dir}"
        )

    scientific_context = json.loads(
        scientific_context_path.read_text(encoding="utf-8")
    )

    if scientific_context.get("mode") != "FRESH_FULL_SUBJECT":
        raise RuntimeError(
            "resume_fresh_subject may only resume FRESH_FULL_SUBJECT state"
        )

    subject_id = scientific_context.get("active_subject_id")
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise RuntimeError(
            "subject_scientific_context lacks active_subject_id"
        )

    memory_source = scientific_context.get("canonical_memory_source")
    if not isinstance(memory_source, str) or not memory_source.strip():
        raise RuntimeError(
            "subject_scientific_context lacks canonical_memory_source"
        )

    memory_path = Path(memory_source).expanduser().resolve()
    if not memory_path.is_file():
        raise RuntimeError(
            f"recorded canonical memory snapshot is missing: {memory_path}"
        )

    prior_subject_context = scientific_context.get(
        "prior_subject_scientific_context"
    )
    if not isinstance(prior_subject_context, Mapping):
        raise RuntimeError(
            "subject_scientific_context lacks exact prior-subject science"
        )

    mission = scientific_context.get("mission", SUBJECT_MISSION)
    if not isinstance(mission, str) or not mission.strip():
        raise RuntimeError("subject mission is invalid")

    scientific_memory = JsonCrossSubjectScientificMemoryStore(memory_path)
    campaign_id = state_dir.name

    nexus_document = json.loads(
        nexus_path.read_text(encoding="utf-8")
    )
    nexus_subject_ids = sorted(
        {
            str(item["subject_id"])
            for item in nexus_document.get("subjects", [])
            if isinstance(item, dict)
            and isinstance(item.get("subject_id"), str)
        }
    )

    if nexus_subject_ids != [subject_id]:
        raise RuntimeError(
            "Nexus subject mismatch: "
            f"context={subject_id} nexus={nexus_subject_ids}"
        )

    # The durable Nexus may legitimately contain results produced by
    # continuation batches after the original fresh-subject history broke.
    # Preserve the strict reconstruction invariant by verifying the original
    # decision/report history against a temporary Nexus view containing only
    # result metadata represented by those original reports. The durable Nexus
    # itself is never modified.
    original_report_result_ids: set[str] = set()

    for line_number, line in enumerate(
        reports_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        report_row = json.loads(line)
        raw_report = report_row.get("report", report_row)
        report = decode_batch_execution_report(raw_report)

        for record in report.records:
            if record.result is not None:
                original_report_result_ids.add(
                    record.result.result_id
                )

    durable_result_metadata = nexus_document.get(
        "analysis_result_metadata",
        [],
    )
    if not isinstance(durable_result_metadata, list):
        raise RuntimeError(
            "Nexus analysis_result_metadata is not a list"
        )

    durable_result_ids = {
        item.get("result_id")
        for item in durable_result_metadata
        if isinstance(item, dict)
        and isinstance(item.get("result_id"), str)
    }

    missing_original_result_ids = sorted(
        original_report_result_ids - durable_result_ids
    )
    if missing_original_result_ids:
        raise RuntimeError(
            "durable Nexus is missing original fresh-subject result_id(s): "
            + ", ".join(missing_original_result_ids)
        )

    verification_nexus_document = dict(nexus_document)
    verification_nexus_document["analysis_result_metadata"] = [
        item
        for item in durable_result_metadata
        if isinstance(item, dict)
        and item.get("result_id") in original_report_result_ids
    ]

    with tempfile.TemporaryDirectory(
        prefix="mts-v4-fresh-resume-verify-"
    ) as temporary:
        temporary_path = Path(temporary)
        verification_nexus_path = (
            temporary_path / "original_history_nexus.json"
        )
        verification_nexus_path.write_text(
            json.dumps(
                verification_nexus_document,
                indent=2,
                sort_keys=True,
                default=str,
            )
            + "\n",
            encoding="utf-8",
        )

        reconstructed = reconstruct_batched_campaign(
            decisions_jsonl=decisions_path,
            reports_jsonl=reports_path,
            nexus_json=verification_nexus_path,
            package_store_dir=(
                temporary_path / "research_packages"
            ),
            campaign_id=campaign_id,
            subject_id=subject_id,
        )

    recovered_store = JsonResearchPackageStore(package_store_dir)

    reconstructed_ids = {
        package.rp_id
        for reconstructed_decision in reconstructed.decisions
        for package in reconstructed_decision.research_packages
    }

    resumed_ids: set[str] = set()
    if resume_decision_path.is_file():
        recorded_resume_decision = _decode_decision(resume_decision_path)
        resumed_ids = {
            package.rp_id
            for package in recorded_resume_decision.research_packages
        }

    expected_durable_ids = sorted(reconstructed_ids | resumed_ids)
    durable_ids = sorted(recovered_store.list_ids())

    if durable_ids != expected_durable_ids:
        raise RuntimeError(
            "Research Package identity mismatch: "
            f"durable={durable_ids} expected={expected_durable_ids}"
        )

    analysis_checkpoint_path = (
        state_dir / "continuation_analysis_checkpoints.jsonl"
    )

    recorded_resume_decision = None
    recorded_resume_decision_fingerprint = None
    checkpointed_records_by_analysis_id = {}

    active_decision_sequence = None

    if resume_decision_path.is_file():
        recorded_resume_decision = _decode_decision(
            resume_decision_path
        )
        active_decision_sequence = len(reconstructed.decisions) + 1

        latest_continuation = _load_latest_continuation_decision(
            continuation_decision_log
        )
        if latest_continuation is not None:
            (
                active_decision_sequence,
                recorded_resume_decision,
            ) = latest_continuation

        recorded_resume_decision_fingerprint = (
            _decision_fingerprint(recorded_resume_decision)
        )
        active_analysis_ids = {
            analysis.analysis_id
            for package in recorded_resume_decision.research_packages
            for analysis in package.analyses
        }
        checkpointed_records_by_analysis_id = (
            _load_analysis_checkpoints(
                analysis_checkpoint_path,
                decision_fingerprint=(
                    recorded_resume_decision_fingerprint
                ),
                decision_sequence=active_decision_sequence,
                accepted_analysis_ids=active_analysis_ids,
            )
        )

    original_spend = _telemetry_spend(original_telemetry)
    prior_resume_spend = _telemetry_spend(resume_telemetry)
    prior_continuation_spend = _telemetry_spend(
        continuation_telemetry
    )
    prior_total_spend = (
        original_spend
        + prior_resume_spend
        + prior_continuation_spend
    )

    remaining = (
        args.total_sol_spend_limit_usd - prior_total_spend
    )
    if remaining <= 0:
        raise RuntimeError(
            "no Sol authorization remains under the requested "
            "total subject ceiling"
        )

    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"CAMPAIGN_ID={campaign_id}", flush=True)
    print(f"SUBJECT={subject_id}", flush=True)
    print("MODE=FRESH_FULL_SUBJECT_RESUME", flush=True)
    print(
        f"DECISIONS_RECONSTRUCTED={len(reconstructed.decisions)}",
        flush=True,
    )
    print(
        f"BATCHES_RECONSTRUCTED={len(reconstructed.reports)}",
        flush=True,
    )
    print(
        f"RESULTS_RECOVERED={len(reconstructed.results_by_analysis_id)}",
        flush=True,
    )
    print(
        f"LATEST_REPORT_RECORDS={len(reconstructed.latest_report.records)}",
        flush=True,
    )
    print(
        f"ORIGINAL_SOL_SPEND_USD={original_spend:.6f}",
        flush=True,
    )
    print(
        f"PRIOR_TOTAL_SOL_SPEND_USD={prior_total_spend:.6f}",
        flush=True,
    )
    print(
        f"REMAINING_SOL_AUTHORIZATION_USD={remaining:.6f}",
        flush=True,
    )
    print(
        f"CANONICAL_MEMORY_SOURCE={scientific_memory.path}",
        flush=True,
    )
    print("EXACT_PRIOR_SUBJECT_CONTEXT_RESTORED=True", flush=True)
    print("PRIOR_ANALYSIS_REEXECUTION_ALLOWED=False", flush=True)
    print("ANALYSIS_EXECUTIONS_BEFORE_INTERPRETATION=0", flush=True)

    if args.dry_run:
        if recorded_resume_decision is not None:
            requested_ids = {
                analysis.analysis_id
                for package in recorded_resume_decision.research_packages
                for analysis in package.analyses
            }
            checkpoint_ids = set(
                checkpointed_records_by_analysis_id
            )
            unexpected = sorted(checkpoint_ids - requested_ids)
            if unexpected:
                raise RuntimeError(
                    "checkpointed analysis_id(s) are not members of "
                    "the accepted resume decision: "
                    + ", ".join(unexpected)
                )

            completed_checkpoint_ids = sorted(
                checkpoint_ids
            )
            pending_ids = sorted(
                requested_ids - checkpoint_ids
            )

            print("RESUME_DECISION_PRESENT=True", flush=True)
            print(
                "RESUME_DECISION_FINGERPRINT="
                f"{recorded_resume_decision_fingerprint}",
                flush=True,
            )
            print(
                "RESUMED_ANALYSIS_SPECIFICATIONS="
                f"{len(requested_ids)}",
                flush=True,
            )
            print(
                "CHECKPOINTED_CONTINUATION_ANALYSES="
                f"{len(completed_checkpoint_ids)}",
                flush=True,
            )
            print(
                "PENDING_CONTINUATION_ANALYSES="
                f"{len(pending_ids)}",
                flush=True,
            )
            if completed_checkpoint_ids:
                print(
                    "CHECKPOINTED_ANALYSIS_IDS="
                    + ",".join(completed_checkpoint_ids),
                    flush=True,
                )
            if pending_ids:
                print(
                    "PENDING_ANALYSIS_IDS="
                    + ",".join(pending_ids),
                    flush=True,
                )
        else:
            print("RESUME_DECISION_PRESENT=False", flush=True)

        print("DRY_RUN=True", flush=True)
        print("SOL_CALLS=0", flush=True)
        print("INTAKE_CALLS=0", flush=True)
        print("ANALYSIS_EXECUTIONS=0", flush=True)
        return 0

    if summary_path.exists():
        raise RuntimeError(
            "resume summary already exists; refusing to rerun a completed fresh-subject resume"
        )

    if resume_decision_path.exists():
        decision = recorded_resume_decision
        print("RESUME_DECISION_REUSED=True", flush=True)
        print(
            f"ACTIVE_CONTINUATION_DECISION_SEQUENCE={active_decision_sequence}",
            flush=True,
        )
        print("RESUME_INTERPRETATION_SOL_CALLS=0", flush=True)
    else:
        os.environ["MTS_SOL_TELEMETRY_PATH"] = str(resume_telemetry)

        rd = SubjectContextSolBatchResearchDirector(
            prior_subject_scientific_context=prior_subject_context,
            research_package_store=recovered_store,
            base_url=_required_env("MTS_SOL_BASE_URL"),
            model=_required_env("MTS_SOL_MODEL"),
            api_key=_required_env("MTS_SOL_API_KEY"),
            timeout_seconds=int(
                os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")
            ),
            required_subject_id=subject_id,
            required_research_phase=ResearchPhase.EXPLORATION,
            sol_spend_limit_usd=remaining,
        )

        runtime = build_batch_runtime(
            rd=rd,
            mission=mission,
            nexus_path=nexus_path,
            scientific_memory=scientific_memory,
        )

        evidence = recovered_evidence_descriptors(
            nexus=runtime.nexus,
            subject_id=subject_id,
        )

        nexus_context = dict(
            recovered_nexus_context(
                reconstructed=reconstructed,
                nexus=runtime.nexus,
                research_concepts=runtime.concepts.payloads(),
            )
        )

        nexus_context["cross_subject_scientific_memory"] = (
            build_cross_subject_context(
                scientific_memory,
                active_subject_id=subject_id,
            )
        )

        recovery_context = dict(
            nexus_context.get("recovery_context", {})
        )
        recovery_context.update(
            {
                "mode": "FRESH_SUBJECT_COMPLETED_BATCH_INTERPRETATION_ONLY",
                "analysis_execution_enabled": False,
                "analysis_executions_before_interpretation": 0,
                "prior_analysis_reexecution_allowed": False,
                "raw_acquired_evidence_payloads_restored": False,
                "instruction": (
                    "Interpret the already completed fresh-subject batch. "
                    "No Analysis may execute before this interpretation. "
                    "If further Analysis is scientifically warranted, author "
                    "it in the returned decision for a later continuation step. "
                    "Ticker-local discovery remains fully available, and "
                    "cross-subject transferability or conditional structure "
                    "may also be considered when scientifically useful."
                ),
            }
        )
        nexus_context["recovery_context"] = recovery_context

        decision = rd.interpret_batch_results(
            mission=mission,
            subject=reconstructed.subject,
            prior_decision=reconstructed.latest_decision,
            report=reconstructed.latest_report,
            evidence=evidence,
            available_methods=runtime.catalog.capability_payloads(),
            nexus_context=nexus_context,
        )

        recorder = BatchCampaignResearchRecorder(
            package_store=recovered_store
        )
        recorder.record_plan(
            campaign_id=campaign_id,
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

        applied_marker = state_dir / "resume_decision_applied.json"
        applied_marker.write_text(
            json.dumps(
                {
                    "applied": True,
                    "decision_source": (
                        "resume_interpretation_decision.json"
                    ),
                    "scientific_content_modified": False,
                    "research_packages_in_decision": len(
                        decision.research_packages
                    ),
                    "rp_closures_applied": len(
                        decision.rp_closures
                    ),
                    "promote_findings": len(
                        decision.promote_findings
                    ),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        payload = asdict(decision)

        resume_decision_path.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
                default=str,
            )
            + "\n",
            encoding="utf-8",
        )

        _append_jsonl(
            resume_decision_log,
            {
                "recorded_at_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
                "decision_sequence": (
                    len(reconstructed.decisions) + 1
                ),
                "analyses_executed": (
                    reconstructed.analyses_executed
                ),
                "analysis_executions_before_interpretation": 0,
                "resumed_from_completed_batch": len(
                    reconstructed.reports
                ),
                "decision": payload,
            },
        )

        spend = rd.sol_spend_snapshot()
        resume_spend = (
            0.0
            if spend is None
            else spend.actual_spend_usd
        )

        print(
            "RESUME_INTERPRETATION_ACCEPTED=True",
            flush=True,
        )
        print(
            "ANALYSIS_EXECUTIONS_BEFORE_INTERPRETATION=0",
            flush=True,
        )
        print(
            "EXACT_PRIOR_SUBJECT_CONTEXT_RESTORED=True",
            flush=True,
        )
        print(
            f"RESUME_SOL_SPEND_USD={resume_spend:.6f}",
            flush=True,
        )
        print(
            "TOTAL_SUBJECT_SOL_SPEND_USD="
            f"{prior_total_spend + resume_spend:.6f}",
            flush=True,
        )

    print(
        f"CONTINUE_RESEARCH={decision.continue_research}",
        flush=True,
    )
    print(
        f"RESEARCH_PACKAGES={len(decision.research_packages)}",
        flush=True,
    )
    print(
        "ANALYSIS_SPECIFICATIONS="
        f"{sum(len(package.analyses) for package in decision.research_packages)}",
        flush=True,
    )
    print(
        f"PROMOTE_FINDINGS={len(decision.promote_findings)}",
        flush=True,
    )
    print(
        f"RP_CLOSURES={len(decision.rp_closures)}",
        flush=True,
    )
    print(
        f"DECISION_JSON={resume_decision_path}",
        flush=True,
    )

    if args.interpret_only:
        print("INTERPRET_ONLY=True", flush=True)
        print("NEW_ANALYSIS_EXECUTIONS=0", flush=True)
        return 0

    if not decision.continue_research:
        print("CONTINUATION_REQUIRED=False", flush=True)
        return 0

    applied_marker = state_dir / "resume_decision_applied.json"
    if not applied_marker.is_file():
        raise RuntimeError(
            "resume decision exists but durable RP application marker "
            "is missing"
        )

    decision_fingerprint = _decision_fingerprint(decision)

    requested_analysis_ids = {
        analysis.analysis_id
        for package in decision.research_packages
        for analysis in package.analyses
    }

    if active_decision_sequence is None:
        active_decision_sequence = len(reconstructed.decisions) + 1

    checkpointed_records_by_analysis_id = (
        _load_analysis_checkpoints(
            analysis_checkpoint_path,
            decision_fingerprint=decision_fingerprint,
            decision_sequence=active_decision_sequence,
            accepted_analysis_ids=requested_analysis_ids,
        )
    )

    checkpoint_ids = set(
        checkpointed_records_by_analysis_id
    )

    unexpected_checkpoint_ids = sorted(
        checkpoint_ids - requested_analysis_ids
    )
    if unexpected_checkpoint_ids:
        raise RuntimeError(
            "checkpointed analysis_id(s) are not members of "
            "the accepted resume decision: "
            + ", ".join(unexpected_checkpoint_ids)
        )

    recovered_analysis_ids = set(
        reconstructed.results_by_analysis_id
    )
    collisions = sorted(
        requested_analysis_ids.intersection(
            recovered_analysis_ids
        )
    )
    if collisions:
        raise RuntimeError(
            "resume decision attempts to reuse completed "
            "analysis_id(s): "
            + ", ".join(collisions)
        )

    print(
        "CONTINUATION_DECISION_FINGERPRINT="
        f"{decision_fingerprint}",
        flush=True,
    )
    print(
        "CONTINUATION_ANALYSES_AUTHORIZED="
        f"{len(requested_analysis_ids)}",
        flush=True,
    )
    print(
        "CONTINUATION_ANALYSES_CHECKPOINTED="
        f"{len(checkpoint_ids)}",
        flush=True,
    )
    print(
        "CONTINUATION_ANALYSES_PENDING="
        f"{len(requested_analysis_ids - checkpoint_ids)}",
        flush=True,
    )
    print(
        "PRIOR_ANALYSIS_REEXECUTION_ALLOWED=False",
        flush=True,
    )

    os.environ["MTS_SOL_TELEMETRY_PATH"] = str(
        continuation_telemetry
    )

    rd = SubjectContextSolBatchResearchDirector(
        prior_subject_scientific_context=(
            prior_subject_context
        ),
        research_package_store=recovered_store,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(
            os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")
        ),
        required_subject_id=subject_id,
        required_research_phase=ResearchPhase.EXPLORATION,
        sol_spend_limit_usd=remaining,
    )

    runtime = build_batch_runtime(
        rd=rd,
        mission=mission,
        nexus_path=nexus_path,
        scientific_memory=scientific_memory,
    )

    evidence = IntakeEngine(runtime.cache).ingest(
        subject=reconstructed.subject,
        source=standard_live_market_source(),
    )

    fresh_evidence_ids = {
        item.evidence_id for item in evidence
    }
    required_direct_evidence_ids = _direct_evidence_ids(
        decision
    )

    missing_direct_evidence_ids = sorted(
        required_direct_evidence_ids
        - fresh_evidence_ids
    )
    if missing_direct_evidence_ids:
        raise RuntimeError(
            "cannot execute accepted Sol continuation without "
            "substituting evidence. Fresh Intake did not reproduce "
            "required evidence_id(s): "
            + ", ".join(missing_direct_evidence_ids)
        )

    recorder = BatchCampaignResearchRecorder(
        package_store=recovered_store
    )

    # Checkpointed requests may already be durable. Re-recording an
    # identical request is intentionally idempotent and closes the
    # crash window between checkpoint persistence and later batch-level
    # recording.
    for checkpoint in (
        checkpointed_records_by_analysis_id.values()
    ):
        if checkpoint.compiled_request is not None:
            recorder.record_accepted_request(
                campaign_id=campaign_id,
                subject=reconstructed.subject,
                request=checkpoint.compiled_request,
            )

    continuation_reports_path = (
        state_dir / "continuation_batch_reports.jsonl"
    )
    continuation_decisions_path = (
        state_dir / "continuation_batch_decisions.jsonl"
    )

    latest_report = None
    written_checkpoint_records = dict(
        checkpointed_records_by_analysis_id
    )
    current_decision = decision
    current_decision_fingerprint = decision_fingerprint
    current_requested_analysis_ids = set(requested_analysis_ids)

    def accepted(request):
        recorder.record_accepted_request(
            campaign_id=campaign_id,
            subject=reconstructed.subject,
            request=request,
        )

    def checkpoint(record, decisions, analyses):
        prior = written_checkpoint_records.get(
            record.analysis_id
        )

        if prior is not None:
            if prior != record:
                raise RuntimeError(
                    "attempted to overwrite continuation checkpoint "
                    "with different terminal record: "
                    f"{record.analysis_id}"
                )
            return

        _append_jsonl(
            analysis_checkpoint_path,
            {
                "recorded_at_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
                "decision_fingerprint": (
                    current_decision_fingerprint
                ),
                "decision_sequence": decisions,
                "analyses_executed": analyses,
                "record": asdict(record),
            },
        )
        written_checkpoint_records[
            record.analysis_id
        ] = record

    def on_report(report, decisions, analyses):
        nonlocal latest_report
        latest_report = report

        expected_ids = current_requested_analysis_ids
        report_ids = {
            record.analysis_id
            for record in report.records
        }

        if report_ids != expected_ids:
            missing = sorted(
                expected_ids - report_ids
            )
            extra = sorted(
                report_ids - expected_ids
            )
            raise RuntimeError(
                "continuation report is not the complete accepted "
                "Sol batch; "
                f"missing={missing} extra={extra}"
            )

        recorder.record_report(report)

        _append_jsonl(
            continuation_reports_path,
            {
                "recorded_at_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
                "decisions": decisions,
                "analyses_executed": analyses,
                "decision_fingerprint": (
                    current_decision_fingerprint
                ),
                "report": asdict(report),
            },
        )

    def on_decision(
        next_decision,
        decisions,
        analyses,
    ):
        nonlocal current_decision
        nonlocal current_decision_fingerprint
        nonlocal current_requested_analysis_ids
        nonlocal written_checkpoint_records

        recorder.record_plan(
            campaign_id=campaign_id,
            subject=reconstructed.subject,
            decision=next_decision,
        )

        recorder.record_predictive_hypothesis_updates(
            next_decision,
            current_report=latest_report,
        )

        recorder.record_closures(next_decision)

        for finding in next_decision.promote_findings:
            runtime.nexus.publish_finding(finding)

        _append_jsonl(
            continuation_decisions_path,
            {
                "recorded_at_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
                "decision_sequence": decisions,
                "analyses_executed": analyses,
                "decision": asdict(next_decision),
            },
        )

        current_decision = next_decision
        current_decision_fingerprint = _decision_fingerprint(
            next_decision
        )
        current_requested_analysis_ids = {
            analysis.analysis_id
            for package in next_decision.research_packages
            for analysis in package.analyses
        }
        written_checkpoint_records = {}

    baseline = ContinuationBaseline(
        decisions=(
            len(reconstructed.decisions) + 1
        ),
        batches_executed=len(
            reconstructed.reports
        ),
        analyses_executed=(
            reconstructed.analyses_executed
        ),
        findings_promoted=(
            reconstructed.findings_promoted
            + len(decision.promote_findings)
        ),
    )

    continuation = (
        CrossSubjectRecoveredBatchCampaignContinuation(
            mission=mission,
            rd=rd,
            validator=runtime.validator,
            analysis=runtime.analysis,
            nexus=runtime.nexus,
            cache=runtime.cache,
            available_methods=(
                runtime.catalog.capability_payloads()
            ),
            research_concepts=(
                runtime.concepts.payloads()
            ),
            scientific_memory=scientific_memory,
        )
    )

    try:
        outcome = continuation.continue_from_decision(
            subject=reconstructed.subject,
            evidence=evidence,
            initial_decision=decision,
            prior_results_by_analysis_id=(
                reconstructed.results_by_analysis_id
            ),
            baseline=baseline,
            decision_callback=on_decision,
            report_callback=on_report,
            accepted_request_callback=accepted,
            checkpointed_records_by_analysis_id=(
                checkpointed_records_by_analysis_id
            ),
            analysis_checkpoint_callback=checkpoint,
        )
    except SolSpendAuthorizationRequired as exc:
        authorization_path = (
            state_dir
            / "continuation_sol_spend_authorization_required.json"
        )
        authorization_path.write_text(
            json.dumps(
                asdict(exc.snapshot),
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(
            "HUMAN_SOL_SPEND_AUTHORIZATION_REQUIRED=True",
            flush=True,
        )
        print(
            f"AUTHORIZATION_ARTIFACT={authorization_path}",
            flush=True,
        )
        return 2

    spend = rd.sol_spend_snapshot()
    new_continuation_sol_spend = (
        0.0
        if spend is None
        else spend.actual_spend_usd
    )

    continuation_analyses = (
        outcome.analyses_executed
        - baseline.analyses_executed
    )
    continuation_batches = (
        outcome.batches_executed
        - baseline.batches_executed
    )

    total_subject_sol_spend = (
        prior_total_spend
        + new_continuation_sol_spend
    )

    summary = {
        "campaign_id": campaign_id,
        "subject_id": subject_id,
        "mode": "FRESH_FULL_SUBJECT_RESUME",
        "cross_subject_context_preserved": True,
        "canonical_cross_subject_memory_source": str(
            scientific_memory.path
        ),
        "exact_prior_subject_context_restored": True,
        "prior_analysis_reexecution_allowed": False,
        "recovered_results": len(
            reconstructed.results_by_analysis_id
        ),
        "accepted_resume_decision_fingerprint": (
            decision_fingerprint
        ),
        "accepted_resume_analysis_specifications": len(
            requested_analysis_ids
        ),
        "continuation_checkpoint_records": len(
            written_checkpoint_records
        ),
        "continuation_batches_executed": (
            continuation_batches
        ),
        "continuation_analyses_executed": (
            continuation_analyses
        ),
        "total_decisions": outcome.decisions,
        "total_batches_executed": (
            outcome.batches_executed
        ),
        "total_analyses_executed": (
            outcome.analyses_executed
        ),
        "closed": outcome.closed,
        "close_reason": outcome.close_reason,
        "prior_sol_spend_usd": prior_total_spend,
        "new_continuation_sol_spend_usd": (
            new_continuation_sol_spend
        ),
        "total_subject_sol_spend_usd": (
            total_subject_sol_spend
        ),
        "final_decision": asdict(
            outcome.final_decision
        ),
    }

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        f"CONTINUATION_BATCHES={continuation_batches}",
        flush=True,
    )
    print(
        f"CONTINUATION_ANALYSES={continuation_analyses}",
        flush=True,
    )
    print(
        f"TOTAL_ANALYSES={outcome.analyses_executed}",
        flush=True,
    )
    print(
        f"CLOSED={outcome.closed}",
        flush=True,
    )
    print(
        f"CLOSE_REASON={outcome.close_reason}",
        flush=True,
    )
    print(
        "CROSS_SUBJECT_CONTEXT_PRESERVED=True",
        flush=True,
    )
    print(
        "NEW_CONTINUATION_SOL_SPEND_USD="
        f"{new_continuation_sol_spend:.6f}",
        flush=True,
    )
    print(
        "TOTAL_SUBJECT_SOL_SPEND_USD="
        f"{total_subject_sol_spend:.6f}",
        flush=True,
    )
    print(
        f"CHECKPOINT_FILE={analysis_checkpoint_path}",
        flush=True,
    )
    print(
        f"SUMMARY={summary_path}",
        flush=True,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
