from __future__ import annotations

from dataclasses import replace

import pytest

from MTS_V4.research_package import (
    ResearchAnalysisRecord,
    ResearchPackage,
    ResearchPackageError,
    ResearchQuestionRecord,
)
from MTS_V4.research_package_store import JsonResearchPackageStore


def test_new_rp_never_overwrites_prior_rp(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")

    rp1 = ResearchPackage(
        rp_id="RP-0001",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Does condition A precede expansion?",
        originating_rationale="Test the first coherent line of inquiry.",
    )
    rp2 = ResearchPackage(
        rp_id="RP-0002",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Does condition B identify direction?",
        originating_rationale="Test a distinct coherent line of inquiry.",
    )

    store.create(rp1)
    store.create(rp2)

    assert store.list_ids() == ("RP-0001", "RP-0002")
    assert store.load("RP-0001") == rp1
    assert store.load("RP-0002") == rp2


def test_followup_questions_remain_bundled_under_original_rp(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    rp = ResearchPackage(
        rp_id="RP-0001",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Does high volume with low price movement matter?",
        originating_rationale="Investigate the originating scientific proposition.",
    )
    store.create(rp)

    q1 = ResearchQuestionRecord(
        question_id="Q-0001",
        question="Is the condition associated with off-exchange activity?",
        rationale="First test of the originating proposition.",
        research_phase="EXPLORATION",
    )
    q1a = ResearchQuestionRecord(
        question_id="Q-0001A",
        parent_question_id="Q-0001",
        question="Does the association persist across volume regimes?",
        rationale="Follow-up generated from Q-0001.",
        research_phase="EXPLORATION",
    )

    evolved = rp.append_question(q1).append_question(q1a)
    store.save(evolved)

    loaded = store.load("RP-0001")
    assert loaded is not None
    assert [item.question_id for item in loaded.questions] == ["Q-0001", "Q-0001A"]
    assert loaded.questions[1].parent_question_id == "Q-0001"


def test_analysis_is_tied_to_question_lineage(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    rp = ResearchPackage(
        rp_id="RP-0001",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Test AAPL condition.",
        originating_rationale="Originating rationale.",
    )
    q1 = ResearchQuestionRecord(
        question_id="Q-0001",
        question="What is the measured relationship?",
        rationale="Measure it.",
        research_phase="EXPLORATION",
    )
    rp = rp.append_question(q1)
    rp = rp.append_analysis(
        ResearchAnalysisRecord(
            request_id="req:1",
            question_id="Q-0001",
            method_id="analysis.relationship.correlation",
            parameters={"method": "pearson"},
            evidence_ids=("evidence:equity:AAPL:1",),
            analysis_inputs=(),
            result_id="analysis-result:1",
            execution_status="SUCCESS",
            interpretation="The AI-authored interpretation belongs to this question lineage.",
        )
    )
    store.create(rp)

    loaded = store.load("RP-0001")
    assert loaded is not None
    assert loaded.analyses[0].question_id == "Q-0001"
    assert loaded.analyses[0].result_id == "analysis-result:1"


def test_child_rp_requires_existing_same_subject_parent(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    parent = ResearchPackage(
        rp_id="RP-0001",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Parent line.",
        originating_rationale="Parent rationale.",
    )
    store.create(parent)

    child = ResearchPackage(
        rp_id="RP-0002",
        parent_rp_id="RP-0001",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Distinct child line.",
        originating_rationale="AI RD explicitly split this into a child RP.",
    )
    store.create(child)
    assert store.load("RP-0002").parent_rp_id == "RP-0001"

    wrong_subject = ResearchPackage(
        rp_id="RP-0003",
        parent_rp_id="RP-0001",
        subject_id="equity:MSFT",
        campaign_id="campaign:msft",
        originating_question="Wrong-subject child.",
        originating_rationale="Should fail mechanical lineage validation.",
    )
    with pytest.raises(ResearchPackageError, match="share subject_id"):
        store.create(wrong_subject)


def test_closed_rp_is_frozen_and_later_rp_does_not_change_it(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    rp1 = ResearchPackage(
        rp_id="RP-0001",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Original line.",
        originating_rationale="Original rationale.",
    )
    store.create(rp1)
    closed = rp1.close(
        close_reason="AI_RD_SCIENTIFIC_CLOSURE",
        final_assessment="AI-authored final assessment.",
    )
    store.save(closed)

    rp2 = ResearchPackage(
        rp_id="RP-0002",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Later line.",
        originating_rationale="Later rationale.",
    )
    store.create(rp2)

    frozen = store.load("RP-0001")
    assert frozen is not None
    assert frozen.status == "CLOSED"
    assert frozen.close_reason == "AI_RD_SCIENTIFIC_CLOSURE"
    assert frozen.final_assessment == "AI-authored final assessment."

    tampered = replace(frozen, final_assessment="rewritten", version=frozen.version + 1)
    with pytest.raises(ResearchPackageError, match="closed research package is immutable"):
        store.save(tampered)


def test_store_rejects_raw_or_cache_payload_fields(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    rp = ResearchPackage(
        rp_id="RP-0001",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Original line.",
        originating_rationale="Original rationale.",
        hypotheses=({"payload": [1, 2, 3]},),
    )
    with pytest.raises(ResearchPackageError, match="raw/cache evidence data"):
        store.create(rp)
