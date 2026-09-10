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


def test_predictive_hypothesis_uses_governed_point_six_threshold_after_minimum_trials():
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
        hypothesis = hypothesis.record_validation_trial(
            PredictiveValidationTrialRecord(
                trial_id=f"T-{index}",
                result_id=f"analysis-result:{index}",
                success=success,
                research_phase="VALIDATION",
                contains_future_information=False,
            )
        )
    assert hypothesis.status == PREDICTIVE_STATUS_TENTATIVE
    assert hypothesis.success_rate == 0.5

    hypothesis = hypothesis.record_validation_trial(
        PredictiveValidationTrialRecord(
            trial_id="T-5",
            result_id="analysis-result:5",
            success=True,
            research_phase="VALIDATION",
            contains_future_information=False,
        )
    )
    assert hypothesis.success_count == 3
    assert hypothesis.failure_count == 2
    assert hypothesis.success_rate == 0.60
    assert hypothesis.status == PREDICTIVE_STATUS_VERIFIED


def test_predictive_hypothesis_is_not_verified_below_point_six_after_minimum_trials():
    hypothesis = PredictiveHypothesisRecord(
        hypothesis_id="H-2",
        statement="Condition B predicts reversal.",
        success_definition="The frozen reversal condition is satisfied.",
        minimum_required_trials=5,
    )
    for index, success in enumerate([True, False, False, True, False], start=1):
        hypothesis = hypothesis.record_validation_trial(
            PredictiveValidationTrialRecord(
                trial_id=f"T-{index}",
                result_id=f"analysis-result:{index}",
                success=success,
                research_phase="VALIDATION",
                contains_future_information=False,
            )
        )
    assert hypothesis.success_rate == 0.4
    assert hypothesis.status == PREDICTIVE_STATUS_NOT_VERIFIED


def test_predictive_verification_rejects_lookahead_or_nonvalidation_trials():
    hypothesis = PredictiveHypothesisRecord(
        hypothesis_id="H-3",
        statement="Condition C predicts continuation.",
        success_definition="The frozen continuation condition is satisfied.",
        minimum_required_trials=1,
    )
    with pytest.raises(ResearchPackageError, match="VALIDATION"):
        hypothesis.record_validation_trial(
            PredictiveValidationTrialRecord(
                trial_id="T-explore",
                result_id="analysis-result:explore",
                success=True,
                research_phase="EXPLORATION",
                contains_future_information=False,
            )
        )
    with pytest.raises(ResearchPackageError, match="look-ahead"):
        hypothesis.record_validation_trial(
            PredictiveValidationTrialRecord(
                trial_id="T-lookahead",
                result_id="analysis-result:lookahead",
                success=True,
                research_phase="VALIDATION",
                contains_future_information=True,
            )
        )


def _request(*, request_id: str, question_id: str, phase: ResearchPhase) -> AnalysisRequest:
    return AnalysisRequest(
        request_id=request_id,
        subject_id="equity:AAPL",
        question="Test the frozen predictive proposition.",
        method_id="analysis.descriptive.statistics",
        evidence_ids=("evidence:equity:AAPL:1",),
        parameters={"column": "close"},
        research_phase=phase,
        rationale="RD-authored rationale",
        rp_id="RP-PREDICTIVE",
        question_id=question_id,
    )


def test_recorder_freezes_tentative_hypothesis_and_counts_only_blind_validation_trials(tmp_path):
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

    first_validation_request = _request(
        request_id="req:validation:1",
        question_id="Q-validation-1",
        phase=ResearchPhase.VALIDATION,
    )
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=ResearchDecision(
            continue_research=True,
            next_request=first_validation_request,
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
    current_request_id = "req:validation:1"
    for index, success in enumerate(outcomes, start=1):
        next_request = None
        continue_research = index < len(outcomes)
        if continue_research:
            next_request = _request(
                request_id=f"req:validation:{index + 1}",
                question_id=f"Q-validation-{index + 1}",
                phase=ResearchPhase.VALIDATION,
            )
        recorder.record_decision(
            campaign_id="campaign:aapl",
            subject=subject,
            decision=ResearchDecision(
                continue_research=continue_research,
                next_request=next_request,
                rp_id="RP-PREDICTIVE",
                close_reason=None if continue_research else "validation complete",
                analysis_interpretation="Blind validation trial interpreted against frozen success definition.",
                interpreted_request_id=current_request_id,
                interpreted_result_id=f"analysis-result:validation:{index}",
                interpreted_execution_status="SUCCESS",
                interpreted_future_information={"contains_future_information": False},
                research_state={
                    "predictive_hypothesis_updates": [
                        {
                            "action": "RECORD_VALIDATION_TRIAL",
                            "hypothesis_id": "H-AAPL-1",
                            "trial_id": f"trial:{index}",
                            "result_id": f"analysis-result:validation:{index}",
                            "success": success,
                        }
                    ]
                },
            ),
            decision_sequence=index + 2,
            analyses_executed=index + 1,
        )
        current_request_id = f"req:validation:{index + 1}"

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
    assert package.status == "CLOSED"
