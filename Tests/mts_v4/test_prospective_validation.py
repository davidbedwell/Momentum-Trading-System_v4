from __future__ import annotations

from dataclasses import replace

import pytest

from MTS_V4.prospective_validation import (
    JsonProspectiveValidationStore,
    ProspectiveValidationError,
    ProspectiveValidationFrontier,
    ProspectiveValidationProtocol,
)
from MTS_V4.prospective_validation_authoring import decode_prospective_validation_protocol
from MTS_V4.research_package import PredictiveHypothesisRecord


def _hypothesis() -> PredictiveHypothesisRecord:
    return PredictiveHypothesisRecord(
        hypothesis_id="AMD-H001",
        statement=(
            "For AMD-like daily equity observations, an instrument closing at or above its trailing 20-session simple moving average has a higher subsequent 10-session terminal return than a contemporaneously designed comparison observation closing below that average."
        ),
        success_definition=(
            "In each blind, predeclared matched comparison trial, success occurs when the 10-session close-to-close return of the observation whose close_vs_sma_20 is at least zero exceeds the 10-session return of the matched observation whose close_vs_sma_20 is below zero. The tentative hypothesis passes only if at least 12 of the first 20 locked matched trials succeed; matching rules, observation eligibility, and non-overlap must be frozen before outcomes are exposed."
        ),
        minimum_required_trials=20,
        source_result_ids=("analysis-result:1",),
        discovered_with_lookahead=True,
    )


def _protocol() -> ProspectiveValidationProtocol:
    h = _hypothesis()
    return ProspectiveValidationProtocol(
        protocol_id="AMD-H001-PV1",
        hypothesis_id=h.hypothesis_id,
        source_subject_id="equity:AMD",
        route="FUTURE_SAME_SUBJECT",
        frozen_hypothesis_statement=h.statement,
        frozen_success_definition=h.success_definition,
        minimum_required_trials=h.minimum_required_trials,
        collection_start_utc="2026-09-12T12:00:00+00:00",
        last_historical_exposure_utc="2026-09-11T20:00:00+00:00",
        authoritative_daily_close_series="adjusted daily close from authoritative intake source",
        exchange_session_calendar="NYSE/Nasdaq US equity regular session calendar",
        corporate_action_adjustment_policy="use the frozen adjusted-close series policy",
        missing_or_corrected_data_policy="defer affected trial until authoritative corrected close is available",
        candidate_condition="close_vs_sma_20 >= 0",
        comparison_condition="close_vs_sma_20 < 0",
        matching_rule="pair observations prospectively without outcome access using the frozen matching specification",
        observation_eligibility="regular-session daily observations after collection_start_utc",
        outcome_horizon_sessions=10,
        non_overlap_scope="BETWEEN_TRIALS_ONLY",
        tie_handling="ties are failures",
        trial_ordering_rule="accept eligible matched pairs in chronological lock order until 20 trials are locked",
        outcome_embargo_rule="do not expose either terminal return before both are evaluable",
        outcome_evaluable_rule="trial becomes evaluable after both observations have ten later sessions",
    )


def test_protocol_preserves_frozen_hypothesis() -> None:
    protocol = _protocol()
    protocol.validate_against_hypothesis(_hypothesis())
    with pytest.raises(ProspectiveValidationError, match="changed frozen hypothesis statement"):
        replace(protocol, frozen_hypothesis_statement="different").validate_against_hypothesis(
            _hypothesis()
        )


def test_collection_start_must_follow_historical_exposure() -> None:
    with pytest.raises(ProspectiveValidationError, match="strictly after"):
        replace(
            _protocol(),
            collection_start_utc="2026-09-11T20:00:00+00:00",
        )


def test_decode_rejects_hypothesis_mutation() -> None:
    h = _hypothesis()
    raw = {
        "protocol_id": "AMD-H001-PV1",
        "hypothesis_id": h.hypothesis_id,
        "source_subject_id": "equity:AMD",
        "route": "FUTURE_SAME_SUBJECT",
        "frozen_hypothesis_statement": "mutated",
        "frozen_success_definition": h.success_definition,
        "minimum_required_trials": 20,
        "collection_start_utc": "2026-09-12T12:00:00+00:00",
        "authoritative_daily_close_series": "series",
        "exchange_session_calendar": "calendar",
        "corporate_action_adjustment_policy": "policy",
        "missing_or_corrected_data_policy": "policy",
        "candidate_condition": "close_vs_sma_20 >= 0",
        "comparison_condition": "close_vs_sma_20 < 0",
        "matching_rule": "rule",
        "observation_eligibility": "eligibility",
        "outcome_horizon_sessions": 10,
        "non_overlap_scope": "BETWEEN_TRIALS_ONLY",
        "tie_handling": "rule",
        "trial_ordering_rule": "rule",
        "outcome_embargo_rule": "rule",
        "outcome_evaluable_rule": "rule",
        "authored_by": "AI_RESEARCH_DIRECTOR",
    }
    import json

    with pytest.raises(ProspectiveValidationError, match="changed frozen hypothesis statement"):
        decode_prospective_validation_protocol(
            json.dumps(raw),
            hypothesis=h,
            source_subject_id="equity:AMD",
            last_historical_exposure_utc="2026-09-11T20:00:00+00:00",
        )


def test_frontier_locks_same_hypothesis_trials_and_enforces_embargo() -> None:
    h = _hypothesis()
    protocol = _protocol()
    frontier = ProspectiveValidationFrontier.arm(protocol)

    frontier, h = frontier.lock_trial(
        prediction_result_id="analysis-result:prediction-1",
        prediction_statement="candidate return will exceed comparison return",
        candidate_session_index=0,
        comparison_session_index=20,
        prediction_contains_future_information=False,
        hypothesis=h,
    )
    assert frontier.trials[0].trial_id == "AMD-H001-T01"
    assert h.trials[0].trial_id == "AMD-H001-T01"
    assert h.hypothesis_id == "AMD-H001"
    assert frontier.trials[0].evaluable_after_session_index == 30

    with pytest.raises(ProspectiveValidationError, match="outcome embargo active"):
        frontier.record_outcome(
            trial_id_value="AMD-H001-T01",
            outcome_result_id="analysis-result:outcome-1",
            success=True,
            current_session_index=29,
            hypothesis=h,
        )

    frontier, h = frontier.record_outcome(
        trial_id_value="AMD-H001-T01",
        outcome_result_id="analysis-result:outcome-1",
        success=True,
        current_session_index=30,
        hypothesis=h,
    )
    assert frontier.trials[0].state == "COMPLETED"
    assert h.success_count == 1
    assert h.status == "TENTATIVE"


def test_frontier_rejects_lookahead_and_cross_trial_overlap() -> None:
    h = _hypothesis()
    frontier = ProspectiveValidationFrontier.arm(_protocol())
    with pytest.raises(ProspectiveValidationError, match="cannot contain future information"):
        frontier.lock_trial(
            prediction_result_id="analysis-result:prediction-bad",
            prediction_statement="bad",
            candidate_session_index=0,
            comparison_session_index=20,
            prediction_contains_future_information=True,
            hypothesis=h,
        )

    frontier, h = frontier.lock_trial(
        prediction_result_id="analysis-result:prediction-1",
        prediction_statement="p1",
        candidate_session_index=0,
        comparison_session_index=20,
        prediction_contains_future_information=False,
        hypothesis=h,
    )
    with pytest.raises(ProspectiveValidationError, match="overlap prior trial"):
        frontier.lock_trial(
            prediction_result_id="analysis-result:prediction-2",
            prediction_statement="p2",
            candidate_session_index=5,
            comparison_session_index=35,
            prediction_contains_future_information=False,
            hypothesis=h,
        )


def test_store_round_trip_preserves_protocol_fingerprint(tmp_path) -> None:
    protocol = _protocol()
    frontier = ProspectiveValidationFrontier.arm(protocol)
    store = JsonProspectiveValidationStore(tmp_path / "amd_h001.json")
    store.save(protocol=protocol, frontier=frontier)
    loaded_protocol, loaded_frontier = store.load()
    assert loaded_protocol == protocol
    assert loaded_frontier == frontier
    assert loaded_frontier.protocol_fingerprint == protocol.fingerprint
