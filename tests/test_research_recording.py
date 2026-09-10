from __future__ import annotations

from MTS_V4.contracts import AnalysisRequest, ResearchDecision, ResearchPhase, SubjectMetadata
from MTS_V4.decision_journal import JsonResearchDecisionJournal
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.research_recording import CampaignResearchRecorder


def request(
    *,
    request_id: str,
    rp_id: str,
    question_id: str,
    question: str,
    parent_question_id: str | None = None,
    parent_rp_id: str | None = None,
) -> AnalysisRequest:
    return AnalysisRequest(
        request_id=request_id,
        subject_id="equity:AAPL",
        question=question,
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


def test_campaign_recorder_preserves_rps_question_lineage_interpretation_and_journal(tmp_path):
    packages = JsonResearchPackageStore(tmp_path / "research_packages")
    journal = JsonResearchDecisionJournal(tmp_path / "rd_decisions.jsonl")
    recorder = CampaignResearchRecorder(
        package_store=packages,
        decision_journal=journal,
    )
    subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")

    first_request = request(
        request_id="req:1",
        rp_id="RP-0001",
        question_id="Q-0001",
        question="Does condition A precede expansion?",
    )
    first = ResearchDecision(
        continue_research=True,
        next_request=first_request,
        rp_id="RP-0001",
    )
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=first,
        decision_sequence=1,
        analyses_executed=0,
    )

    # The orchestrator writes the same RD decision again after deterministic
    # Analysis execution and before asking RD to interpret it. This must not
    # duplicate either the journal record or the RP request lineage.
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=first,
        decision_sequence=1,
        analyses_executed=1,
    )

    followup_request = request(
        request_id="req:2",
        rp_id="RP-0001",
        question_id="Q-0001A",
        parent_question_id="Q-0001",
        question="Does the relationship persist across regimes?",
    )
    interpreted = ResearchDecision(
        continue_research=True,
        next_request=followup_request,
        rp_id="RP-0001",
        analysis_interpretation="The first result motivates a regime follow-up.",
        interpreted_request_id="req:1",
        interpreted_result_id="analysis-result:1",
        interpreted_execution_status="SUCCESS",
    )
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=interpreted,
        decision_sequence=2,
        analyses_executed=1,
    )

    rp1 = packages.load("RP-0001")
    assert rp1 is not None
    assert [item.question_id for item in rp1.questions] == ["Q-0001", "Q-0001A"]
    assert rp1.questions[1].parent_question_id == "Q-0001"
    assert [item.request_id for item in rp1.analyses] == ["req:1", "req:2"]
    assert rp1.analyses[0].result_id == "analysis-result:1"
    assert rp1.analyses[0].interpretation == "The first result motivates a regime follow-up."

    child_request = request(
        request_id="req:3",
        rp_id="RP-0002",
        question_id="Q-0002",
        parent_rp_id="RP-0001",
        question="Does a distinct condition identify direction?",
    )
    branch = ResearchDecision(
        continue_research=True,
        next_request=child_request,
        rp_id="RP-0001",
        analysis_interpretation="The follow-up suggests a distinct directionality proposition.",
        interpreted_request_id="req:2",
        interpreted_result_id="analysis-result:2",
        interpreted_execution_status="SUCCESS",
    )
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=branch,
        decision_sequence=3,
        analyses_executed=2,
    )

    rp1_after_branch = packages.load("RP-0001")
    rp2 = packages.load("RP-0002")
    assert rp1_after_branch is not None
    assert rp2 is not None
    assert rp2.parent_rp_id == "RP-0001"
    assert rp1_after_branch.originating_question == "Does condition A precede expansion?"
    assert rp2.originating_question == "Does a distinct condition identify direction?"
    assert packages.list_ids() == ("RP-0001", "RP-0002")

    closed = ResearchDecision(
        continue_research=False,
        rp_id="RP-0002",
        close_reason="AI_RD_SCIENTIFIC_CLOSURE",
        analysis_interpretation="The child RP is complete for the available evidence.",
        interpreted_request_id="req:3",
        interpreted_result_id="analysis-result:3",
        interpreted_execution_status="SUCCESS",
    )
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=closed,
        decision_sequence=4,
        analyses_executed=3,
    )

    frozen1 = packages.load("RP-0001")
    frozen2 = packages.load("RP-0002")
    assert frozen1 is not None and frozen2 is not None
    assert frozen1.status == "OPEN"
    assert frozen2.status == "CLOSED"
    assert frozen2.final_assessment == "The child RP is complete for the available evidence."
    assert frozen1.originating_question == "Does condition A precede expansion?"

    records = journal.records("campaign:aapl")
    assert [item["decision_sequence"] for item in records] == [1, 2, 3, 4]
    assert records[-1]["decision"]["close_reason"] == "AI_RD_SCIENTIFIC_CLOSURE"


def test_later_rp_does_not_overwrite_closed_prior_rp(tmp_path):
    packages = JsonResearchPackageStore(tmp_path / "research_packages")
    journal = JsonResearchDecisionJournal(tmp_path / "rd_decisions.jsonl")
    recorder = CampaignResearchRecorder(
        package_store=packages,
        decision_journal=journal,
    )
    subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")

    first_request = request(
        request_id="req:1",
        rp_id="RP-0001",
        question_id="Q-0001",
        question="First line",
    )
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=ResearchDecision(
            continue_research=True,
            next_request=first_request,
            rp_id="RP-0001",
        ),
        decision_sequence=1,
        analyses_executed=0,
    )
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=ResearchDecision(
            continue_research=False,
            rp_id="RP-0001",
            close_reason="done",
        ),
        decision_sequence=2,
        analyses_executed=0,
    )
    before = packages.load("RP-0001")

    second_request = request(
        request_id="req:2",
        rp_id="RP-0002",
        question_id="Q-0002",
        question="Second line",
    )
    recorder.record_decision(
        campaign_id="campaign:aapl",
        subject=subject,
        decision=ResearchDecision(
            continue_research=True,
            next_request=second_request,
            rp_id="RP-0002",
        ),
        decision_sequence=3,
        analyses_executed=0,
    )

    assert packages.load("RP-0001") == before
    assert packages.load("RP-0002") is not None
