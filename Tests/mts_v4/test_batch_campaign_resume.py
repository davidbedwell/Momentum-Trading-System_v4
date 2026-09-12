from types import SimpleNamespace

from MTS_V4.batch_campaign_resume import (
    RECOVERED_CACHE_KEY_PREFIX,
    recovered_evidence_descriptors,
    recovered_nexus_context,
)
from MTS_V4.contracts import (
    AnalysisResult,
    AnalysisResultMetadata,
    EvidenceMetadata,
    Finding,
    SubjectMetadata,
)
from MTS_V4.nexus import InMemoryResearchNexus


def _nexus() -> InMemoryResearchNexus:
    nexus = InMemoryResearchNexus()
    subject = SubjectMetadata(subject_id="equity:AMD", ticker="AMD")
    nexus.upsert_subject(subject)
    nexus.upsert_evidence_metadata(
        EvidenceMetadata(
            evidence_id="E1",
            subject_id=subject.subject_id,
            evidence_type="PRICE",
            artifact_type="TABULAR",
            source_identity="fixture",
            coverage_start="2026-01-01",
            coverage_end="2026-01-31",
            row_count=20,
            schema=("date", "close"),
            provenance={"provider": "fixture"},
            neutral_semantics="daily price history",
            content_identity="abc",
        )
    )
    nexus.register_analysis_result_metadata(
        AnalysisResultMetadata(
            result_id="R1",
            request_id="REQ1",
            subject_id=subject.subject_id,
            method_id="analysis.fixture",
            evidence_ids=("E1",),
            future_information={"contains_future_information": True},
            execution_metadata={"execution_status": "SUCCESS"},
        )
    )
    nexus.publish_finding(
        Finding(
            finding_id="F1",
            subject_id=subject.subject_id,
            statement="fixture finding",
            supporting_result_ids=("R1",),
            evidence_ids=("E1",),
        )
    )
    return nexus


def test_recovered_evidence_descriptors_are_metadata_only_and_identity_preserving():
    nexus = _nexus()
    descriptor = recovered_evidence_descriptors(
        nexus=nexus,
        subject_id="equity:AMD",
    )[0]

    assert descriptor.evidence_id == "E1"
    assert descriptor.schema == ("date", "close")
    assert descriptor.content_identity == "abc"
    assert descriptor.provenance == {"provider": "fixture"}
    assert descriptor.cache_key == RECOVERED_CACHE_KEY_PREFIX + "E1"


def test_recovered_nexus_context_preserves_campaign_result_catalog_without_payload_ranking():
    nexus = _nexus()
    result = AnalysisResult(
        result_id="R1",
        request_id="REQ1",
        subject_id="equity:AMD",
        method_id="analysis.fixture",
        outputs={
            "derived_dataset_catalog": {
                "aligned": {"output_path": ["derived_datasets", "aligned"]}
            },
            "derived_datasets": {"aligned": [{"x": 1}]},
        },
        evidence_ids=("E1",),
        execution_metadata={
            "execution_status": "SUCCESS",
            "future_information": {"contains_future_information": True},
        },
    )
    reconstructed = SimpleNamespace(
        subject=SubjectMetadata(subject_id="equity:AMD", ticker="AMD"),
        results_by_analysis_id={"AMD-A001": result},
    )

    context = recovered_nexus_context(
        reconstructed=reconstructed,
        nexus=nexus,
        research_concepts=({"concept_id": "C1"},),
    )

    catalog = context["campaign_analysis_result_catalog"]
    assert len(catalog) == 1
    assert catalog[0]["analysis_id"] == "AMD-A001"
    assert catalog[0]["result_id"] == "R1"
    assert catalog[0]["reusable_derived_datasets"] == {
        "aligned": {"output_path": ["derived_datasets", "aligned"]}
    }
    assert "derived_datasets" not in catalog[0]
    assert context["recovery_context"]["analysis_execution_enabled"] is False
    assert context["recovery_context"]["raw_acquired_evidence_payloads_restored"] is False
