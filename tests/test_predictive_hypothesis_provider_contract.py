from __future__ import annotations

import json

from MTS_V4.research_package_provider import ResearchPackageAwareResearchDirector


def test_rd_is_told_tentative_blind_validation_lock_and_point_six_rule():
    messages = ResearchPackageAwareResearchDirector._decision_messages(
        operation="INTERPRET_ANALYSIS_RESULT",
        mission="discover reproducible predictive market conditions",
        payload={
            "subject": {"subject_id": "equity:AAPL", "ticker": "AAPL"},
            "evidence": [],
            "available_analysis_methods": [],
            "objective_execution_requirements": {},
            "nexus_context": {},
        },
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
