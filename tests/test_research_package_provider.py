from __future__ import annotations

import json

from MTS_V4.contracts import AnalysisRequest, ResearchDecision, ResearchPhase
from MTS_V4.research_package import ResearchAnalysisRecord, ResearchPackage, ResearchQuestionRecord
from MTS_V4.research_package_provider import ResearchPackageAwareResearchDirector
from MTS_V4.research_package_store import JsonResearchPackageStore


def _request(*, rp_id: str, question_id: str, parent_question_id=None, parent_rp_id=None, request_id="req:1"):
    return AnalysisRequest(
        request_id=request_id,
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


class _RepairSequenceProvider(ResearchPackageAwareResearchDirector):
    def __init__(self, *, store, responses):
        super().__init__(
            research_package_store=store,
            base_url="http://example.invalid",
            model="test-model",
        )
        self._responses = iter(responses)
        self.messages_seen = []

    def _chat_completion(self, messages):
        self.messages_seen.append(messages)
        return next(self._responses)


def _decision_json(*, parent_rp_id, request_id="req:next"):
    return json.dumps(
        {
            "continue_research": True,
            "rp_id": "RP-0001",
            "analysis_interpretation": "Observed result motivates another question.",
            "next_request": {
                "request_id": request_id,
                "subject_id": "equity:AAPL",
                "question": "Next AI-authored question",
                "method_id": "analysis.descriptive.statistics",
                "evidence_ids": ["evidence:equity:AAPL:1"],
                "analysis_inputs": [],
                "parameters": {"column": "close"},
                "research_phase": "EXPLORATION",
                "rationale": "AI-authored rationale",
                "rp_id": "RP-0001",
                "question_id": "Q-0002",
                "parent_question_id": "Q-0001",
                "parent_rp_id": parent_rp_id,
            },
            "promote_findings": [],
            "research_state": {},
            "close_reason": None,
        }
    )


def test_rp_representation_repair_can_survive_repeated_same_defect(tmp_path):
    malformed = _decision_json(parent_rp_id="RP-0001")
    valid = _decision_json(parent_rp_id=None)
    provider = _RepairSequenceProvider(
        store=JsonResearchPackageStore(tmp_path / "research_packages"),
        responses=[malformed, malformed, valid],
    )

    decision = provider._request_decision(
        operation="INTERPRET_ANALYSIS_RESULT",
        mission="test",
        payload={
            "subject": {"subject_id": "equity:AAPL"},
            "analysis_request": {"rp_id": "RP-0001"},
        },
    )

    assert decision.next_request is not None
    assert decision.next_request.parent_rp_id is None
    assert len(provider.messages_seen) == 3
    repair_messages = provider.messages_seen[1]
    assert repair_messages[-2]["role"] == "assistant"
    assert '"parent_rp_id":"RP-0001"' in repair_messages[-2]["content"]
    assert "parent_rp_id may not equal rp_id" in repair_messages[-1]["content"]


def _store_with_used_request(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    package = ResearchPackage(
        rp_id="RP-0001",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Initial question",
        originating_rationale="Initial rationale",
    )
    store.create(package)
    package = package.append_question(
        ResearchQuestionRecord(
            question_id="Q-0001",
            question="Initial question",
            rationale="Initial rationale",
            research_phase="EXPLORATION",
        )
    )
    package = package.append_analysis(
        ResearchAnalysisRecord(
            request_id="req001",
            question_id="Q-0001",
            method_id="analysis.dataset.compose",
            parameters={"join_type": "INNER"},
            evidence_ids=("evidence:equity:AAPL:1",),
            analysis_inputs=(),
        )
    )
    store.save(package)
    return store


def test_durable_request_id_reuse_is_rejected_before_new_execution(tmp_path):
    store = _store_with_used_request(tmp_path)
    provider = _RepairSequenceProvider(store=store, responses=[])
    decision = ResearchDecision(
        continue_research=True,
        rp_id="RP-0001",
        analysis_interpretation="The failed attempt requires corrected parameters.",
        next_request=_request(
            rp_id="RP-0001",
            question_id="Q-0001",
            request_id="req001",
        ),
    )

    defect = provider._decision_representation_defect(
        "INTERPRET_ANALYSIS_RESULT",
        decision,
        {"analysis_request": {"rp_id": "RP-0001"}},
    )

    assert defect == (
        "next_request.request_id has already been durably used; every new Analysis "
        "execution attempt requires a new request_id: req001"
    )


def test_fresh_request_id_is_accepted_for_revised_execution_attempt(tmp_path):
    store = _store_with_used_request(tmp_path)
    provider = _RepairSequenceProvider(store=store, responses=[])
    decision = ResearchDecision(
        continue_research=True,
        rp_id="RP-0001",
        analysis_interpretation="The failed attempt requires corrected parameters.",
        next_request=_request(
            rp_id="RP-0001",
            question_id="Q-0001",
            request_id="req002",
        ),
    )

    defect = provider._decision_representation_defect(
        "INTERPRET_ANALYSIS_RESULT",
        decision,
        {"analysis_request": {"rp_id": "RP-0001"}},
    )

    assert defect is None
