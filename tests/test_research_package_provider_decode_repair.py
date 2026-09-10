from __future__ import annotations

import json

from MTS_V4.research_package_provider import ResearchPackageAwareResearchDirector
from MTS_V4.research_package_store import JsonResearchPackageStore


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


def _decision_json(*, parent_rp_id):
    return json.dumps(
        {
            "continue_research": True,
            "rp_id": "RP-0001",
            "analysis_interpretation": "Observed result motivates another question.",
            "next_request": {
                "request_id": "req:next",
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


def test_malformed_json_during_rp_repair_gets_another_ai_repair_attempt(tmp_path):
    initial_with_lineage_defect = _decision_json(parent_rp_id="RP-0001")
    malformed_repair = '{"continue_research": true, "rp_id": "RP-0001", bad_json}'
    valid = _decision_json(parent_rp_id=None)

    provider = _RepairSequenceProvider(
        store=JsonResearchPackageStore(tmp_path / "research_packages"),
        responses=[initial_with_lineage_defect, malformed_repair, valid],
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

    second_repair_messages = provider.messages_seen[2]
    assert second_repair_messages[-2]["role"] == "assistant"
    assert second_repair_messages[-2]["content"] == malformed_repair
    assert "repair response is not valid decision JSON" in second_repair_messages[-1]["content"]
