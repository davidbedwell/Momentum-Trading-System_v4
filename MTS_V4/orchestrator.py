from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .cache import TemporaryResearchCache
from .contracts import EvidenceDescriptor, ResearchDecision, SubjectMetadata
from .interfaces import AnalysisExecutor, ResearchDirectorProvider
from .nexus import ResearchNexus
from .validation import ObjectiveContractValidator


class ResearchLoopError(RuntimeError):
    pass


StateCallback = Callable[[ResearchDecision, int, int], None]


@dataclass(frozen=True, slots=True)
class ResearchLoopOutcome:
    decisions: int
    analyses_executed: int
    findings_promoted: int
    closed: bool
    close_reason: str | None
    final_decision: ResearchDecision


class ResearchLoopOrchestrator:
    """Mechanical RD -> validate -> Analysis -> RD loop.

    The orchestrator contains no scientific selection logic. Every question,
    method, scientifically meaningful parameter, interpretation, finding, and
    continue/stop decision comes from the ResearchDirectorProvider.

    Optional checkpoint callbacks receive only AI-authored decision state and
    mechanical counters. Resume never reconstructs or guesses scientific state.

    Research concepts are descriptive idea seeds only. They are exposed to RD
    as context and never selected, ranked, promoted, or treated as evidence by
    the orchestrator.
    """

    def __init__(
        self,
        *,
        mission: str,
        rd: ResearchDirectorProvider,
        validator: ObjectiveContractValidator,
        analysis: AnalysisExecutor,
        nexus: ResearchNexus,
        cache: TemporaryResearchCache,
        available_methods: Sequence[Mapping[str, Any]],
        research_concepts: Sequence[Mapping[str, Any]] = (),
        max_contract_repairs: int = 3,
    ) -> None:
        if max_contract_repairs < 0:
            raise ValueError("max_contract_repairs cannot be negative")
        self._mission = mission
        self._rd = rd
        self._validator = validator
        self._analysis = analysis
        self._nexus = nexus
        self._cache = cache
        self._available_methods = tuple(dict(method) for method in available_methods)
        self._research_concepts = tuple(dict(concept) for concept in research_concepts)
        self._max_contract_repairs = max_contract_repairs

    def run(
        self,
        *,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        max_analyses: int,
        initial_decision: ResearchDecision | None = None,
        initial_decisions: int = 0,
        initial_analyses: int = 0,
        evidence_continuity: Mapping[str, object] | None = None,
        state_callback: StateCallback | None = None,
    ) -> ResearchLoopOutcome:
        if max_analyses <= 0:
            raise ValueError("max_analyses must be positive")
        if initial_decisions < 0 or initial_analyses < 0:
            raise ValueError("initial counters cannot be negative")

        self._nexus.upsert_subject(subject)
        evidence_map = {item.evidence_id: item for item in evidence}
        if len(evidence_map) != len(evidence):
            raise ResearchLoopError("duplicate evidence_id")
        for item in evidence:
            if item.subject_id != subject.subject_id:
                raise ResearchLoopError(
                    f"evidence {item.evidence_id} does not belong to {subject.subject_id}"
                )
            self._nexus.upsert_evidence_metadata(item.durable_metadata())

        decisions = initial_decisions
        analyses = initial_analyses
        promoted = 0

        if initial_decision is None:
            decision = self._rd.begin_research(
                mission=self._mission,
                subject=subject,
                evidence=evidence,
                available_methods=self._available_methods,
                nexus_context=self._nexus_context(subject.subject_id),
            )
            decisions += 1
            promoted += self._publish_promotions(decision)
            self._checkpoint(state_callback, decision, decisions, analyses)
        else:
            decision = initial_decision
            if evidence_continuity is not None:
                decision = self._rd.resume_research(
                    mission=self._mission,
                    subject=subject,
                    prior_decision=initial_decision,
                    evidence_continuity=evidence_continuity,
                    evidence=evidence,
                    available_methods=self._available_methods,
                    nexus_context=self._nexus_context(subject.subject_id),
                )
                decisions += 1
                promoted += self._publish_promotions(decision)
                self._checkpoint(state_callback, decision, decisions, analyses)

        while decision.continue_research:
            if analyses >= max_analyses:
                return ResearchLoopOutcome(
                    decisions=decisions,
                    analyses_executed=analyses,
                    findings_promoted=promoted,
                    closed=False,
                    close_reason="ANALYSIS_BUDGET_EXHAUSTED",
                    final_decision=decision,
                )
            if decision.next_request is None:
                raise ResearchLoopError(
                    "RD requested continuation without an AnalysisRequest"
                )

            repairs = 0
            while True:
                defects = self._validator.validate(decision.next_request, evidence_map)
                if not defects:
                    break
                if repairs >= self._max_contract_repairs:
                    raise ResearchLoopError(
                        "objective contract repair budget exhausted: "
                        + "; ".join(defect.message for defect in defects)
                    )
                decision = self._rd.repair_request(
                    mission=self._mission,
                    subject=subject,
                    prior_decision=decision,
                    defects=defects,
                    evidence=evidence,
                    available_methods=self._available_methods,
                    nexus_context=self._nexus_context(subject.subject_id),
                )
                decisions += 1
                promoted += self._publish_promotions(decision)
                repairs += 1
                self._checkpoint(state_callback, decision, decisions, analyses)
                if not decision.continue_research:
                    return ResearchLoopOutcome(
                        decisions=decisions,
                        analyses_executed=analyses,
                        findings_promoted=promoted,
                        closed=True,
                        close_reason=decision.close_reason,
                        final_decision=decision,
                    )
                if decision.next_request is None:
                    raise ResearchLoopError(
                        "RD repair requested continuation without an AnalysisRequest"
                    )

            request = decision.next_request
            payloads: dict[str, object] = {}
            for evidence_id in request.evidence_ids:
                descriptor = evidence_map[evidence_id]
                payloads[evidence_id] = self._cache.get(descriptor.cache_key)

            result = self._analysis.execute(request, payloads)
            analyses += 1
            if result.request_id != request.request_id:
                raise ResearchLoopError("Analysis result request lineage mismatch")
            if result.subject_id != subject.subject_id:
                raise ResearchLoopError("Analysis result subject lineage mismatch")
            if result.method_id != request.method_id:
                raise ResearchLoopError(
                    "Analysis substituted a method; v4 requires exact method execution"
                )

            # If the process dies after Analysis but before RD interpretation, the
            # last checkpoint still contains the AI-authored request. Resume may
            # safely re-execute that exact deterministic Analysis request.
            self._checkpoint(state_callback, decision, decisions, analyses)

            decision = self._rd.interpret_result(
                mission=self._mission,
                subject=subject,
                request=request,
                result=result,
                evidence=evidence,
                available_methods=self._available_methods,
                nexus_context=self._nexus_context(subject.subject_id),
            )
            decisions += 1
            promoted += self._publish_promotions(decision)
            self._checkpoint(state_callback, decision, decisions, analyses)

        return ResearchLoopOutcome(
            decisions=decisions,
            analyses_executed=analyses,
            findings_promoted=promoted,
            closed=True,
            close_reason=decision.close_reason,
            final_decision=decision,
        )

    def _publish_promotions(self, decision: ResearchDecision) -> int:
        for finding in decision.promote_findings:
            self._nexus.publish_finding(finding)
        return len(decision.promote_findings)

    @staticmethod
    def _checkpoint(
        callback: StateCallback | None,
        decision: ResearchDecision,
        decisions: int,
        analyses: int,
    ) -> None:
        if callback is not None:
            callback(decision, decisions, analyses)

    def _nexus_context(self, subject_id: str) -> Mapping[str, object]:
        return {
            "subject": self._nexus.get_subject(subject_id),
            "evidence_metadata": self._nexus.evidence_metadata_for_subject(subject_id),
            "significant_findings": self._nexus.findings_for_subject(subject_id),
            "research_concepts": self._research_concepts,
            "research_concept_policy": {
                "authority": "NON_AUTHORITATIVE_IDEA_SEEDS",
                "treat_as_evidence": False,
                "must_test_before_acceptance": True,
                "rd_may_reject_or_reformulate": True,
                "rd_may_generate_additional_concepts": True,
                "deterministic_selection_or_ranking": False,
            },
        }
