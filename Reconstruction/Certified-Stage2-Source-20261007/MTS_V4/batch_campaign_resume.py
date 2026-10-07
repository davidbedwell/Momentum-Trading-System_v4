from __future__ import annotations

from typing import Mapping, Sequence

from .batch_campaign_reconstruction import ReconstructedBatchCampaign
from .contracts import EvidenceDescriptor
from .nexus import ResearchNexus


RECOVERED_CACHE_KEY_PREFIX = "recovered-metadata-only:"


def recovered_evidence_descriptors(
    *,
    nexus: ResearchNexus,
    subject_id: str,
) -> tuple[EvidenceDescriptor, ...]:
    """Recreate RD-visible evidence descriptors from durable Nexus metadata.

    These descriptors are for interpretation only. Their synthetic cache keys
    deliberately do not imply that raw evidence payloads survived process loss.
    A later execution path must reacquire or otherwise restore payloads before
    an AnalysisRequest may consume acquired evidence directly.
    """

    descriptors: list[EvidenceDescriptor] = []
    for item in nexus.evidence_metadata_for_subject(subject_id):
        descriptors.append(
            EvidenceDescriptor(
                evidence_id=item.evidence_id,
                subject_id=item.subject_id,
                evidence_type=item.evidence_type,
                artifact_type=item.artifact_type,
                source_identity=item.source_identity,
                coverage_start=item.coverage_start,
                coverage_end=item.coverage_end,
                row_count=item.row_count,
                schema=tuple(item.schema),
                cache_key=RECOVERED_CACHE_KEY_PREFIX + item.evidence_id,
                provenance=dict(item.provenance),
                neutral_semantics=item.neutral_semantics,
                content_identity=item.content_identity,
            )
        )
    return tuple(descriptors)


def recovered_nexus_context(
    *,
    reconstructed: ReconstructedBatchCampaign,
    nexus: ResearchNexus,
    research_concepts: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    """Rebuild the same campaign-local RD context available before process loss."""

    catalog = []
    for analysis_id, result in reconstructed.results_by_analysis_id.items():
        reusable = result.outputs.get("derived_dataset_catalog", {})
        catalog.append(
            {
                "analysis_id": analysis_id,
                "result_id": result.result_id,
                "request_id": result.request_id,
                "method_id": result.method_id,
                "execution_status": result.execution_metadata.get("execution_status"),
                "reusable_derived_datasets": reusable if isinstance(reusable, Mapping) else {},
                "future_information": result.execution_metadata.get("future_information", {}),
            }
        )

    subject_id = reconstructed.subject.subject_id
    return {
        "subject": nexus.get_subject(subject_id),
        "evidence_metadata": nexus.evidence_metadata_for_subject(subject_id),
        "significant_findings": nexus.findings_for_subject(subject_id),
        "historical_analysis_result_metadata": nexus.analysis_result_metadata_for_subject(subject_id),
        "research_concepts": tuple(dict(item) for item in research_concepts),
        "research_concept_policy": {
            "authority": "NON_AUTHORITATIVE_IDEA_SEEDS",
            "treat_as_evidence": False,
            "rd_may_reject_or_reformulate": True,
            "rd_may_generate_additional_concepts": True,
            "deterministic_selection_or_ranking": False,
        },
        "campaign_analysis_result_catalog": tuple(catalog),
        "campaign_analysis_result_catalog_policy": {
            "persistence": "CAMPAIGN_LOCAL_NOT_NEXUS",
            "contains_row_payloads": False,
            "purpose": (
                "Audit visibility. New batch Analysis Specifications should reference logical analysis_id, "
                "not generated result_id/output_path plumbing."
            ),
        },
        "recovery_context": {
            "mode": "RECONSTRUCTED_COMPLETED_BATCH_INTERPRETATION",
            "analysis_execution_enabled": False,
            "raw_acquired_evidence_payloads_restored": False,
            "instruction": (
                "Interpret the already completed batch using the durable scientific and result history. "
                "Do not assume that raw acquired-evidence cache payloads survived process loss."
            ),
        },
    }
