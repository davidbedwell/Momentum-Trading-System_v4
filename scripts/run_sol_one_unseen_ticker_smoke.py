from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

from MTS_V4.adaptive_batch import SubjectEligibilityEnvelope, SubjectRunLedger
from MTS_V4.bootstrap import DEFAULT_MISSION, build_runtime
from MTS_V4.campaign import CheckpointedCampaignRunner
from MTS_V4.checkpoint import JsonCampaignCheckpointStore
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore
from MTS_V4.decision_journal import JsonResearchDecisionJournal
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.research_recording import CampaignResearchRecorder
from MTS_V4.sol_primary_provider import SolPrimaryResearchDirector
from MTS_V4.subject_memory_digest import SolSubjectScientificMemoryAuthor
from MTS_V4.subject_selection import RDSubjectSelectionDecision, SolAdaptiveSubjectSelector


AAPL_HYPOTHESIS_ID = "H-AAPL-MOM-001-SEVERE-5D-REBOUND"
AAPL_HYPOTHESIS_STATEMENT = (
    "When AAPL close return from T-5 through T is less than or equal to -5%, "
    "the close at T+5 will be strictly greater than the close at T."
)
AAPL_SUCCESS_DEFINITION = "SUCCESS iff close(T+5) > close(T); otherwise FAILURE."

DEFAULT_CANDIDATES = (
    "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AMD", "JPM",
    "GS", "CAT", "BA", "WMT", "COST", "UNH",
)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _candidate_subject_ids() -> tuple[str, ...]:
    configured = os.getenv("MTS_SOL_SMOKE_CANDIDATES", "").strip()
    tickers = tuple(
        item.strip().upper()
        for item in (configured.split(",") if configured else DEFAULT_CANDIDATES)
        if item.strip()
    )
    if not tickers:
        raise RuntimeError("candidate universe is empty")
    if "AAPL" in tickers:
        raise RuntimeError("AAPL is prior scientific memory and cannot be an unseen smoke candidate")
    if "XOM" in tickers:
        raise RuntimeError("XOM has prior MTS exposure and cannot be an unseen smoke candidate")
    return tuple(f"equity:{ticker}" for ticker in tickers)


def _ticker(subject_id: str) -> str:
    prefix, separator, ticker = subject_id.partition(":")
    if prefix != "equity" or separator != ":" or not ticker:
        raise RuntimeError(f"unsupported subject_id for live equity smoke: {subject_id}")
    return ticker.upper()


def _aapl_scientific_context() -> Mapping[str, object]:
    """Audited source context for Sol to consolidate into durable scientific memory."""
    return {
        "source_run": "AAPL Sol comparison rerun audited 2026-09-11; evidence as of 2026-09-10",
        "subject_id": "equity:AAPL",
        "scientific_findings_promoted": 0,
        "important_tentative_hypothesis": {
            "hypothesis_id": AAPL_HYPOTHESIS_ID,
            "statement": AAPL_HYPOTHESIS_STATEMENT,
            "success_definition": AAPL_SUCCESS_DEFINITION,
            "status": "TENTATIVE_REQUIRES_BLIND_VALIDATION",
            "subject_scope": (
                "AAPL only. This exact frozen hypothesis is not directly valid as a blind "
                "hypothesis on another ticker. Its pattern may motivate a separate falsifiable "
                "cross-subject generalization, but that generalization must be explicitly authored "
                "and frozen before validation on another subject."
            ),
            "trigger_protocol": {
                "observable_trigger": "close return from T-5 through T <= -0.05",
                "prediction_horizon_sessions": 5,
                "prediction_must_be_locked_before": "T+1 information",
                "overlap_rule": "no overlapping unresolved five-session trial",
                "minimum_required_trials": 20,
            },
        },
        "exploratory_measurement": {
            "aligned_rows": 491,
            "severe_weakness_rows": 38,
            "non_severe_rows": 453,
            "severe_t_plus_5_mean": 0.0331,
            "severe_t_plus_5_median": 0.0307,
            "severe_positive_finish_fraction": 0.736842,
            "non_severe_t_plus_5_mean": 0.0021,
            "non_severe_t_plus_5_median": 0.0034,
            "non_severe_positive_finish_fraction": 0.536424,
            "descriptive_positive_finish_advantage_percentage_points": 20.0418,
        },
        "scientific_limitations": (
            "severe rows were clustered/consecutive",
            "backward and forward windows overlap",
            "effective independent episodes are fewer than 38",
            "groups are unequal",
            "threshold selection/multiplicity remain concerns",
            "temporal stability is unknown",
            "blind validation is required",
        ),
        "validation_boundary_reached": {
            "latest_observable_date": "2026-09-10",
            "latest_backward_5_session_return": 0.00495,
            "trigger_active": False,
            "prediction_locked": False,
            "trial_created": False,
        },
        "evidence_ids": (
            "evidence:equity:AAPL:555bb6528103ea9eef7feaaa",
            "evidence:equity:AAPL:a5b94ce3197124c281a81dbb",
            "evidence:equity:AAPL:7c13d94208d95fcd3e63eac3",
            "evidence:equity:AAPL:af529e78d58cc88e80633916",
            "evidence:equity:AAPL:195dd9c16d6037e923e76d64",
            "evidence:equity:AAPL:8d8ba19cb1c2a66eed8a0876",
        ),
        "methodological_lesson": (
            "Preserve coordinate-space lineage explicitly when composing derived datasets; "
            "row position and source/anchor identity are not interchangeable."
        ),
    }


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


def _seed_aapl_memory_if_needed(
    *,
    rd: SolPrimaryResearchDirector,
    memory: JsonCrossSubjectScientificMemoryStore,
) -> None:
    if any(record.subject_id == "equity:AAPL" for record in memory.records()):
        return
    digest = SolSubjectScientificMemoryAuthor(
        rd=rd,
        scientific_memory=memory,
    ).author_and_persist(
        mission=DEFAULT_MISSION,
        subject_id="equity:AAPL",
        subject_scientific_context=_aapl_scientific_context(),
    )
    if not any(record.hypothesis_id == AAPL_HYPOTHESIS_ID for record in digest.records):
        raise RuntimeError(
            "Sol-authored AAPL memory did not preserve the supplied frozen hypothesis_id; "
            "deterministic code will not substitute or invent hypothesis provenance"
        )


def _configured_sources() -> tuple[str, ...]:
    return (
        "YFINANCE_DAILY",
        "UNUSUAL_WHALES_DARKPOOL_PRICE_LEVELS",
        "UNUSUAL_WHALES_FLOW_ALERTS",
        "UNUSUAL_WHALES_GREEK_EXPOSURE_BY_EXPIRY",
        "UNUSUAL_WHALES_FLOW_BY_EXPIRY",
        "FINRA_OTC_TRANSPARENCY_WEEKLY_SUMMARY",
    )


def _select_subject(
    *,
    rd: SolPrimaryResearchDirector,
    memory: JsonCrossSubjectScientificMemoryStore,
    candidate_subject_ids: Sequence[str],
) -> RDSubjectSelectionDecision:
    selector = SolAdaptiveSubjectSelector(
        rd=rd,
        scientific_memory=memory,
        eligibility=SubjectEligibilityEnvelope(
            approved_subject_ids=frozenset(candidate_subject_ids),
        ),
    )
    return selector.choose_next(
        mission=DEFAULT_MISSION,
        previously_seen=("equity:AAPL",),
        candidate_subject_ids=candidate_subject_ids,
        available_sources_by_subject={
            subject_id: _configured_sources() for subject_id in candidate_subject_ids
        },
    )


def _require_scientifically_applicable_first_role(selection: RDSubjectSelectionDecision) -> None:
    if selection.mode != "VALIDATION_FIRST":
        return
    if selection.hypothesis_id == AAPL_HYPOTHESIS_ID:
        raise RuntimeError(
            "Sol selected VALIDATION_FIRST using an AAPL-specific frozen hypothesis on a different "
            "subject. That would be category substitution, not blind validation. The AAPL pattern "
            "may motivate a separately authored cross-subject hypothesis, but deterministic code "
            "will not rewrite AAPL into the selected ticker."
        )
    raise RuntimeError(
        "Sol selected VALIDATION_FIRST for a hypothesis whose frozen cross-subject protocol is not "
        "present in the initial AAPL-only memory. Do not infer or invent the missing protocol."
    )


def _subject_research_provenance(
    *,
    package_store: JsonResearchPackageStore,
    subject_id: str,
) -> tuple[Mapping[str, object], ...]:
    """Expose compact durable RP lineage without making scientific selections."""
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
                        "status": item.status,
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


def main() -> None:
    timeout_seconds = int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600"))
    max_analyses = int(os.getenv("MTS_SOL_SMOKE_MAX_ANALYSES", "100"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    state_dir = Path(
        os.getenv("MTS_SOL_SMOKE_STATE_DIR", f"/home/ubuntu/mts-v4-sol-one-unseen-{stamp}")
    )
    state_dir.mkdir(parents=True, exist_ok=True)

    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    memory = JsonCrossSubjectScientificMemoryStore(state_dir / "cross_subject_memory.json")
    coordination_rd = _sol_rd(package_store=package_store, timeout_seconds=timeout_seconds)

    _seed_aapl_memory_if_needed(rd=coordination_rd, memory=memory)
    candidates = _candidate_subject_ids()
    selection = _select_subject(
        rd=coordination_rd,
        memory=memory,
        candidate_subject_ids=candidates,
    )
    (state_dir / "selection.json").write_text(
        json.dumps(
            {
                "subject_id": selection.subject_id,
                "rationale": selection.rationale,
                "mode": selection.mode,
                "hypothesis_id": selection.hypothesis_id,
            },
            sort_keys=True,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    _require_scientifically_applicable_first_role(selection)

    subject = SubjectMetadata(
        subject_id=selection.subject_id,
        ticker=_ticker(selection.subject_id),
    )
    exploration_rd = _sol_rd(
        package_store=package_store,
        timeout_seconds=timeout_seconds,
        required_subject_id=selection.subject_id,
        required_research_phase=ResearchPhase.EXPLORATION,
    )
    runtime = build_runtime(
        rd=exploration_rd,
        mission=DEFAULT_MISSION,
        nexus_path=state_dir / "research_nexus.json",
        max_contract_repairs=3,
        scientific_memory=memory,
    )
    evidence = IntakeEngine(runtime.cache).ingest(
        subject=subject,
        source=standard_live_market_source(),
    )

    recorder = CampaignResearchRecorder(
        package_store=package_store,
        decision_journal=JsonResearchDecisionJournal(state_dir / "rd_decisions.jsonl"),
    )
    runner = CheckpointedCampaignRunner(
        orchestrator=runtime.orchestrator,
        cache=runtime.cache,
        checkpoint_store=JsonCampaignCheckpointStore(state_dir / "checkpoint.json"),
        research_recorder=recorder,
    )
    campaign_id = f"mts-v4-sol-one-unseen-{subject.ticker.lower()}-{stamp}"
    outcome = runner.run_new(
        campaign_id=campaign_id,
        subject=subject,
        evidence=evidence,
        max_analyses=max_analyses,
    )

    durable_packages = _subject_research_provenance(
        package_store=package_store,
        subject_id=selection.subject_id,
    )
    scientific_context = {
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
    digest = SolSubjectScientificMemoryAuthor(
        rd=coordination_rd,
        scientific_memory=memory,
    ).author_and_persist(
        mission=DEFAULT_MISSION,
        subject_id=selection.subject_id,
        subject_scientific_context=scientific_context,
    )

    ledger = SubjectRunLedger(
        subject_id=selection.subject_id,
        selection_rationale=selection.rationale,
        decisions=outcome.decisions,
        analyses_executed=outcome.analyses_executed,
        findings_promoted=outcome.findings_promoted,
        research_packages=len(durable_packages),
        validation_trials=0,
        close_reason=outcome.close_reason,
        zero_finding_diagnosis=(
            "No formal Finding was promoted; inspect the Sol-authored subject digest and final "
            "research state for the scientific explanation."
            if outcome.findings_promoted == 0 else None
        ),
    )
    (state_dir / "subject_ledger.json").write_text(
        json.dumps(asdict(ledger), sort_keys=True, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"SOL_MODEL={_required_env('MTS_SOL_MODEL')}", flush=True)
    print("PRIOR_MEMORY_SUBJECT=equity:AAPL", flush=True)
    print(f"CANDIDATE_COUNT={len(candidates)}", flush=True)
    print(f"SELECTED_SUBJECT={selection.subject_id}", flush=True)
    print(f"SELECTION_MODE={selection.mode}", flush=True)
    print(f"SELECTION_HYPOTHESIS_ID={selection.hypothesis_id}", flush=True)
    print(f"SELECTION_RATIONALE={selection.rationale}", flush=True)
    print(f"EVIDENCE_COUNT={len(evidence)}", flush=True)
    print(f"OUTCOME_DECISIONS={outcome.decisions}", flush=True)
    print(f"OUTCOME_ANALYSES={outcome.analyses_executed}", flush=True)
    print(f"OUTCOME_FINDINGS_PROMOTED={outcome.findings_promoted}", flush=True)
    print(f"OUTCOME_CLOSED={outcome.closed}", flush=True)
    print(f"OUTCOME_CLOSE_REASON={outcome.close_reason}", flush=True)
    print(f"RESEARCH_PACKAGES={len(durable_packages)}", flush=True)
    print(f"DIGEST_RECORDS={len(digest.records)}", flush=True)
    print(f"FRONTIER_VERSION={digest.frontier.version if digest.frontier else None}", flush=True)


if __name__ == "__main__":
    main()
