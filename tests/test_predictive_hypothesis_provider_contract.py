from __future__ import annotations

import json

from MTS_V4.blind_validation import BlindValidationResearchDirector
from MTS_V4.bootstrap import DEFAULT_MISSION
from MTS_V4.research_package_provider import ResearchPackageAwareResearchDirector


def _payload():
    return {
        "subject": {"subject_id": "equity:AAPL", "ticker": "AAPL"},
        "evidence": [],
        "available_analysis_methods": [],
        "objective_execution_requirements": {},
        "nexus_context": {},
    }


def test_rd_is_told_tentative_blind_validation_lock_and_point_six_rule():
    messages = ResearchPackageAwareResearchDirector._decision_messages(
        operation="INTERPRET_ANALYSIS_RESULT",
        mission=DEFAULT_MISSION,
        payload=_payload(),
    )
    user = json.loads(messages[1]["content"])
    instructions = "\n".join(user["instructions"])

    assert "CREATE_TENTATIVE" in instructions
    assert "LOCK_VALIDATION_TRIAL" in instructions
    assert "RECORD_VALIDATION_OUTCOME" in instructions
    assert "research_phase=VALIDATION" in instructions
    assert "without look-ahead knowledge" in instructions
    assert "before any future outcome is exposed" in instructions
    assert "success_rate >= 0.60" in instructions
    assert "NOT_VERIFIED" in instructions
    assert "minimum_required_trials" in instructions

    updates_schema = user["required_decision_schema"]["research_state"][
        "predictive_hypothesis_updates"
    ]
    assert updates_schema[0]["action"] == (
        "CREATE_TENTATIVE, LOCK_VALIDATION_TRIAL, or RECORD_VALIDATION_OUTCOME"
    )


def test_production_rd_is_explicitly_directed_toward_prospective_discovery():
    messages = ResearchPackageAwareResearchDirector._decision_messages(
        operation="BEGIN_RESEARCH",
        mission=DEFAULT_MISSION,
        payload=_payload(),
    )
    system = messages[0]["content"]
    user = json.loads(messages[1]["content"])
    instructions = "\n".join(user["instructions"])

    assert "observable at time T" in DEFAULT_MISSION
    assert "subsequent market behavior at T+1 onward" in DEFAULT_MISSION
    assert "actively seek scientifically defensible prospective structure" in DEFAULT_MISSION
    assert "prospective predictive discovery" in system
    assert "Historical look-ahead is a legitimate exploratory discovery tool" in system
    assert "Do not stop at contemporaneous description" in system
    assert "central scientific objective of MTS" in instructions
    assert "Historical look-ahead is explicitly allowed during EXPLORATION" in instructions
    assert "Do not manufacture a predictive relationship" in instructions
    assert "Never generalize validation restrictions backward into EXPLORATION" in instructions


def test_blind_rd_keeps_prediction_stage_strictly_no_lookahead():
    rd = BlindValidationResearchDirector(
        trial_id="trial:1",
        hypothesis_id="H-1",
        hypothesis_statement="Condition A predicts expansion.",
        success_definition="Frozen target is reached within frozen horizon.",
        base_url="http://example.invalid",
        model="test-model",
    )
    messages = rd._decision_messages(
        operation="BEGIN_RESEARCH",
        mission=DEFAULT_MISSION,
        payload=_payload(),
    )
    system = messages[0]["content"]
    user = json.loads(messages[1]["content"])
    instructions = "\n".join(user["instructions"])

    assert user["blind_validation"]["future_outcomes_available"] is False
    assert user["blind_validation"]["exploratory_rp_history_available"] is False
    assert "historical blind-validation prediction stage" in instructions
    assert "no later outcome information is available" in instructions
    assert "Do not revise that hypothesis" in instructions
    assert "Only pre-cutoff evidence is available" in system
