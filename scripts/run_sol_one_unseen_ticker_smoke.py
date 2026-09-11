from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from MTS_V4.adaptive_batch import SubjectEligibilityEnvelope, SubjectRunLedger
from MTS_V4.blind_validation import HistoricalBlindValidationSession, HistoricalEvidenceWindow
from MTS_V4.blind_validation_runtime import build_blind_prediction_orchestrator
from MTS_V4.bootstrap import DEFAULT_MISSION, build_runtime
from MTS_V4.campaign import CheckpointedCampaignRunner
from MTS_V4.checkpoint import JsonCampaignCheckpointStore
from MTS_V4.contracts import EvidenceDescriptor, SubjectMetadata
from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore
from MTS_V4.decision_journal import JsonResearchDecisionJournal
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.research_recording import CampaignResearchRecorder
from MTS_V4.sol_primary_provider import SolPrimaryResearchDirector
from MTS_V4.subject_memory_digest import SolSubjectScientificMemoryAuthor
from MTS_V4.subject_selection import RDSubjectSelectionDecision, SolAdaptiveSubjectSelector
from MTS_V4.validation_first import ValidationFirstSubjectGate


AAPL_HYPOTHESIS_ID = "H-AAPL-MOM-001-SEVERE-5D-REBOUND"
AAPL_HYPOTHESIS_STATEMENT = (
    "When AAPL close return from T-5 through T is less than or equal to -5%, "
    "the close at T+5 will be strictly greater than the close at T."
)
AAPL_SUCCESS_DEFINITION = "SUCCESS iff close(T+5) > close(T); otherwise FAILURE."

DEFAULT_CANDIDATES = (
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOGL",
    "TSLA",
    "AMD",
    "JPM",
    "GS",
    "XOM",
    "CAT",
    "BA",
    "WMT",
    "COST",
    "UNH",
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
    return tuple(f"equity:{ticker}" for ticker in tickers)


def _ticker(subject_id: str) -> str:
    prefix, separator, ticker = subject_id.partition(":")
    if prefix != "equity" or separator != ":" or not ticker:
        raise RuntimeError(f"unsupported subject_id for live equity smoke: {subject_id}")
    return ticker.upper()


def _aapl_scientific_context() -> Mapping[str, object]:
    """Audited source context for Sol to consolidate; this is not deterministic memory authorship."""
    return {
        "source_run": "AAPL Sol comparison rerun audited 2026-09-11; evidence as of 2026-09-10",
        "subject_id": "equity:AAPL",
        "scientific_findings_promoted": 0,
        "important_tentative_hypothesis": {
            "hypothesis_id": AAPL_HYPOTHESIS_ID,
            "statement": AAPL_HYPOTHESIS_STATEMENT,
            "success_definition": AAPL_SUCCESS_DEFINITION,
            "status": "TENTATIVE_REQUIRES_BLIND_VALIDATION",
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


def _sol_rd(*, package_store: JsonResearchPackageStore, timeout_seconds: int) -> SolPrimaryResearchDirector:
    return SolPrimaryResearchDirector(
        research_package_store=package_store,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=timeout_seconds,
    )


def _seed_aapl_memory_if_needed(
    *,
    rd: SolPrimaryResearchDirector,
    memory: JsonCrossSubjectScientificMemoryStore,
) -> None:
    if any(record.subject_id == "equity:AAPL" for record in memory.records()):
        return
    author = SolSubjectScientificMemoryAuthor(rd=rd, scientific_memory=memory)
    digest = author.author_and_persist(
        mission=DEFAULT_MISSION,
        subject_id="equity:AAPL",
        subject_scientific_context=_aapl_scientific_context(),
    )
    if not any(record.hypothesis_id == AAPL_HYPOTHESIS_ID for record in digest.records):
        raise RuntimeError(
            "Sol-authored AAPL memory did not preserve the supplied frozen hypothesis_id; "
            "do not substitute or invent a hypothesis in deterministic code"
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
    eligibility = SubjectEligibilityEnvelope(
        approved_subject_ids=frozenset(candidate_subject_ids),
    )
    selector = SolAdaptiveSubjectSelector(
        rd=rd,
        scientific_memory=memory,
        eligibility=eligibility,
    )
    return selector.choose_next(
        mission=DEFAULT_MISSION,
        previously_seen=("equity:AAPL",),
        candidate_subject_ids=candidate_subject_ids,
        available_sources_by_subject={
            subject_id: _configured_sources() for subject_id in candidate_subject_ids
        },
    )


def _ohlcv_descriptor(evidence: Sequence[EvidenceDescriptor]) -> EvidenceDescriptor:
    matches = [item for item in evidence if item.evidence_type == "OHLCV"]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one OHLCV evidence descriptor; found {len(matches)}")
    return matches[0]


def _ohlcv_rows(runtime, descriptor: EvidenceDescriptor) -> tuple[Mapping[str, Any], ...]:
    payload = runtime.cache.get(descriptor.cache_key)
    rows = tuple(payload)
    if not rows or not all(isinstance(row, Mapping) for row in rows):
        raise RuntimeError("OHLCV payload is empty or invalid")
    return rows


def _close_value(row: Mapping[str, Any]) -> float:
    value = row.get("close")
    if not isinstance(value, (int, float)):
        raise RuntimeError(f"OHLCV close is nonnumeric: {value!r}")
    return float(value)


def _first_nonoverlapping_severe_5d_trial(rows: Sequence[Mapping[str, Any]]) -> tuple[int, int]:
    """Mechanical frozen-protocol trial selection independent of hidden outcome values.

    Scan chronologically and select the first trigger with five future sessions.
    The trigger itself uses only closes through T. The returned outcome index is
    exactly T+5 under the supplied frozen hypothesis.
    """
    for index in range(5, len(rows) - 5):
        prior = _close_value(rows[index - 5])
        current = _close_value(rows[index])
        if prior == 0:
            continue
        backward_return = (current - prior) / prior
        if backward_return <= -0.05:
            return index, index + 5
    raise RuntimeError("no eligible severe five-session weakness trigger exists in available OHLCV history")


def _blind_prediction_statement(outcome) -> tuple[str, str]:
    state = outcome.final_decision.research_state
    if not isinstance(state, Mapping):
        raise RuntimeError("blind validation final decision lacks mapping research_state")
    blind = state.get("blind_prediction")
    if not isinstance(blind, Mapping):
        raise RuntimeError("blind validation final decision lacks research_state.blind_prediction")
    statement = blind.get("prediction_statement")
    if not isinstance(statement, str) or not statement.strip():
        raise RuntimeError("blind validation prediction_statement is blank")
    result_id = blind.get("prediction_result_id")
    if not isinstance(result_id, str) or not result_id.strip():
        result_id = f"blind-prediction:{outcome.final_decision.next_request.request_id}" if outcome.final_decision.next_request else "blind-prediction:final-decision"
    return statement.strip(), result_id


def _run_validation_first(
    *,
    selection: RDSubjectSelectionDecision,
    gate: ValidationFirstSubjectGate,
    runtime,
    evidence: Sequence[EvidenceDescriptor],
    package_store: JsonResearchPackageStore,
    timeout_seconds: int,
) -> Mapping[str, object]:
    if selection.hypothesis_id != AAPL_HYPOTHESIS_ID:
        raise RuntimeError(
            "VALIDATION_FIRST selected an unsupported hypothesis for this controlled smoke; "
            "deterministic code will not infer a missing validation protocol"
        )

    descriptor = _ohlcv_descriptor(evidence)
    rows = _ohlcv_rows(runtime, descriptor)
    trigger_index, outcome_index = _first_nonoverlapping_severe_5d_trial(rows)
    date_field = "date"
    cutoff = rows[trigger_index].get(date_field)
    outcome_end = rows[outcome_index].get(date_field)
    if not isinstance(cutoff, str) or not isinstance(outcome_end, str):
        raise RuntimeError("controlled blind smoke requires string OHLCV date values")

    trial_id = f"trial:{selection.subject_id}:{AAPL_HYPOTHESIS_ID}:{cutoff}"
    session = HistoricalBlindValidationSession.build(
        trial_id=trial_id,
        hypothesis_id=AAPL_HYPOTHESIS_ID,
        subject=SubjectMetadata(subject_id=selection.subject_id, ticker=_ticker(selection.subject_id)),
        evidence=(descriptor,),
        source_cache=runtime.cache,
        windows=(
            HistoricalEvidenceWindow(
                evidence_id=descriptor.evidence_id,
                time_field=date_field,
                cutoff=cutoff,
                outcome_end=outcome_end,
            ),
        ),
    )
    blind = build_blind_prediction_orchestrator(
        session=session,
        runtime=runtime,
        research_package_store=package_store,
        hypothesis_statement=AAPL_HYPOTHESIS_STATEMENT,
        success_definition=AAPL_SUCCESS_DEFINITION,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=timeout_seconds,
    )
    outcome = blind.run(
        subject=session.subject,
        evidence=session.evidence,
        max_analyses=int(os.getenv("MTS_SOL_BLIND_MAX_ANALYSES", "25")),
    )
    statement, prediction_result_id = _blind_prediction_statement(outcome)
    session.lock_prediction(statement)
    gate.lock_prediction(trial_id=trial_id, prediction_result_id=prediction_result_id)

    revealed = session.reveal_outcomes()[descriptor.evidence_id]
    if len(revealed) < 5:
        raise RuntimeError("blind outcome reveal did not contain five post-cutoff sessions")
    trigger_close = _close_value(rows[trigger_index])
    outcome_close = _close_value(rows[outcome_index])
    success = outcome_close > trigger_close
    outcome_result_id = f"validation-outcome:{trial_id}"
    gate.score_outcome(outcome_result_id=outcome_result_id, success=success)

    return {
        "mode": "VALIDATION_FIRST",
        "trial_id": trial_id,
        "hypothesis_id": AAPL_HYPOTHESIS_ID,
        "cutoff": cutoff,
        "outcome_end": outcome_end,
        "trigger_close": trigger_close,
        "outcome_close": outcome_close,
        "prediction_statement": statement,
        "success": success,
        "prediction_result_id": prediction_result_id,
        "outcome_result_id": outcome_result_id,
        "audit": [audit.__dict__ for audit in session.audits],
    }


def main() -> None:
    timeout_seconds = int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600"))
    max_analyses = int(os.getenv("MTS_SOL_SMOKE_MAX_ANALYSES", "100"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    state_dir = Path(os.getenv("MTS_SOL_SMOKE_STATE_DIR", f"/home/ubuntu/mts-v4-sol-one-unseen-{stamp}"))
    state_dir.mkdir(parents=True, exist_ok=True)

    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    memory = JsonCrossSubjectScientificMemoryStore(state_dir / "cross_subject_memory.json")
    rd = _sol_rd(package_store=package_store, timeout_seconds=timeout_seconds)
    _seed_aapl_memory_if_needed(rd=rd, memory=memory)

    candidates = _candidate_subject_ids()
    selection = _select_subject(rd=rd, memory=memory, candidate_subject_ids=candidates)
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
        )
        + "\n",
        encoding="utf-8",
    )

    subject = SubjectMetadata(subject_id=selection.subject_id, ticker=_ticker(selection.subject_id))
    runtime = build_runtime(
        rd=rd,
        mission=DEFAULT_MISSION,
        nexus_path=state_dir / "research_nexus.json",
        max_contract_repairs=3,
        scientific_memory=memory,
    )
    intake = IntakeEngine(runtime.cache)
    evidence = intake.ingest(subject=subject, source=standard_live_market_source())

    validation_context: Mapping[str, object] = {"mode": "EXPLORATION"}
    if selection.mode == "VALIDATION_FIRST":
        gate = ValidationFirstSubjectGate(
            subject_id=selection.subject_id,
            hypothesis_id=selection.hypothesis_id or "",
        )
        validation_context = _run_validation_first(
            selection=selection,
            gate=gate,
            runtime=runtime,
            evidence=evidence,
            package_store=package_store,
            timeout_seconds=timeout_seconds,
        )
        if gate.phase.value != "VALIDATION_SCORED":
            raise RuntimeError("validation-first gate did not reach VALIDATION_SCORED")
        gate.release_to_exploration()

    recorder = CampaignResearchRecorder(
        package_store=package_store,
        decision_journal=JsonResearchDecisionJournal(state_dir / "rd_decisions.jsonl"),
    )
    checkpoint_store = JsonCampaignCheckpointStore(state_dir / "checkpoint.json")
    runner = CheckpointedCampaignRunner(
        orchestrator=runtime.orchestrator,
        cache=runtime.cache,
        checkpoint_store=checkpoint_store,
        research_recorder=recorder,
    )
    campaign_id = f"mts-v4-sol-one-unseen-{subject.ticker.lower()}-{stamp}"
    outcome = runner.run_new(
        campaign_id=campaign_id,
        subject=subject,
        evidence=evidence,
        max_analyses=max_analyses,
    )

    scientific_context = {
        "selection": {
            "subject_id": selection.subject_id,
            "rationale": selection.rationale,
            "mode": selection.mode,
            "hypothesis_id": selection.hypothesis_id,
        },
        "blind_validation": validation_context,
        "exploration_outcome": {
            "decisions": outcome.decisions,
            "analyses_executed": outcome.analyses_executed,
            "findings_promoted": outcome.findings_promoted,
            "closed": outcome.closed,
            "close_reason": outcome.close_reason,
            "final_research_state": outcome.final_decision.research_state,
        },
        "evidence": [item.durable_metadata() for item in evidence],
    }
    digest = SolSubjectScientificMemoryAuthor(
        rd=rd,
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
        validation_trials=1 if selection.mode == "VALIDATION_FIRST" else 0,
        close_reason=outcome.close_reason,
        zero_finding_diagnosis=(
            "No formal Finding was promoted; inspect Sol-authored subject digest and final research state for the scientific reason."
            if outcome.findings_promoted == 0
            else None
        ),
    )
    (state_dir / "subject_ledger.json").write_text(
        json.dumps(ledger.__dict__, sort_keys=True, indent=2, default=str) + "\n",
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
    print(f"DIGEST_RECORDS={len(digest.records)}", flush=True)
    print(f"FRONTIER_VERSION={digest.frontier.version if digest.frontier is not None else None}", flush=True)
    print("VALIDATION_CONTEXT=" + json.dumps(validation_context, sort_keys=True, default=str), flush=True)


if __name__ == "__main__":
    main()
