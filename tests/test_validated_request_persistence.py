from __future__ import annotations

from MTS_V4.campaign import CheckpointedCampaignRunner
from MTS_V4.checkpoint import JsonCampaignCheckpointStore
from MTS_V4.contracts import AnalysisRequest, ResearchDecision, ResearchPhase, SubjectMetadata
from MTS_V4.decision_journal import JsonResearchDecisionJournal
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.research_recording import CampaignResearchRecorder


def _request(request_id: str, *, question_id: str = "Q-0001") -> AnalysisRequest:
    return AnalysisRequest(
        request_id=request_id,
        subject_id="equity:AAPL",
        question="Check the relationship.",
        method_id="analysis.descriptive.statistics",
        evidence_ids=(),
        parameters={"columns": ["close"]},
        research_phase=ResearchPhase.EXPLORATION,
        rationale="Mechanical persistence test.",
        rp_id="RP-0001",
        question_id=question_id,
        parent_question_id=None,
        parent_rp_id=None,
    )


def _runner(tmp_path):
    packages = JsonResearchPackageStore(tmp_path / "research_packages")
    journal = JsonResearchDecisionJournal(tmp_path / "decision_journal.jsonl")
    recorder = CampaignResearchRecorder(
        package_store=packages,
        decision_journal=journal,
    )
    checkpoints = JsonCampaignCheckpointStore(tmp_path / "checkpoint.json")
    runner = CheckpointedCampaignRunner(
        orchestrator=object(),
        cache=object(),
        checkpoint_store=checkpoints,
        research_recorder=recorder,
    )
    return runner, packages, journal, checkpoints


def test_checkpoint_records_exact_rd_decision_without_persisting_unvalidated_request(tmp_path):
    runner, packages, journal, checkpoints = _runner(tmp_path)
    subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")
    request = _request("req:invalid-first")
    decision = ResearchDecision(
        continue_research=True,
        rp_id="RP-0001",
        next_request=request,
    )

    save_checkpoint = runner._checkpoint_callback(
        campaign_id="campaign:aapl",
        subject=subject,
        evidence=(),
    )
    save_checkpoint(decision, 1, 0)

    assert packages.list_ids() == ()
    records = journal.records("campaign:aapl")
    assert len(records) == 1
    assert records[0]["decision"]["next_request"]["request_id"] == "req:invalid-first"
    checkpoint = checkpoints.load()
    assert checkpoint is not None
    assert checkpoint.decision.next_request is not None
    assert checkpoint.decision.next_request.request_id == "req:invalid-first"


def test_only_objectively_accepted_request_enters_research_package(tmp_path):
    runner, packages, journal, _ = _runner(tmp_path)
    subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")
    invalid = _request("req:invalid-first")
    accepted = _request("req:accepted", question_id="Q-0002")

    save_checkpoint = runner._checkpoint_callback(
        campaign_id="campaign:aapl",
        subject=subject,
        evidence=(),
    )
    save_checkpoint(
        ResearchDecision(continue_research=True, rp_id="RP-0001", next_request=invalid),
        1,
        0,
    )
    save_checkpoint(
        ResearchDecision(continue_research=True, rp_id="RP-0001", next_request=accepted),
        2,
        0,
    )

    assert packages.list_ids() == ()
    assert len(journal.records("campaign:aapl")) == 2

    persist_accepted = runner._accepted_request_callback(
        campaign_id="campaign:aapl",
        subject=subject,
    )
    assert persist_accepted is not None
    persist_accepted(accepted)

    package = packages.load("RP-0001")
    assert package is not None
    assert [item.request_id for item in package.analyses] == ["req:accepted"]
    assert [item.question_id for item in package.questions] == ["Q-0002"]
    assert package.analyses[0].result_id is None


def test_replaying_same_accepted_pending_request_is_idempotent(tmp_path):
    runner, packages, _, _ = _runner(tmp_path)
    subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")
    request = _request("req:pending")
    persist_accepted = runner._accepted_request_callback(
        campaign_id="campaign:aapl",
        subject=subject,
    )
    assert persist_accepted is not None

    persist_accepted(request)
    persist_accepted(request)

    package = packages.load("RP-0001")
    assert package is not None
    assert len(package.questions) == 1
    assert len(package.analyses) == 1
    assert package.analyses[0].request_id == "req:pending"
    assert package.analyses[0].result_id is None
