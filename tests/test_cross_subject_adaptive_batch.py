from __future__ import annotations

import json

import pytest

from MTS_V4.adaptive_batch import (
    SubjectEligibilityEnvelope,
    SubjectRunLedger,
    ThreeSubjectBatchController,
)
from MTS_V4.batch_synthesis import SolBatchScientificSynthesizer
from MTS_V4.cross_subject_memory import (
    InMemoryCrossSubjectScientificMemory,
    ResearchFrontierState,
    ScientificMemoryRecord,
)
from MTS_V4.subject_selection import SolAdaptiveSubjectSelector


class StubRD:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def _chat_completion(self, messages):
        self.calls.append(messages)
        return self.responses.pop(0)


def test_cross_subject_memory_excludes_active_subject_and_has_no_raw_rows():
    memory = InMemoryCrossSubjectScientificMemory()
    memory.publish(ScientificMemoryRecord(record_id="m-aapl", subject_id="AAPL", kind="TENTATIVE_HYPOTHESIS", summary="severe weakness rebound candidate"))
    memory.publish(ScientificMemoryRecord(record_id="m-msft", subject_id="MSFT", kind="NEGATIVE_RESULT", summary="candidate absent"))
    memory.set_frontier(ResearchFrontierState(version=1, summary="discriminate rebound generalization"))
    context = memory.context(exclude_subject_id="MSFT")
    assert [item["subject_id"] for item in context["records"]] == ["AAPL"]
    assert context["policy"]["raw_rows_present"] is False
    assert context["policy"]["mandatory_research_agenda"] is False


def test_subject_selector_leaves_scientific_choice_to_rd_but_enforces_eligibility():
    rd = StubRD([json.dumps({"subject_id": "XOM", "rationale": "Energy subject discriminates sector dependence."})])
    memory = InMemoryCrossSubjectScientificMemory()
    selector = SolAdaptiveSubjectSelector(
        rd=rd,
        scientific_memory=memory,
        eligibility=SubjectEligibilityEnvelope(approved_subject_ids=frozenset({"XOM", "MSFT"})),
    )
    decision = selector.choose_next(mission="predict T+1 onward", previously_seen=("AAPL",), candidate_subject_ids=("AAPL", "XOM", "MSFT"))
    assert decision.subject_id == "XOM"
    assert "AAPL" not in json.loads(rd.calls[0][1]["content"])["eligible_candidate_subject_ids"]


def test_batch_hard_stops_after_three_subjects():
    controller = ThreeSubjectBatchController(batch_id="B1")
    for symbol in ("AAPL", "XOM", "JPM"):
        assert controller.validate_selection(subject_id=symbol, rationale="scientific variation", previously_seen=()) == ()
        controller.accept_selection(subject_id=symbol, rationale="scientific variation")
        controller.record_run(SubjectRunLedger(subject_id=symbol, selection_rationale="scientific variation", decisions=1, analyses_executed=1, findings_promoted=0))
    assert controller.requires_review is True
    assert controller.ledger().requires_review is True
    assert controller.validate_selection(subject_id="MSFT", rationale="next", previously_seen=()) == ("three-subject autonomous batch limit reached; human review required",)
    with pytest.raises(RuntimeError):
        controller.accept_selection(subject_id="MSFT", rationale="next")


def test_batch_synthesis_requires_zero_finding_diagnosis():
    ledger_controller = ThreeSubjectBatchController(batch_id="B1")
    ledger_controller.accept_selection(subject_id="AAPL", rationale="baseline")
    ledger_controller.record_run(SubjectRunLedger(subject_id="AAPL", selection_rationale="baseline", decisions=2, analyses_executed=1, findings_promoted=0))
    ledger = ledger_controller.ledger()
    response = {
        "replicated_relationships": [],
        "contradicted_relationships": [],
        "untested_relationships": [],
        "conditional_or_regime_effects": [],
        "candidate_generalizations": [],
        "subject_anomalies": [],
        "zero_finding_diagnoses": {"AAPL": "Tentative hypothesis correctly not promoted pending blind validation."},
        "frontier_update": {},
        "cohort_discrimination_assessment": "insufficient after one subject",
        "next_subject_selection_direction": "choose a scientifically discriminating unseen subject",
    }
    synthesizer = SolBatchScientificSynthesizer(rd=StubRD([json.dumps(response)]), scientific_memory=InMemoryCrossSubjectScientificMemory())
    result = synthesizer.synthesize(mission="predict", ledger=ledger)
    assert "AAPL" in result.synthesis["zero_finding_diagnoses"]
