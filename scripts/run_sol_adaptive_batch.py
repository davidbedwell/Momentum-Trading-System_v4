from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

from MTS_V4.adaptive_batch import SubjectEligibilityEnvelope, SubjectRunLedger, ThreeSubjectBatchController
from MTS_V4.adaptive_program import CompletedSubjectRun, SolAdaptiveThreeSubjectProgram
from MTS_V4.batch_synthesis import SolBatchScientificSynthesizer
from MTS_V4.bootstrap import DEFAULT_MISSION, build_runtime
from MTS_V4.checkpoint import JsonCampaignCheckpointStore
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore
from MTS_V4.decision_journal import JsonResearchDecisionJournal
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.research_recording import CampaignResearchRecorder
from MTS_V4.campaign import CheckpointedCampaignRunner
from MTS_V4.sol_primary_provider import SolPrimaryResearchDirector
from MTS_V4.subject_memory_digest import SolSubjectScientificMemoryAuthor
from MTS_V4.subject_selection import RDSubjectSelectionDecision, SolAdaptiveSubjectSelector
from MTS_V4.validation_first import ValidationFirstSubjectGate


DEFAULT_CANDIDATES = (
    "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AMD", "JPM", "GS",
    "CAT", "BA", "WMT", "COST", "UNH", "JNJ", "PG", "HD",
)

DEFAULT_PREVIOUSLY_SEEN = (
    "equity:AAPL",
    "equity:MSFT",
    "equity:XOM",
)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
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
    if len(tickers) < 3:
        raise RuntimeError("adaptive batch requires at least three candidate tickers")
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


def _sol_rd(
    *,
    package_store: JsonResearchPackageStore,
    timeout_seconds: int,
    required_subject_id: str | None = None,
    required_research_phase: ResearchPhase | None = None,
) -> SolPrimaryResearchDirector:
    return SolPrimaryResearchDirector(
        research_package_store=package_store,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=timeout_seconds,
        required_subject_id=required_subject_id,
        required_research_phase=required_research_phase,
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
    *,
    package_store: JsonResearchPackageStore,
    subject_id: str,
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
    """Return only hypotheses with an externally supplied executable blind protocol.

    The current runner deliberately does not infer a historical cutoff, horizon,
    evidence window, or scoring rule from scientific prose. Until a protocol is
    explicitly supplied by a future validated protocol registry, the objectively
    executable set is empty and Sol may select only EXPLORATION. This preserves
    the approved authority boundary instead of deterministically inventing the
    science needed to make a blind trial runnable.
    """
    configured = os.getenv("MTS_ADAPTIVE_BATCH_VALIDATABLE_HYPOTHESES", "").strip()
    if not configured:
        return frozenset()
    raise RuntimeError(
        "MTS_ADAPTIVE_BATCH_VALIDATABLE_HYPOTHESES was supplied, but this runner does not yet "
        "have an approved executable protocol registry. Refusing to infer validation science."
    )


def main() -> None:
    timeout_seconds = int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600"))
    max_analyses = int(os.getenv("MTS_ADAPTIVE_BATCH_MAX_ANALYSES_PER_SUBJECT", "100"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    batch_id = os.getenv("MTS_ADAPTIVE_BATCH_ID", f"mts-v4-sol-batch-{stamp}").strip()
    state_dir = Path(
        os.getenv("MTS_ADAPTIVE_BATCH_STATE_DIR", f"/home/ubuntu/{batch_id}")
    )
    state_dir.mkdir(parents=True, exist_ok=True)

    candidates = _candidate_subject_ids()
    previously_seen = _previously_seen()
    overlap = sorted(set(candidates) & set(previously_seen))
    if overlap:
        raise RuntimeError(f"candidate universe contains previously seen subjects: {overlap}")

    memory_path = _seed_memory_if_requested(state_dir=state_dir)
    memory = JsonCrossSubjectScientificMemoryStore(memory_path)
    coordination_store = JsonResearchPackageStore(state_dir / "coordination_packages")
    coordination_rd = _sol_rd(
        package_store=coordination_store,
        timeout_seconds=timeout_seconds,
    )

    eligibility = SubjectEligibilityEnvelope(
        approved_subject_ids=frozenset(candidates),
        required_available_sources=frozenset(_configured_sources()),
    )
    validatable_hypothesis_ids = _validatable_hypothesis_ids_from_environment()
    selector = SolAdaptiveSubjectSelector(
        rd=coordination_rd,
        scientific_memory=memory,
        eligibility=eligibility,
        validatable_hypothesis_ids=validatable_hypothesis_ids,
    )
    controller = ThreeSubjectBatchController(
        batch_id=batch_id,
        eligibility=eligibility,
    )
    memory_author = SolSubjectScientificMemoryAuthor(
        rd=coordination_rd,
        scientific_memory=memory,
    )
    synthesizer = SolBatchScientificSynthesizer(
        rd=coordination_rd,
        scientific_memory=memory,
    )

    def run_blind_validation(
        selection: RDSubjectSelectionDecision,
        gate: ValidationFirstSubjectGate,
    ) -> None:
        raise RuntimeError(
            "VALIDATION_FIRST reached without an approved executable blind-validation protocol registry. "
            f"subject={selection.subject_id} hypothesis_id={selection.hypothesis_id}. "
            "Deterministic code will not invent the cutoff, evidence windows, horizon, or scoring rule."
        )

    def run_exploration(selection: RDSubjectSelectionDecision) -> CompletedSubjectRun:
        subject_id = selection.subject_id
        ticker = _ticker(subject_id)
        subject_dir = state_dir / "subjects" / ticker
        subject_dir.mkdir(parents=True, exist_ok=False)

        package_store = JsonResearchPackageStore(subject_dir / "research_packages")
        rd = _sol_rd(
            package_store=package_store,
            timeout_seconds=timeout_seconds,
            required_subject_id=subject_id,
            required_research_phase=ResearchPhase.EXPLORATION,
        )
        runtime = build_runtime(
            rd=rd,
            mission=DEFAULT_MISSION,
            nexus_path=subject_dir / "research_nexus.json",
            max_contract_repairs=3,
            scientific_memory=memory,
        )
        subject = SubjectMetadata(subject_id=subject_id, ticker=ticker)
        evidence = IntakeEngine(runtime.cache).ingest(
            subject=subject,
            source=standard_live_market_source(),
        )
        recorder = CampaignResearchRecorder(
            package_store=package_store,
            decision_journal=JsonResearchDecisionJournal(subject_dir / "rd_decisions.jsonl"),
        )
        runner = CheckpointedCampaignRunner(
            orchestrator=runtime.orchestrator,
            cache=runtime.cache,
            checkpoint_store=JsonCampaignCheckpointStore(subject_dir / "checkpoint.json"),
            research_recorder=recorder,
        )
        campaign_id = f"{batch_id}-{ticker.lower()}"
        outcome = runner.run_new(
            campaign_id=campaign_id,
            subject=subject,
            evidence=evidence,
            max_analyses=max_analyses,
        )
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
                "analyses_executed": outcome.analyses_executed,
                "findings_promoted": outcome.findings_promoted,
                "closed": outcome.closed,
                "close_reason": outcome.close_reason,
                "final_research_state": outcome.final_decision.research_state,
            },
            "durable_research_packages": durable_packages,
            "provenance_instruction": (
                "When a memory record summarizes a supplied Research Package, Finding, predictive "
                "hypothesis, or Analysis result, preserve its exact supplied rp_id, finding_id, "
                "hypothesis_id, and/or result_ids. Do not omit known durable provenance and do not "
                "invent identifiers."
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
        return CompletedSubjectRun(
            ledger=ledger,
            scientific_context=scientific_context,
        )

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
    if not ledger.requires_review or len(ledger.subjects) != 3:
        raise RuntimeError("adaptive batch returned without reaching the approved three-subject review boundary")

    batch_artifact = {
        "batch_id": batch_id,
        "requires_human_review": True,
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
    }
    artifact_path = state_dir / "batch_review.json"
    artifact_path.write_text(
        json.dumps(batch_artifact, sort_keys=True, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"BATCH_ID={batch_id}", flush=True)
    print(f"SOL_MODEL={_required_env('MTS_SOL_MODEL')}", flush=True)
    print(f"SUBJECTS={','.join(item.subject_id for item in result.selections)}", flush=True)
    print("SUBJECT_COUNT=3", flush=True)
    print("HUMAN_REVIEW_REQUIRED=True", flush=True)
    print(f"BATCH_REVIEW={artifact_path}", flush=True)


if __name__ == "__main__":
    main()
