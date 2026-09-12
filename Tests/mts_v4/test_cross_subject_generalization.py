from __future__ import annotations

from MTS_V4.contracts import EvidenceDescriptor
from MTS_V4.cross_subject_generalization import (
    GENERALIZATION_SUBJECT_ID,
    SolCrossSubjectGeneralizationResearchDirector,
    generalization_evidence_view,
)


def _evidence(*, evidence_id: str, subject_id: str, cache_key: str) -> EvidenceDescriptor:
    return EvidenceDescriptor(
        evidence_id=evidence_id,
        subject_id=subject_id,
        evidence_type="DAILY_OHLCV",
        artifact_type="NORMALIZED_DATASET",
        source_identity="TEST",
        coverage_start="2026-01-01",
        coverage_end="2026-09-11",
        row_count=100,
        schema=("date", "close"),
        cache_key=cache_key,
        provenance={"provider": "TEST"},
        neutral_semantics="Test daily rows.",
    )


def test_generalization_projection_preserves_origin_and_cache_binding() -> None:
    amd = _evidence(evidence_id="evidence:amd", subject_id="equity:AMD", cache_key="cache:amd")
    ba = _evidence(evidence_id="evidence:ba", subject_id="equity:BA", cache_key="cache:ba")

    projected = generalization_evidence_view((amd, ba))

    assert [item.subject_id for item in projected] == [GENERALIZATION_SUBJECT_ID, GENERALIZATION_SUBJECT_ID]
    assert [item.cache_key for item in projected] == ["cache:amd", "cache:ba"]
    assert projected[0].provenance["origin_subject_id"] == "equity:AMD"
    assert projected[1].provenance["origin_subject_id"] == "equity:BA"
    assert amd.subject_id == "equity:AMD"
    assert ba.subject_id == "equity:BA"


def test_generalization_projection_rejects_cross_subject_evidence_id_collision() -> None:
    amd = _evidence(evidence_id="evidence:same", subject_id="equity:AMD", cache_key="cache:amd")
    ba = _evidence(evidence_id="evidence:same", subject_id="equity:BA", cache_key="cache:ba")

    try:
        generalization_evidence_view((amd, ba))
    except ValueError as exc:
        assert "evidence_id collision" in str(exc)
    else:
        raise AssertionError("cross-subject evidence_id collision should fail closed")


def test_generalization_prompt_preserves_sol_scientific_authority() -> None:
    messages = SolCrossSubjectGeneralizationResearchDirector._batch_messages(
        operation="BEGIN_BATCH_RESEARCH",
        mission="test",
        payload={"context": {}},
    )
    system = messages[0]["content"]

    assert "CROSS-SUBJECT GENERALIZATION" in system
    assert "Actively consider transferability" in system
    assert "If no cross-subject proposition is currently justified, close with zero analyses" in system
    assert "Deterministic code does not choose which subjects to compare" in system
