from __future__ import annotations

import json

import pytest

from MTS_V4.adaptive_batch import SubjectEligibilityEnvelope
from MTS_V4.cross_subject_memory import InMemoryCrossSubjectScientificMemory
from MTS_V4.subject_selection import SolAdaptiveSubjectSelector


class StubRD:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.calls = []

    def _chat_completion(self, messages):
        self.calls.append(messages)
        return json.dumps(self.response)


def _selector(response: dict[str, object], *, validatable: frozenset[str] | None):
    rd = StubRD(response)
    selector = SolAdaptiveSubjectSelector(
        rd=rd,
        scientific_memory=InMemoryCrossSubjectScientificMemory(),
        eligibility=SubjectEligibilityEnvelope(
            approved_subject_ids=frozenset({"equity:NVDA", "equity:JPM"})
        ),
        validatable_hypothesis_ids=validatable,
    )
    return selector, rd


def test_empty_executable_validation_set_exposes_only_exploration_and_rejects_validation_first():
    selector, rd = _selector(
        {
            "subject_id": "equity:NVDA",
            "rationale": "Useful discriminator.",
            "mode": "VALIDATION_FIRST",
            "hypothesis_id": "H-1",
        },
        validatable=frozenset(),
    )
    with pytest.raises(ValueError, match="not mechanically executable"):
        selector.choose_next(
            mission="predict T+1 onward",
            previously_seen=("equity:AAPL",),
            candidate_subject_ids=("equity:NVDA", "equity:JPM"),
        )
    payload = json.loads(rd.calls[0][1]["content"])
    assert payload["human_governance"]["allowed_selection_modes"] == ["EXPLORATION"]
    assert payload["human_governance"]["mechanically_executable_validation_hypothesis_ids"] == []


def test_exact_executable_hypothesis_can_be_selected_validation_first():
    selector, rd = _selector(
        {
            "subject_id": "equity:JPM",
            "rationale": "Blind test is scientifically discriminating.",
            "mode": "VALIDATION_FIRST",
            "hypothesis_id": "H-CROSS-1",
        },
        validatable=frozenset({"H-CROSS-1"}),
    )
    decision = selector.choose_next(
        mission="predict T+1 onward",
        previously_seen=("equity:AAPL",),
        candidate_subject_ids=("equity:NVDA", "equity:JPM"),
    )
    assert decision.mode == "VALIDATION_FIRST"
    assert decision.hypothesis_id == "H-CROSS-1"
    payload = json.loads(rd.calls[0][1]["content"])
    assert payload["human_governance"]["allowed_selection_modes"] == [
        "EXPLORATION",
        "VALIDATION_FIRST",
    ]
    assert payload["human_governance"]["mechanically_executable_validation_hypothesis_ids"] == [
        "H-CROSS-1"
    ]


def test_validation_first_rejects_hypothesis_outside_executable_set():
    selector, _ = _selector(
        {
            "subject_id": "equity:JPM",
            "rationale": "Attempt invalid protocol binding.",
            "mode": "VALIDATION_FIRST",
            "hypothesis_id": "H-NOT-EXECUTABLE",
        },
        validatable=frozenset({"H-CROSS-1"}),
    )
    with pytest.raises(ValueError, match="not mechanically executable"):
        selector.choose_next(
            mission="predict T+1 onward",
            previously_seen=("equity:AAPL",),
            candidate_subject_ids=("equity:NVDA", "equity:JPM"),
        )


def test_legacy_none_preserves_unrestricted_selector_contract():
    selector, rd = _selector(
        {
            "subject_id": "equity:NVDA",
            "rationale": "Legacy caller still owns executable validation callback.",
            "mode": "VALIDATION_FIRST",
            "hypothesis_id": "H-LEGACY",
        },
        validatable=None,
    )
    decision = selector.choose_next(
        mission="predict T+1 onward",
        previously_seen=("equity:AAPL",),
        candidate_subject_ids=("equity:NVDA", "equity:JPM"),
    )
    assert decision.hypothesis_id == "H-LEGACY"
    payload = json.loads(rd.calls[0][1]["content"])
    assert payload["human_governance"]["allowed_selection_modes"] == [
        "EXPLORATION",
        "VALIDATION_FIRST",
    ]
