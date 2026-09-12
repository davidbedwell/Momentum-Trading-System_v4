from __future__ import annotations

from datetime import date, timedelta

import pytest

from MTS_V4.prospective_outcome_vault import (
    generate_vault_key,
    release_collective_outcomes,
    seal_available_outcomes,
)
from MTS_V4.prospective_validation import (
    JsonProspectiveValidationStore,
    ProspectiveValidationError,
    ProspectiveValidationFrontier,
    ProspectiveValidationProtocol,
)
from MTS_V4.prospective_validation_runtime import AuthoritativeSession
from MTS_V4.research_package import PredictiveHypothesisRecord, ResearchPackage
from MTS_V4.research_package_store import JsonResearchPackageStore


def _protocol() -> ProspectiveValidationProtocol:
    statement = "AMD H001 frozen statement"
    success = "AMD H001 frozen success definition"
    return ProspectiveValidationProtocol(
        protocol_id="AMD-H001-FUTURE-SAME-SUBJECT-PBV-V1-20260912",
        hypothesis_id="AMD-H001",
        source_subject_id="equity:AMD",
        route="FUTURE_SAME_SUBJECT",
        frozen_hypothesis_statement=statement,
        frozen_success_definition=success,
        minimum_required_trials=20,
        collection_start_utc="2026-09-12T00:00:00Z",
        last_historical_exposure_utc="2026-09-11T23:59:59Z",
        authoritative_daily_close_series=(
            "Nasdaq official NOCP. SMA20_t uses the immediately preceding 19 Nasdaq sessions."
        ),
        exchange_session_calendar="Official XNAS calendar.",
        corporate_action_adjustment_policy="Exact mandatory multipliers.",
        missing_or_corrected_data_policy=(
            "Terminal record finalized on the fifth Nasdaq session after the terminal session."
        ),
        candidate_condition="Value is greater than or equal to zero.",
        comparison_condition="Value is less than zero.",
        matching_rule="Examine the next nine Nasdaq sessions.",
        observation_eligibility="Frozen official inputs.",
        outcome_horizon_sessions=10,
        non_overlap_scope="BETWEEN_TRIALS_ONLY",
        tie_handling="Equality fails.",
        trial_ordering_rule="First 20 locked pairs.",
        outcome_embargo_rule=(
            "No validation outcome may be decrypted, queried, displayed, exported, or used before collective release."
        ),
        outcome_evaluable_rule=(
            "Terminal is the tenth subsequent Nasdaq session after t; final cutoff is the fifth XNAS session after u."
        ),
    )


def _weekdays(start: date, count: int) -> list[date]:
    result = []
    current = start
    while len(result) < count:
        if current.weekday() < 5:
            result.append(current)
        current += timedelta(days=1)
    return result


def _locked_state(protocol: ProspectiveValidationProtocol):
    hypothesis = PredictiveHypothesisRecord(
        hypothesis_id=protocol.hypothesis_id,
        statement=protocol.frozen_hypothesis_statement,
        success_definition=protocol.frozen_success_definition,
        minimum_required_trials=20,
    )
    frontier = ProspectiveValidationFrontier.arm(protocol)
    for ordinal in range(20):
        base = 30 + ordinal * 25
        frontier, hypothesis = frontier.lock_trial(
            prediction_result_id=f"lock-{ordinal + 1}",
            prediction_statement=f"locked trial {ordinal + 1}",
            candidate_session_index=base,
            comparison_session_index=base + 1,
            prediction_contains_future_information=False,
            hypothesis=hypothesis,
        )
    return frontier, hypothesis


def _sessions() -> tuple[AuthoritativeSession, ...]:
    dates = _weekdays(date(2026, 8, 3), 540)
    closes = {index: "100" for index in range(len(dates))}
    for ordinal in range(20):
        base = 30 + ordinal * 25
        closes[base] = "100"
        closes[base + 1] = "100"
        closes[base + 10] = "110" if ordinal < 12 else "90"
        closes[base + 11] = "100"
    return tuple(
        AuthoritativeSession(
            session_index=index,
            session_date=session_date.isoformat(),
            source_subject_id="equity:AMD",
            source_identity="NASDAQ_NOCP",
            nocp=closes[index],
            mandatory_share_multiplier="1",
        )
        for index, session_date in enumerate(dates)
    )


def test_collective_outcomes_are_encrypted_then_released_all_at_once(tmp_path):
    protocol = _protocol()
    frontier, hypothesis = _locked_state(protocol)
    validation_store = JsonProspectiveValidationStore(tmp_path / "validation.json")
    validation_store.save(protocol=protocol, frontier=frontier)

    rp_store = JsonResearchPackageStore(tmp_path / "rps")
    rp_store.create(
        ResearchPackage(
            rp_id="RP-AMD-005",
            subject_id="equity:AMD",
            campaign_id="test",
            originating_question="validate",
            originating_rationale="frozen protocol",
            predictive_hypotheses=(hypothesis,),
        )
    )
    vault = tmp_path / "vault.json"
    key = generate_vault_key()
    seal = seal_available_outcomes(
        validation_store=validation_store,
        sessions=_sessions(),
        as_of_utc="2029-12-31T23:00:00Z",
        vault_path=vault,
        vault_key=key,
    )
    assert seal.locked_trials == 20
    assert seal.sealed_trials == 20
    assert seal.release_ready is True
    ciphertext_document = vault.read_text()
    assert '"success"' not in ciphertext_document
    assert "candidate_return" not in ciphertext_document
    assert "comparison_return" not in ciphertext_document

    before = rp_store.load("RP-AMD-005")
    assert before is not None
    before_h = before.predictive_hypotheses[0]
    assert before_h.success_count == 0
    assert before_h.failure_count == 0
    assert before_h.success_rate is None

    released = release_collective_outcomes(
        validation_store=validation_store,
        research_package_store=rp_store,
        rp_id="RP-AMD-005",
        vault_path=vault,
        vault_key=key,
    )
    assert released.status == "RELEASED"
    assert released.completed_trials == 20
    assert released.success_count == 12
    assert released.failure_count == 8
    assert released.success_rate == 0.60
    assert released.hypothesis_status == "VERIFIED"


def test_collective_release_refuses_before_all_twenty_trials_are_locked(tmp_path):
    protocol = _protocol()
    frontier, hypothesis = _locked_state(protocol)
    frontier = ProspectiveValidationFrontier(
        protocol_id=frontier.protocol_id,
        protocol_fingerprint=frontier.protocol_fingerprint,
        hypothesis_id=frontier.hypothesis_id,
        source_subject_id=frontier.source_subject_id,
        required_trials=frontier.required_trials,
        outcome_horizon_sessions=frontier.outcome_horizon_sessions,
        non_overlap_scope=frontier.non_overlap_scope,
        state="IN_PROGRESS",
        trials=frontier.trials[:19],
    )
    hypothesis = PredictiveHypothesisRecord(
        hypothesis_id=hypothesis.hypothesis_id,
        statement=hypothesis.statement,
        success_definition=hypothesis.success_definition,
        minimum_required_trials=hypothesis.minimum_required_trials,
        trials=hypothesis.trials[:19],
    )
    validation_store = JsonProspectiveValidationStore(tmp_path / "validation.json")
    validation_store.save(protocol=protocol, frontier=frontier)
    rp_store = JsonResearchPackageStore(tmp_path / "rps")
    rp_store.create(
        ResearchPackage(
            rp_id="RP-AMD-005",
            subject_id="equity:AMD",
            campaign_id="test",
            originating_question="validate",
            originating_rationale="frozen protocol",
            predictive_hypotheses=(hypothesis,),
        )
    )
    with pytest.raises(ProspectiveValidationError, match="fewer than 20 trials locked"):
        release_collective_outcomes(
            validation_store=validation_store,
            research_package_store=rp_store,
            rp_id="RP-AMD-005",
            vault_path=tmp_path / "vault.json",
            vault_key=generate_vault_key(),
        )
