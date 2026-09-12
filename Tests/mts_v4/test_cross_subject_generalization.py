from __future__ import annotations

import json
from pathlib import Path

from MTS_V4.contracts import EvidenceDescriptor
from MTS_V4.cross_subject_generalization import (
    GENERALIZATION_SUBJECT_ID,
    SolCrossSubjectGeneralizationResearchDirector,
    generalization_evidence_view,
)
from MTS_V4.research_package_store import JsonResearchPackageStore
from scripts.run_sol_cross_subject_generalization import (
    _historical_subject_context,
    _prior_memory_documents,
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


def test_historical_context_unwraps_canonical_research_package_and_preserves_lineage(
    tmp_path: Path,
) -> None:
    package_path = tmp_path / "mts-v4-test" / "research_packages" / "rp-test.json"
    package_path.parent.mkdir(parents=True)
    package_path.write_text(
        json.dumps(
            {
                "format": JsonResearchPackageStore.FORMAT,
                "research_package": {
                    "rp_id": "rp-test",
                    "campaign_id": "campaign-test",
                    "subject_id": "equity:AMD",
                    "parent_rp_id": "rp-parent",
                    "status": "CLOSED",
                    "objective": "test objective",
                    "originating_question": "Does it transfer?",
                    "originating_rationale": "Prior evidence warranted testing.",
                    "hypotheses": ["ordinary hypothesis"],
                    "predictive_hypotheses": [{"hypothesis_id": "ph-1"}],
                    "findings": [{"finding_id": "finding-1"}],
                    "unresolved_issues": ["issue-1"],
                    "analyses": [{"analysis_id": "analysis-1", "result_id": "result-1"}],
                    "close_reason": "question exhausted",
                    "final_assessment": "closed assessment",
                },
            }
        ),
        encoding="utf-8",
    )

    context = _historical_subject_context(tmp_path, ("AMD",))
    packages = context["subjects"][0]["research_packages"]

    assert len(packages) == 1
    package = packages[0]
    assert package["source_path"] == str(package_path)
    assert package["source_format"] == JsonResearchPackageStore.FORMAT
    assert package["subject_id"] == "equity:AMD"
    assert package["campaign_id"] == "campaign-test"
    assert package["hypotheses"] == ["ordinary hypothesis"]
    assert package["predictive_hypotheses"] == [{"hypothesis_id": "ph-1"}]
    assert package["findings"] == [{"finding_id": "finding-1"}]
    assert package["unresolved_issues"] == ["issue-1"]
    assert package["analysis_lineage"] == [{"analysis_id": "analysis-1", "result_id": "result-1"}]
    assert package["close_reason"] == "question exhausted"
    assert package["final_assessment"] == "closed assessment"


def test_prior_memory_documents_deduplicate_exact_copies_but_preserve_distinct_records(
    tmp_path: Path,
) -> None:
    duplicate = {"version": 1, "finding": "same scientific memory"}
    distinct = {"version": 2, "finding": "newer distinct scientific memory"}
    paths = (
        tmp_path / "mts-v4-a" / "cross_subject_memory.json",
        tmp_path / "mts-v4-b" / "nested" / "cross_subject_memory.json",
        tmp_path / "mts-v4-c" / "cross_subject_memory.json",
    )
    for path, document in zip(paths, (duplicate, duplicate, distinct), strict=True):
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(document), encoding="utf-8")

    documents = _prior_memory_documents(tmp_path)

    assert len(documents) == 2
    assert [item["document"] for item in documents] == [duplicate, distinct]
    assert documents[0]["source_path"] == str(paths[0])
    assert documents[1]["source_path"] == str(paths[2])
