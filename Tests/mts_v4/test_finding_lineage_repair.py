from __future__ import annotations

import pytest

from MTS_V4.contracts import (
    AnalysisResultMetadata,
    EvidenceMetadata,
    Finding,
    SubjectMetadata,
)
from MTS_V4.nexus import InMemoryResearchNexus, NexusError
from MTS_V4.nexus_json import JsonResearchNexus


SUBJECT = SubjectMetadata(subject_id="equity:TSLA", ticker="TSLA")
EVIDENCE_ID = "evidence:equity:TSLA:source-1"
RESULT_ID = "analysis-result:tsla-1"


def _evidence() -> EvidenceMetadata:
    return EvidenceMetadata(
        evidence_id=EVIDENCE_ID,
        subject_id=SUBJECT.subject_id,
        evidence_type="MARKET_DATA",
        artifact_type="TABULAR",
        source_identity="TEST_SOURCE",
        coverage_start="2026-01-01",
        coverage_end="2026-09-11",
        row_count=10,
        schema=("date", "close"),
    )


def _result() -> AnalysisResultMetadata:
    return AnalysisResultMetadata(
        result_id=RESULT_ID,
        request_id="request:tsla-1",
        subject_id=SUBJECT.subject_id,
        method_id="analysis.test",
        evidence_ids=(EVIDENCE_ID,),
    )


def _finding(*, supporting_result_ids: tuple[str, ...] = (RESULT_ID,)) -> Finding:
    return Finding(
        finding_id="finding:tsla-1",
        subject_id=SUBJECT.subject_id,
        statement="AI-authored scientific statement remains unchanged.",
        supporting_result_ids=supporting_result_ids,
        evidence_ids=(),
        metadata={"confidence": "tentative"},
    )


def _seed(nexus) -> None:
    nexus.upsert_subject(SUBJECT)
    nexus.upsert_evidence_metadata(_evidence())
    nexus.register_analysis_result_metadata(_result())


@pytest.mark.parametrize("kind", ["memory", "json"])
def test_publish_finding_repairs_only_inherited_evidence_lineage(kind: str, tmp_path) -> None:
    nexus = (
        InMemoryResearchNexus()
        if kind == "memory"
        else JsonResearchNexus(tmp_path / "research_nexus.json")
    )
    _seed(nexus)

    original = _finding()
    nexus.publish_finding(original)

    persisted = nexus.get_finding(original.finding_id)
    assert persisted is not None
    assert persisted.statement == original.statement
    assert persisted.supporting_result_ids == original.supporting_result_ids
    assert persisted.metadata == original.metadata
    assert persisted.evidence_ids == (EVIDENCE_ID,)


@pytest.mark.parametrize("kind", ["memory", "json"])
def test_lineage_repair_does_not_hide_unknown_supporting_result(kind: str, tmp_path) -> None:
    nexus = (
        InMemoryResearchNexus()
        if kind == "memory"
        else JsonResearchNexus(tmp_path / "research_nexus.json")
    )
    _seed(nexus)

    with pytest.raises(NexusError, match="unknown result_id"):
        nexus.publish_finding(_finding(supporting_result_ids=("analysis-result:missing",)))
