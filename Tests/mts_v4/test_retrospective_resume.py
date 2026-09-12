from __future__ import annotations

from types import SimpleNamespace

from MTS_V4.batch_contracts import BatchExecutionReport, BatchResearchDecision
from MTS_V4.contracts import EvidenceMetadata, SubjectMetadata
from MTS_V4.nexus import InMemoryResearchNexus
from MTS_V4.retrospective_resume import interpret_reconstructed_retrospective_boundary


class RecordingRD:
    def __init__(self) -> None:
        self.calls = []

    def interpret_batch_results(self, **kwargs):
        self.calls.append(kwargs)
        return BatchResearchDecision(
            continue_research=False,
            close_reason="fixture resolved",
        )


def test_retrospective_resume_returns_completed_batch_to_rd_with_zero_analysis_path():
    subject = SubjectMetadata(subject_id="equity:TSLA", ticker="TSLA")
    nexus = InMemoryResearchNexus()
    nexus.upsert_subject(subject)
    nexus.upsert_evidence_metadata(
        EvidenceMetadata(
            evidence_id="E-TSLA",
            subject_id=subject.subject_id,
            evidence_type="PRICE",
            artifact_type="TABULAR",
            source_identity="fixture",
            coverage_start="2026-01-01",
            coverage_end="2026-09-11",
            row_count=100,
            schema=("date", "close"),
        )
    )
    prior = BatchResearchDecision(continue_research=True)
    report = BatchExecutionReport(records=())
    reconstructed = SimpleNamespace(
        subject=subject,
        latest_decision=prior,
        latest_report=report,
        results_by_analysis_id={},
    )
    rd = RecordingRD()

    decision = interpret_reconstructed_retrospective_boundary(
        rd=rd,
        reconstructed=reconstructed,
        nexus=nexus,
        mission="retrospective fixture",
        available_methods=(),
        research_concepts=(),
    )

    assert decision.continue_research is False
    assert len(rd.calls) == 1
    call = rd.calls[0]
    assert call["prior_decision"] is prior
    assert call["report"] is report
    assert call["nexus_context"]["recovery_context"]["analysis_execution_enabled"] is False
    assert call["nexus_context"]["recovery_context"]["analysis_executions_before_interpretation"] == 0
    assert "analysis" not in call
    assert "executor" not in call
