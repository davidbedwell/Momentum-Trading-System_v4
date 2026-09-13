from __future__ import annotations

import pytest

from MTS_V4.batch_campaign_continuation import (
    ContinuationBaseline,
    RecoveredBatchCampaignContinuation,
)
from MTS_V4.batch_contracts import (
    BatchAnalysisRecord,
    BatchResearchDecision,
    ResearchPackagePlan,
    ScientificAnalysisSpecification,
    ScientificInputReference,
)
from MTS_V4.batch_orchestrator import BatchResearchLoopError
from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.contracts import AnalysisResult, EvidenceDescriptor, ResearchPhase, SubjectMetadata
from MTS_V4.method_catalog import MethodCatalog, MethodSpec
from MTS_V4.nexus import InMemoryResearchNexus
from MTS_V4.validation import ObjectiveContractValidator


class _Analysis:
    def __init__(self):
        self.requests = []

    def execute(self, request, payloads):
        self.requests.append(request)
        return AnalysisResult(
            result_id=f"result:new:{len(self.requests)}",
            request_id=request.request_id,
            subject_id=request.subject_id,
            method_id=request.method_id,
            outputs={"value": 1.0},
            evidence_ids=request.evidence_ids,
            execution_metadata={"execution_status": "SUCCESS"},
        )


class _RD:
    def __init__(self):
        self.begin_calls = 0
        self.interpret_calls = 0

    def begin_batch_research(self, **kwargs):
        self.begin_calls += 1
        raise AssertionError("continuation must not begin a new campaign")

    def interpret_batch_results(self, *, report, **kwargs):
        self.interpret_calls += 1
        assert len(report.records) == 1
        return BatchResearchDecision(
            continue_research=False,
            close_reason="RECOVERED_CONTINUATION_COMPLETE",
            batch_interpretation="Reviewed the new continuation batch only.",
        )


def _fixture():
    subject = SubjectMetadata(subject_id="equity:TSLA", ticker="TSLA")
    evidence = EvidenceDescriptor(
        evidence_id="evidence:tsla:test",
        subject_id=subject.subject_id,
        evidence_type="OHLCV",
        artifact_type="NORMALIZED_DATASET",
        source_identity="fixture",
        coverage_start="2026-01-01",
        coverage_end="2026-09-11",
        row_count=2,
        schema=("x",),
        cache_key="cache:tsla:test",
    )
    cache = TemporaryResearchCache()
    cache.put(evidence.cache_key, [{"x": 1.0}, {"x": 2.0}])
    catalog = MethodCatalog([MethodSpec("analysis.test", ("NORMALIZED_DATASET",))])
    analysis = _Analysis()
    rd = _RD()
    loop = RecoveredBatchCampaignContinuation(
        mission="fixture mission",
        rd=rd,
        validator=ObjectiveContractValidator(catalog),
        analysis=analysis,
        nexus=InMemoryResearchNexus(),
        cache=cache,
        available_methods=catalog.capability_payloads(),
    )
    prior = AnalysisResult(
        result_id="result:old",
        request_id="request:old",
        subject_id=subject.subject_id,
        method_id="analysis.test",
        outputs={"value": 0.0},
        evidence_ids=(evidence.evidence_id,),
        execution_metadata={"execution_status": "SUCCESS"},
    )
    return subject, evidence, analysis, rd, loop, prior


def _decision(subject, evidence, *, analysis_id="analysis:new"):
    spec = ScientificAnalysisSpecification(
        analysis_id=analysis_id,
        rp_id="RP-TSLA-CONTINUE",
        question_id="Q-TSLA-CONTINUE",
        subject_id=subject.subject_id,
        question="Execute only the newly authored continuation analysis.",
        method_id="analysis.test",
        inputs=(ScientificInputReference(role="raw", evidence_id=evidence.evidence_id),),
        parameters={},
        research_phase=ResearchPhase.EXPLORATION,
        rationale="fixture",
    )
    return BatchResearchDecision(
        continue_research=True,
        research_packages=(
            ResearchPackagePlan(
                rp_id="RP-TSLA-CONTINUE",
                objective="Continue from the accepted recovered decision.",
                analyses=(spec,),
            ),
        ),
    )


def test_continuation_executes_only_new_analysis_and_never_calls_begin():
    subject, evidence, analysis, rd, loop, prior = _fixture()
    outcome = loop.continue_from_decision(
        subject=subject,
        evidence=(evidence,),
        initial_decision=_decision(subject, evidence),
        prior_results_by_analysis_id={"analysis:old": prior},
        baseline=ContinuationBaseline(
            decisions=3,
            batches_executed=2,
            analyses_executed=24,
        ),
    )

    assert rd.begin_calls == 0
    assert rd.interpret_calls == 1
    assert len(analysis.requests) == 1
    assert analysis.requests[0].question == "Execute only the newly authored continuation analysis."
    assert outcome.analyses_executed == 25
    assert outcome.batches_executed == 3
    assert outcome.decisions == 4
    assert outcome.closed is True




def test_continuation_reuses_checkpoint_after_interruption_without_reexecution():
    subject, evidence, analysis, rd, loop, prior = _fixture()
    checkpoints = {}

    def checkpoint_then_interrupt(record, decisions, analyses):
        checkpoints[record.analysis_id] = record
        raise RuntimeError("simulated interruption after durable analysis checkpoint")

    with pytest.raises(RuntimeError, match="simulated interruption"):
        loop.continue_from_decision(
            subject=subject,
            evidence=(evidence,),
            initial_decision=_decision(subject, evidence),
            prior_results_by_analysis_id={"analysis:old": prior},
            baseline=ContinuationBaseline(
                decisions=3,
                batches_executed=2,
                analyses_executed=24,
            ),
            analysis_checkpoint_callback=checkpoint_then_interrupt,
        )

    assert len(analysis.requests) == 1
    assert set(checkpoints) == {"analysis:new"}
    assert checkpoints["analysis:new"].result is not None

    (
        subject2,
        evidence2,
        analysis2,
        rd2,
        loop2,
        prior2,
    ) = _fixture()

    outcome = loop2.continue_from_decision(
        subject=subject2,
        evidence=(evidence2,),
        initial_decision=_decision(subject2, evidence2),
        prior_results_by_analysis_id={"analysis:old": prior2},
        baseline=ContinuationBaseline(
            decisions=3,
            batches_executed=2,
            analyses_executed=24,
        ),
        checkpointed_records_by_analysis_id=checkpoints,
    )

    assert analysis2.requests == []
    assert rd2.begin_calls == 0
    assert rd2.interpret_calls == 1
    assert outcome.analyses_executed == 25
    assert outcome.batches_executed == 3
    assert outcome.decisions == 4
    assert outcome.closed is True


def test_continuation_rejects_checkpoint_not_in_accepted_decision():
    subject, evidence, analysis, rd, loop, prior = _fixture()

    foreign_record = BatchAnalysisRecord(
        analysis_id="analysis:not-authorized",
        rp_id="RP-TSLA-CONTINUE",
        status="OBJECTIVE_CONTRACT_DEFECT",
        objective_defect="fixture",
    )

    with pytest.raises(
        BatchResearchLoopError,
        match="not members of the accepted continuation decision",
    ):
        loop.continue_from_decision(
            subject=subject,
            evidence=(evidence,),
            initial_decision=_decision(subject, evidence),
            prior_results_by_analysis_id={"analysis:old": prior},
            baseline=ContinuationBaseline(
                decisions=3,
                batches_executed=2,
                analyses_executed=24,
            ),
            checkpointed_records_by_analysis_id={
                foreign_record.analysis_id: foreign_record
            },
        )

    assert analysis.requests == []
    assert rd.begin_calls == 0
    assert rd.interpret_calls == 0


def test_continuation_rejects_reexecution_of_recovered_analysis_identity():
    subject, evidence, analysis, rd, loop, prior = _fixture()
    with pytest.raises(BatchResearchLoopError, match="re-execute prior analysis_id"):
        loop.continue_from_decision(
            subject=subject,
            evidence=(evidence,),
            initial_decision=_decision(subject, evidence, analysis_id="analysis:old"),
            prior_results_by_analysis_id={"analysis:old": prior},
            baseline=ContinuationBaseline(
                decisions=3,
                batches_executed=2,
                analyses_executed=24,
            ),
        )

    assert analysis.requests == []
    assert rd.begin_calls == 0
    assert rd.interpret_calls == 0

def test_checkpoint_loader_selects_current_decision_and_rejects_wrong_fingerprint(tmp_path):
    import json
    from dataclasses import asdict

    from scripts.resume_fresh_subject import _load_analysis_checkpoints

    subject, evidence, analysis, rd, loop, prior = _fixture()
    captured = {}

    def capture_then_interrupt(record, decisions, analyses):
        captured[record.analysis_id] = record
        raise RuntimeError("capture")

    with pytest.raises(RuntimeError, match="capture"):
        loop.continue_from_decision(
            subject=subject,
            evidence=(evidence,),
            initial_decision=_decision(subject, evidence),
            prior_results_by_analysis_id={"analysis:old": prior},
            baseline=ContinuationBaseline(
                decisions=3,
                batches_executed=2,
                analyses_executed=24,
            ),
            analysis_checkpoint_callback=capture_then_interrupt,
        )

    record = captured["analysis:new"]
    path = tmp_path / "continuation_analysis_checkpoints.jsonl"

    rows = [
        {
            "decision_sequence": 2,
            "decision_fingerprint": "older-fingerprint",
            "record": asdict(record),
        },
        {
            "decision_sequence": 3,
            "decision_fingerprint": "current-fingerprint",
            "record": asdict(record),
        },
    ]
    path.write_text(
        "".join(json.dumps(row, default=str) + "\n" for row in rows),
        encoding="utf-8",
    )

    loaded = _load_analysis_checkpoints(
        path,
        decision_fingerprint="current-fingerprint",
        decision_sequence=3,
        accepted_analysis_ids={"analysis:new"},
    )

    assert set(loaded) == {"analysis:new"}

    bad_rows = [
        {
            "decision_sequence": 3,
            "decision_fingerprint": "wrong-fingerprint",
            "record": asdict(record),
        }
    ]
    path.write_text(
        "".join(json.dumps(row, default=str) + "\n" for row in bad_rows),
        encoding="utf-8",
    )

    with pytest.raises(
        RuntimeError,
        match="decision fingerprint mismatch",
    ):
        _load_analysis_checkpoints(
            path,
            decision_fingerprint="current-fingerprint",
            decision_sequence=3,
            accepted_analysis_ids={"analysis:new"},
        )
