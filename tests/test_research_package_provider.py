from __future__ import annotations

from MTS_V4.contracts import AnalysisRequest, ResearchDecision, ResearchPhase
from MTS_V4.research_package_provider import ResearchPackageAwareResearchDirector


def _request(*, rp_id: str, question_id: str, parent_question_id=None, parent_rp_id=None):
    return AnalysisRequest(
        request_id="req:1",
        subject_id="equity:AAPL",
        question="AI-authored question",
        method_id="analysis.descriptive.statistics",
        evidence_ids=("evidence:equity:AAPL:1",),
        parameters={"column": "close"},
        research_phase=ResearchPhase.EXPLORATION,
        rationale="AI-authored rationale",
        rp_id=rp_id,
        question_id=question_id,
        parent_question_id=parent_question_id,
        parent_rp_id=parent_rp_id,
    )


def test_self_parent_question_is_objective_lineage_defect():
    decision = ResearchDecision(
        continue_research=True,
        rp_id="RP-0001",
        next_request=_request(
            rp_id="RP-0001",
            question_id="Q-0001",
            parent_question_id="Q-0001",
        ),
    )

    defect = ResearchPackageAwareResearchDirector._rp_representation_defect(
        "INTERPRET_ANALYSIS_RESULT",
        decision,
        {"analysis_request": {"rp_id": "RP-0001"}},
    )

    assert defect == "parent_question_id may not equal question_id"


def test_self_parent_rp_is_objective_lineage_defect():
    decision = ResearchDecision(
        continue_research=True,
        rp_id="RP-0001",
        next_request=_request(
            rp_id="RP-0001",
            question_id="Q-0002",
            parent_question_id="Q-0001",
            parent_rp_id="RP-0001",
        ),
    )

    defect = ResearchPackageAwareResearchDirector._rp_representation_defect(
        "INTERPRET_ANALYSIS_RESULT",
        decision,
        {"analysis_request": {"rp_id": "RP-0001"}},
    )

    assert defect == "parent_rp_id may not equal rp_id"


def test_valid_followup_lineage_is_not_rejected():
    decision = ResearchDecision(
        continue_research=True,
        rp_id="RP-0001",
        analysis_interpretation="The result motivates a follow-up.",
        next_request=_request(
            rp_id="RP-0001",
            question_id="Q-0002",
            parent_question_id="Q-0001",
            parent_rp_id=None,
        ),
    )

    defect = ResearchPackageAwareResearchDirector._rp_representation_defect(
        "INTERPRET_ANALYSIS_RESULT",
        decision,
        {"analysis_request": {"rp_id": "RP-0001"}},
    )

    assert defect is None
