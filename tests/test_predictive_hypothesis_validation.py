from __future__ import annotations

import pytest

from MTS_V4.contracts import AnalysisRequest, ResearchDecision, ResearchPhase, SubjectMetadata
from MTS_V4.decision_journal import JsonResearchDecisionJournal
from MTS_V4.research_package import (
    PREDICTIVE_STATUS_NOT_VERIFIED,
    PREDICTIVE_STATUS_TENTATIVE,
    PREDICTIVE_STATUS_VERIFIED,
    PREDICTIVE_VERIFICATION_SUCCESS_THRESHOLD,
    PredictiveHypothesisRecord,
    PredictiveValidationTrialRecord,
    ResearchPackageError,
)
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.research_recording import CampaignResearchRecorder


def _locked_trial(index: int) -> PredictiveValidationTrialRecord:
    return PredictiveValidationTrialRecord(
        trial_id=f"T-{index}",
        prediction_result_id=f"analysis-result:prediction:{index}",
        prediction_statement="The frozen hypothesis predicts success for this blind trial.",
        prediction_research_phase="VALIDATION",
        prediction_contains_future_information=False,
    )


def test_predictive_hypothesis_uses_governed_point_six_threshold_after_completed_trials():
    hypothesis = PredictiveHypothesisRecord(
        hypothesis_id="H-1",
        statement="Condition A predicts upward expansion.",
        success_definition="Price rises by the predeclared target within the predeclared horizon.",
        minimum_required_trials=5,
    )
    assert hypothesis.status == PREDICTIVE_STATUS_TENTATIVE
    assert hypothesis.verification_success_threshold == PREDICTIVE_VERIFICATION_SUCCESS_THRESHOLD
    assert hypothesis.verification_success_threshold == 0.60

    outcomes = [True, False, True, False]
    for index, success in enumerate(outcomes, start=1):
        hypothesis = hypothesis.lock_validation_trial(_locked_trial(index))
        hypothesis = hypothesis.record_validation_outcome(
            trial_id=f"T-{index}",
            outcome_result_id=f"analysis-result:outcome:{index}",
            success=success,
            outcome_contains_future_information=True,
        )
    assert hypothesis.status == PREDICTIVE_STATUS_TENTATIVE
    assert hypothesis.success_rate == 0.5

    hypothesis = hypothesis.lock_validation_trial(_locked_trial(5))
    hypothesis = hypothesis.record_validation_outcome(
        trial_id="T-5",
        outcome_result_id="analysis-result:outcome:5",
        success=True,
        outcome_contains_future_information=True,
    )
    assert hypothesis.success_count == 3
    assert hypothesis.failure_count == 2
    assert hypothesis.success_rate == 0.60
    assert hypothesis.status == PREDICTIVE_STATUS_VERIFIED


def test_predictive_hypothesis_is_not_verified_below_point_six_after_minimum_completed_trials():
    hypothesis = PredictiveHypothesisRecord(
        hypothesis_id="H-2",
        statement="Condition B predicts reversal.",
        success_definition="The frozen reversal condition is satisfied.",
        minimum_required_trials=5,
    )
    for index, success in enumerate([True, False, False, True, False], start=1):
        hypothesis = hypothesis.lock_validation_trial(_locked_trial(index))
        hypothesis = hypothesis.record_validation_outcome(
            trial_id=f"T-{index}",
            outcome_result_id=f"analysis-result:outcome:{index}",
            success=success,
            outcome_contains_future_information=True,
        )
    assert hypothesis.success_rate == 0.4
    assert hypothesis.status == PREDICTIVE_STATUS_NOT_VERIFIED


def test_prediction_lock_rejects_lookahead_or_nonvalidation_prediction():
    hypothesis = PredictiveHypothesisRecord(
        hypothesis_id="H-3",
        statement="Condition C predicts continuation.",
        success_definition="The frozen continuation condition is satisfied.",
        minimum_required_trials=1,
    )
    with pytest.raises(ResearchPackageError, match="VALIDATION"):
        hypothesis.lock_validation_trial(
            PredictiveValidationTrialRecord(
                trial_id="T-explore",
                prediction_result_id="analysis-result:explore",
                prediction_statement="Predict success.",
                prediction_research_phase="EXPLORATION",
                prediction_contains_future_information=False,
            )
        )
    with pytest.raises(ResearchPackageError, match="look-ahead"):
        hypothesis.lock_validation_trial(
            PredictiveValidationTrialRecord(
                trial_id="T-lookahead",
                prediction_result_id="analysis-result:lookahead",
                prediction_statement="Predict success.",
                prediction_research_phase="VALIDATION",
                prediction_contains_future_information=True,
            )
        )


def test_future_information_is_allowed_only_after_prediction_is_locked():
    hypothesis = PredictiveHypothesisRecord(
        hypothesis_id="H-4",
        statement="Condition D predicts expansion.",
        success_definition="The frozen expansion condition is satisfied.",
        minimum_required_trials=1,
    )
    hypothesis = hypothesis.lock_validation_trial(_locked_trial(1))
    hypothesis = hypothesis.record_validation_outcome(
        trial_id="T-1",
        outcome_result_id="analysis-result:future-outcome",
        success=True,
        outcome_contains_future_information=True,
    )
    assert hypothesis.trials[0].prediction_contains_future_information is False
    assert hypothesis.trials[0].outcome_contains_future_information is True
    assert hypothesis.status == PREDICTIVE_STATUS_VERIFIED


def _request(
    *,
    request_id: str,
    question_id: str,
    phase: ResearchPhase,
    question: str,
) -> AnalysisRequest:
    return AnalysisRequest(
        request_id=request_id,
        subject_id="equity:AAPL",
        question=question,
        method_id="analysis.descriptive.statistics",
        evidence_ids=("evidence:equity:AAPL:1",),
        parameters={"columns": ["close"]},
        research_phase=phase,
        rationale="RD-authored rationale",
        rp_id="RP-PREDICTIVE",
        question_id=question_id,
    )


def test_recorder_freezes_hypothesis_locks_blind_predictions_then_scores_outcomes(tmp_path):
    packages = JsonResearchPackageStore(tmp_path / "research_packages")
    recorder = CampaignResearchRecorder(
        package_store=packages,
        decision_journal=JsonResearchDecisionJournal(tmp_path / "rd_decisions.jsonl"),
    )
    subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")

    exploration_request = _request(
        request_id="req:explore",
        question_id="Q-explore",
        phase=ResearchPhase.EXPLORATION,
        question="Discover a candidate predictive relationship.",
    )
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=ResearchDecision(
            continue_research=True,
            next_request=exploration_request,
            rp_id="RP-PREDICTIVE",
        ),
        decision_sequence=1,
        analyses_executed=0,
    )

    first_prediction_request = _request(
        request_id="req:prediction:1",
        question_id="Q-prediction-1",
        phase=ResearchPhase.VALIDATION,
        question="Apply the frozen hypothesis without future knowledge.",
    )
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=ResearchDecision(
            continue_research=True,
            next_request=first_prediction_request,
            rp_id="RP-PREDICTIVE",
            analysis_interpretation="Exploration produced a candidate predictive relationship.",
            interpreted_request_id="req:explore",
            interpreted_result_id="analysis-result:explore",
            interpreted_execution_status="SUCCESS",
            interpreted_future_information={"contains_future_information": True},
            research_state={
                "predictive_hypothesis_updates": [
                    {
                        "action": "CREATE_TENTATIVE",
                        "hypothesis_id": "H-AAPL-1",
                        "statement": "Frozen condition predicts the frozen outcome.",
                        "success_definition": "The predeclared outcome occurs within the predeclared horizon.",
                        "minimum_required_trials": 5,
                        "source_result_ids": ["analysis-result:explore"],
                    }
                ]
            },
        ),
        decision_sequence=2,
        analyses_executed=1,
    )

    outcomes = [True, False, True, False, True]
    sequence = 3
    analyses_executed = 2
    for index, success in enumerate(outcomes, start=1):
        outcome_request = _request(
            request_id=f"req:outcome:{index}",
            question_id=f"Q-outcome-{index}",
            phase=ResearchPhase.EXPLORATION,
            question="Evaluate the already-locked prediction using the subsequent outcome.",
        )
        lock_decision = ResearchDecision(
            continue_research=True,
            next_request=outcome_request,
            rp_id="RP-PREDICTIVE",
            analysis_interpretation="No-lookahead evidence supports locking the trial prediction.",
            interpreted_request_id=f"req:prediction:{index}",
            interpreted_result_id=f"analysis-result:prediction:{index}",
            interpreted_execution_status="SUCCESS",
            interpreted_future_information={"contains_future_information": False},
            research_state={
                "predictive_hypothesis_updates": [
                    {
                        "action": "LOCK_VALIDATION_TRIAL",
                        "hypothesis_id": "H-AAPL-1",
                        "trial_id": f"trial:{index}",
                        "prediction_result_id": f"analysis-result:prediction:{index}",
                        "prediction_statement": "The frozen hypothesis predicts success for this trial.",
                    }
                ]
            },
        )
        recorder.record_decision(
            campaign_id="campaign:aapl",
            subject=subject,
            decision=lock_decision,
            decision_sequence=sequence,
            analyses_executed=analyses_executed,
        )
        # The same scientific decision may be checkpointed again after execution
        # of its next request. The prediction lock must remain idempotent.
        recorder.record_decision(
            campaign_id="campaign:aapl",
            subject=subject,
            decision=lock_decision,
            decision_sequence=sequence,
            analyses_executed=analyses_executed + 1,
        )
        sequence += 1
        analyses_executed += 1

        continue_research = index < len(outcomes)
        next_prediction_request = None
        if continue_research:
            next_prediction_request = _request(
                request_id=f"req:prediction:{index + 1}",
                question_id=f"Q-prediction-{index + 1}",
                phase=ResearchPhase.VALIDATION,
                question="Apply the frozen hypothesis without future knowledge.",
            )
        outcome_decision = ResearchDecision(
            continue_research=continue_research,
            next_request=next_prediction_request,
            rp_id="RP-PREDICTIVE",
            close_reason=None if continue_research else "blind validation complete",
            analysis_interpretation="Outcome evaluated against the frozen success definition.",
            interpreted_request_id=f"req:outcome:{index}",
            interpreted_result_id=f"analysis-result:outcome:{index}",
            interpreted_execution_status="SUCCESS",
            interpreted_future_information={"contains_future_information": True},
            research_state={
                "predictive_hypothesis_updates": [
                    {
                        "action": "RECORD_VALIDATION_OUTCOME",
                        "hypothesis_id": "H-AAPL-1",
                        "trial_id": f"trial:{index}",
                        "outcome_result_id": f"analysis-result:outcome:{index}",
                        "success": success,
                    }
                ]
            },
        )
        recorder.record_decision(
            campaign_id="campaign:aapl",
            subject=subject,
            decision=outcome_decision,
            decision_sequence=sequence,
            analyses_executed=analyses_executed,
        )
        sequence += 1
        analyses_executed += 1

    package = packages.load("RP-PREDICTIVE")
    assert package is not None
    assert len(package.predictive_hypotheses) == 1
    hypothesis = package.predictive_hypotheses[0]
    assert hypothesis.discovered_with_lookahead is True
    assert hypothesis.minimum_required_trials == 5
    assert hypothesis.success_count == 3
    assert hypothesis.failure_count == 2
    assert hypothesis.success_rate == 0.60
    assert hypothesis.status == PREDICTIVE_STATUS_VERIFIED
    assert all(
        trial.prediction_contains_future_information is False
        for trial in hypothesis.trials
    )
    assert all(trial.outcome_result_id is not None for trial in hypothesis.trials)
    assert package.status == "CLOSED"
