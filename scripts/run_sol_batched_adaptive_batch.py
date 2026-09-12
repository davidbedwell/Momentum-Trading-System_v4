from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
from typing import Mapping, Sequence

from MTS_V4.adaptive_batch import SubjectEligibilityEnvelope, SubjectRunLedger, ThreeSubjectBatchController
from MTS_V4.adaptive_program import CompletedSubjectRun, SolAdaptiveThreeSubjectProgram
from MTS_V4.batch_contracts import BatchExecutionReport
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.batch_synthesis import SolBatchScientificSynthesizer
from MTS_V4.bootstrap import DEFAULT_MISSION, build_batch_runtime
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector
from MTS_V4.sol_primary_provider import SolPrimaryResearchDirector
from MTS_V4.sol_spend_guard import (
    DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    SolSpendAuthorizationRequired,
    SolSpendAuthorizationSnapshot,
)
from MTS_V4.subject_memory_digest import SolSubjectScientificMemoryAuthor
from MTS_V4.subject_selection import RDSubjectSelectionDecision, SolAdaptiveSubjectSelector
from MTS_V4.validation_first import ValidationFirstSubjectGate


DEFAULT_CANDIDATES = (
    "AAPL", "MSFT", "XOM", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AMD", "JPM", "GS",
    "CAT", "BA", "WMT", "COST", "UNH", "JNJ", "PG", "HD",
)
DEFAULT_PREVIOUSLY_SEEN = ("equity:AAPL", "equity:MSFT", "equity:XOM")


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _positive_float_env(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    value = default if not raw else float(raw)
    if value <= 0:
        raise RuntimeError(f"{name} must be positive")
    return value


def _format_money(value: float | None) -> str:
    return "unknown" if value is None else f"${value:.2f}"


def _interactive_spend_authorization(
    subject_id: str,
    snapshot: SolSpendAuthorizationSnapshot,
) -> float | None:
    print(f"\nHUMAN SOL SPEND AUTHORIZATION REQUIRED SUBJECT={subject_id}", flush=True)
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
            "Enter a new total Sol spend ceiling in USD for this subject, or press Enter to stop: "
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


def _ticker(subject_id: str) -> str:
    prefix, separator, ticker = subject_id.partition(":")
    if prefix != "equity" or separator != ":" or not ticker:
        raise RuntimeError(f"unsupported subject_id for live equity batch: {subject_id}")
    return ticker.upper()


def _configured_sources() -> tuple[str, ...]:
    return (
        "YFINANCE_DAILY",
        "UNUSUAL_WHALES_DARKPOOL_PRICE_LEVELS",
        "UNUSUAL_WHALES_FLOW_ALERTS",
        "UNUSUAL_WHALES_GREEK_EXPOSURE_BY_EXPIRY",
        "UNUSUAL_WHALES_FLOW_BY_EXPIRY",
        "FINRA_OTC_TRANSPARENCY_WEEKLY_SUMMARY",
    )


def _candidate_subject_ids() -> tuple[str, ...]:
    configured = os.getenv("MTS_ADAPTIVE_BATCH_CANDIDATES", "").strip()
    tickers = tuple(
        item.strip().upper()
        for item in (configured.split(",") if configured else DEFAULT_CANDIDATES)
        if item.strip()
    )
    if len(tickers) < 1:
        raise RuntimeError("adaptive batch requires at least one candidate ticker")
    if len(tickers) != len(set(tickers)):
        raise RuntimeError("adaptive batch candidate tickers must be unique")
    return tuple(f"equity:{ticker}" for ticker in tickers)


def _previously_seen() -> tuple[str, ...]:
    configured = os.getenv("MTS_ADAPTIVE_BATCH_PREVIOUSLY_SEEN", "").strip()
    if not configured:
        return DEFAULT_PREVIOUSLY_SEEN
    values = tuple(item.strip() for item in configured.split(",") if item.strip())
    return tuple(
        value if value.startswith("equity:") else f"equity:{value.upper()}"
        for value in values
    )


def _seed_memory_if_requested(*, state_dir: Path) -> Path:
    memory_path = state_dir / "cross_subject_memory.json"
    if memory_path.exists():
        return memory_path
    seed = os.getenv("MTS_ADAPTIVE_BATCH_SEED_MEMORY_PATH", "").strip()
    if not seed:
        return memory_path
    seed_path = Path(seed)
    if not seed_path.is_file():
        raise RuntimeError(f"seed scientific-memory file does not exist: {seed_path}")
    shutil.copy2(seed_path, memory_path)
    return memory_path


def _subject_research_provenance(
    *, package_store: JsonResearchPackageStore, subject_id: str
) -> tuple[Mapping[str, object], ...]:
    packages: list[Mapping[str, object]] = []
    for rp_id in package_store.list_ids():
        package = package_store.load(rp_id)
        if package is None or package.subject_id != subject_id:
            continue
        packages.append(
            {
                "rp_id": package.rp_id,
                "parent_rp_id": package.parent_rp_id,
                "status": package.status,
                "close_reason": package.close_reason,
                "final_assessment": package.final_assessment,
                "findings": [dict(item) for item in package.findings],
                "predictive_hypotheses": [
                    {
                        "hypothesis_id": item.hypothesis_id,
                        "statement": item.statement,
                        "success_definition": item.success_definition,
                        "status": item.status,
                        "minimum_required_trials": item.minimum_required_trials,
                        "source_result_ids": list(item.source_result_ids),
                    }
                    for item in package.predictive_hypotheses
                ],
                "analysis_results": [
                    {
                        "request_id": item.request_id,
                        "result_id": item.result_id,
                        "execution_status": item.execution_status,
                        "research_phase": item.research_phase,
                    }
                    for item in package.analyses
                    if item.result_id is not None
                ],
            }
        )
    return tuple(packages)


def _validatable_hypothesis_ids_from_environment() -> frozenset[str]:
    configured = os.getenv("MTS_ADAPTIVE_BATCH_VALIDATABLE_HYPOTHESES", "").strip()
    if not configured:
        return frozenset()
    raise RuntimeError(
        "MTS_ADAPTIVE_BATCH_VALIDATABLE_HYPOTHESES was supplied, but this runner does not yet "
        "have an approved executable protocol registry. Refusing to infer validation science."
    )


def _append_jsonl(path: Path, payload: Mapping[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")) + "\n")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the adaptive MTS v4 subject program with batched Sol research inside each subject. "
            "Subject selection/memory synthesis remain coordination calls; each subject gets an initial "
            "$20 Sol-spend authorization by default while scientific RP/Analysis breadth remains unbounded."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate non-secret configuration and exit before any Intake or Sol API call",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    timeout_seconds = int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600"))
    for legacy_name in (
        "MTS_ADAPTIVE_BATCH_MAX_ANALYSES_PER_SUBJECT",
        "MTS_HUMAN_SAFETY_MAX_ANALYSES_PER_SUBJECT",
    ):
        if os.getenv(legacy_name, "").strip():
            raise RuntimeError(
                f"{legacy_name} is retired. Analysis count is not a funding or scientific limit. "
                "Use MTS_SOL_SPEND_LIMIT_USD_PER_SUBJECT to change the human Sol dollar authorization."
            )
    sol_spend_limit_usd = _positive_float_env(
        "MTS_SOL_SPEND_LIMIT_USD_PER_SUBJECT",
        DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    )
    batch_limit = int(os.getenv("MTS_ADAPTIVE_BATCH_SUBJECT_LIMIT", "3"))
    if batch_limit < 1:
        raise RuntimeError("MTS_ADAPTIVE_BATCH_SUBJECT_LIMIT must be positive")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    batch_id = os.getenv("MTS_ADAPTIVE_BATCH_ID", f"mts-v4-sol-batched-{stamp}").strip()
    state_dir = Path(os.getenv("MTS_ADAPTIVE_BATCH_STATE_DIR", f"/home/ubuntu/{batch_id}"))
    candidates = _candidate_subject_ids()
    if len(candidates) < batch_limit:
        raise RuntimeError(
            f"adaptive batch subject limit {batch_limit} exceeds candidate count {len(candidates)}"
        )
    previously_seen = _previously_seen()
    if args.dry_run:
        print(
            f"DRY_RUN=True BATCH_ID={batch_id} SUBJECT_LIMIT={batch_limit} "
            f"SOL_SPEND_LIMIT_USD_PER_SUBJECT={sol_spend_limit_usd:.2f} "
            f"CANDIDATES={len(candidates)} STATE_DIR={state_dir}"
        )
        return 0

    state_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MTS_SOL_TELEMETRY_PATH", str(state_dir / "sol_transport_telemetry.jsonl"))
    base_url = _required_env("MTS_SOL_BASE_URL")
    model = _required_env("MTS_SOL_MODEL")
    api_key = _required_env("MTS_SOL_API_KEY")

    memory_path = _seed_memory_if_requested(state_dir=state_dir)
    memory = JsonCrossSubjectScientificMemoryStore(memory_path)
    coordination_store = JsonResearchPackageStore(state_dir / "coordination_packages")
    coordination_rd = SolPrimaryResearchDirector(
        research_package_store=coordination_store,
        base_url=base_url,
        model=model,
        api_key=api_key,
        timeout_seconds=timeout_seconds,
    )
    eligibility = SubjectEligibilityEnvelope(
        approved_subject_ids=frozenset(candidates),
        required_available_sources=frozenset(_configured_sources()),
    )
    selector = SolAdaptiveSubjectSelector(
        rd=coordination_rd,
        scientific_memory=memory,
        eligibility=eligibility,
        validatable_hypothesis_ids=_validatable_hypothesis_ids_from_environment(),
    )
    controller = ThreeSubjectBatchController(
        batch_id=batch_id,
        eligibility=eligibility,
        batch_limit=batch_limit,
    )
    memory_author = SolSubjectScientificMemoryAuthor(rd=coordination_rd, scientific_memory=memory)
    synthesizer = SolBatchScientificSynthesizer(rd=coordination_rd, scientific_memory=memory)

    def run_blind_validation(
        selection: RDSubjectSelectionDecision,
        gate: ValidationFirstSubjectGate,
    ) -> None:
        raise RuntimeError(
            "VALIDATION_FIRST reached without an approved executable blind-validation protocol registry. "
            f"subject={selection.subject_id} hypothesis_id={selection.hypothesis_id}. "
            "Deterministic code will not invent cutoff, evidence windows, horizon, or scoring rule."
        )

    def run_exploration(selection: RDSubjectSelectionDecision) -> CompletedSubjectRun:
        subject_id = selection.subject_id
        ticker = _ticker(subject_id)
        subject = SubjectMetadata(subject_id=subject_id, ticker=ticker)
        subject_dir = state_dir / "subjects" / ticker
        subject_dir.mkdir(parents=True, exist_ok=False)
        package_store = JsonResearchPackageStore(subject_dir / "research_packages")
        recorder = BatchCampaignResearchRecorder(package_store=package_store)

        def authorize_more(snapshot: SolSpendAuthorizationSnapshot) -> float | None:
            return _interactive_spend_authorization(subject_id, snapshot)

        rd = SolBatchResearchDirector(
            research_package_store=package_store,
            base_url=base_url,
            model=model,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            required_subject_id=subject_id,
            required_research_phase=ResearchPhase.EXPLORATION,
            sol_spend_limit_usd=sol_spend_limit_usd,
            human_spend_authorization_callback=authorize_more,
        )
        runtime = build_batch_runtime(
            rd=rd,
            mission=DEFAULT_MISSION,
            nexus_path=subject_dir / "research_nexus.json",
            scientific_memory=memory,
        )
        evidence = IntakeEngine(runtime.cache).ingest(
            subject=subject,
            source=standard_live_market_source(),
        )
        campaign_id = f"{batch_id}-{ticker.lower()}"
        decision_path = subject_dir / "batch_decisions.jsonl"
        report_path = subject_dir / "batch_reports.jsonl"
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
            artifact = subject_dir / "sol_spend_authorization_required.json"
            artifact.write_text(
                json.dumps(asdict(exc.snapshot), sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            raise RuntimeError(
                "Human Sol-spend authorization required before another premium-model call: "
                f"subject={subject_id} actual_spend={exc.snapshot.actual_spend_usd:.4f} "
                f"authorized={exc.snapshot.authorized_spend_usd:.2f} artifact={artifact}"
            ) from exc

        spend = rd.sol_spend_snapshot()
        durable_packages = _subject_research_provenance(
            package_store=package_store,
            subject_id=subject_id,
        )
        scientific_context = {
            "batch_id": batch_id,
            "selection": {
                "subject_id": selection.subject_id,
                "rationale": selection.rationale,
                "mode": selection.mode,
                "hypothesis_id": selection.hypothesis_id,
            },
            "exploration_outcome": {
                "decisions": outcome.decisions,
                "batches_executed": outcome.batches_executed,
                "analyses_executed": outcome.analyses_executed,
                "findings_promoted": outcome.findings_promoted,
                "closed": outcome.closed,
                "close_reason": outcome.close_reason,
                "final_research_state": outcome.final_decision.research_state,
                "final_research_progress": (
                    asdict(outcome.final_decision.research_progress)
                    if outcome.final_decision.research_progress is not None
                    else None
                ),
                "sol_spend": asdict(spend) if spend is not None else None,
            },
            "durable_research_packages": durable_packages,
            "provenance_instruction": (
                "When a memory record summarizes a supplied Research Package, Finding, predictive hypothesis, "
                "or Analysis result, preserve its exact supplied rp_id, finding_id, hypothesis_id, and/or result_ids. "
                "Do not omit known durable provenance and do not invent identifiers."
            ),
            "evidence": [item.durable_metadata() for item in evidence],
        }
        hypotheses_created = sum(
            len(package.get("predictive_hypotheses", ())) for package in durable_packages
        )
        ledger = SubjectRunLedger(
            subject_id=subject_id,
            selection_rationale=selection.rationale,
            decisions=outcome.decisions,
            analyses_executed=outcome.analyses_executed,
            findings_promoted=outcome.findings_promoted,
            research_packages=len(durable_packages),
            hypotheses_created=hypotheses_created,
            validation_trials=0,
            close_reason=outcome.close_reason,
            zero_finding_diagnosis=(
                "No formal Finding was promoted; the mandatory post-batch Sol synthesis must diagnose why."
                if outcome.findings_promoted == 0 else None
            ),
        )
        (subject_dir / "subject_ledger.json").write_text(
            json.dumps(asdict(ledger), sort_keys=True, indent=2, default=str) + "\n",
            encoding="utf-8",
        )
        return CompletedSubjectRun(ledger=ledger, scientific_context=scientific_context)

    program = SolAdaptiveThreeSubjectProgram(
        mission=DEFAULT_MISSION,
        selector=selector,
        controller=controller,
        synthesizer=synthesizer,
        memory_author=memory_author,
        run_exploration=run_exploration,
        run_blind_validation=run_blind_validation,
        available_sources=lambda _subject_id: _configured_sources(),
    )
    result = program.run_batch(
        candidate_subject_ids=candidates,
        previously_seen=previously_seen,
    )
    ledger = controller.ledger()
    if not ledger.requires_review or len(ledger.subjects) != batch_limit:
        raise RuntimeError(
            f"adaptive batch returned without reaching the approved {batch_limit}-subject review boundary"
        )
    batch_artifact = {
        "batch_id": batch_id,
        "execution_architecture": "BATCHED_SOL_MULTI_RP_MULTI_ANALYSIS",
        "requires_human_review": True,
        "approved_subject_limit": batch_limit,
        "initial_sol_spend_authorization_usd_per_subject": sol_spend_limit_usd,
        "previously_seen_subject_ids": list(previously_seen),
        "candidate_subject_ids": list(candidates),
        "selections": [
            {
                "subject_id": item.subject_id,
                "rationale": item.rationale,
                "mode": item.mode,
                "hypothesis_id": item.hypothesis_id,
            }
            for item in result.selections
        ],
        "ledger": ledger.compact_context(),
        "subject_digests": [
            {
                "subject_id": digest.subject_id,
                "record_ids": [record.record_id for record in digest.records],
                "frontier_version": digest.frontier.version if digest.frontier else None,
            }
            for digest in result.subject_digests
        ],
        "batch_scientific_synthesis": dict(result.synthesis.synthesis),
        "sol_transport_telemetry": str(state_dir / "sol_transport_telemetry.jsonl"),
    }
    artifact_path = state_dir / "batch_review.json"
    artifact_path.write_text(
        json.dumps(batch_artifact, sort_keys=True, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"BATCH_ID={batch_id}", flush=True)
    print(f"SOL_MODEL={model}", flush=True)
    print(f"SUBJECTS={','.join(item.subject_id for item in result.selections)}", flush=True)
    print(f"SUBJECT_COUNT={len(result.selections)}", flush=True)
    print(f"APPROVED_SUBJECT_LIMIT={batch_limit}", flush=True)
    print(f"INITIAL_SOL_SPEND_AUTHORIZATION_USD_PER_SUBJECT={sol_spend_limit_usd:.2f}", flush=True)
    print("HUMAN_REVIEW_REQUIRED=True", flush=True)
    print(f"SOL_TELEMETRY={state_dir / 'sol_transport_telemetry.jsonl'}", flush=True)
    print(f"BATCH_REVIEW={artifact_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
