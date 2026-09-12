from __future__ import annotations

from typing import Mapping, Protocol, Sequence

from .batch_campaign_reconstruction import ReconstructedBatchCampaign
from .batch_campaign_resume import recovered_evidence_descriptors, recovered_nexus_context
from .batch_contracts import BatchResearchDecision
from .contracts import EvidenceDescriptor, SubjectMetadata
from .nexus import ResearchNexus


class RetrospectiveResumeResearchDirector(Protocol):
    def interpret_batch_results(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        prior_decision,
        report,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, object]],
        nexus_context: Mapping[str, object],
    ) -> BatchResearchDecision: ...


def interpret_reconstructed_retrospective_boundary(
    *,
    rd: RetrospectiveResumeResearchDirector,
    reconstructed: ReconstructedBatchCampaign,
    nexus: ResearchNexus,
    mission: str,
    available_methods: Sequence[Mapping[str, object]],
    research_concepts: Sequence[Mapping[str, object]],
) -> BatchResearchDecision:
    """Return the completed recovered batch to RD without executing Analysis.

    This function intentionally has no Analysis executor, cache, compiler, or
    orchestration dependency. Its only scientific action is one
    INTERPRET_BATCH_RESULTS boundary call over the already completed report.
    Additional Analysis may occur only after the returned RD decision is durably
    accepted by a later continuation path.
    """

    evidence = recovered_evidence_descriptors(
        nexus=nexus,
        subject_id=reconstructed.subject.subject_id,
    )
    context = recovered_nexus_context(
        reconstructed=reconstructed,
        nexus=nexus,
        research_concepts=research_concepts,
    )
    recovery_context = dict(context.get("recovery_context", {}))
    recovery_context.update(
        {
            "mode": "RETROSPECTIVE_COMPLETED_BATCH_INTERPRETATION_ONLY",
            "analysis_execution_enabled": False,
            "analysis_executions_before_interpretation": 0,
            "instruction": (
                "Interpret the already completed retrospective batch. No Analysis may execute before this "
                "interpretation. If further Analysis is scientifically warranted, author it in the returned "
                "decision for a later continuation step."
            ),
        }
    )
    context = dict(context)
    context["recovery_context"] = recovery_context

    return rd.interpret_batch_results(
        mission=mission,
        subject=reconstructed.subject,
        prior_decision=reconstructed.latest_decision,
        report=reconstructed.latest_report,
        evidence=evidence,
        available_methods=available_methods,
        nexus_context=context,
    )
