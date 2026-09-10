from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping, Sequence

from .contracts import (
    AnalysisRequest,
    AnalysisResult,
    ContractDefect,
    EvidenceDescriptor,
    ResearchDecision,
    SubjectMetadata,
)
from .interfaces import ResearchDirectorProvider


class AppellateResearchDirector:
    """Primary AI RD with a superior AI appeal provider after repeated repair failure.

    Normal research remains with the primary provider. Objective-contract repair
    attempts remain with the primary provider until ``primary_repair_attempts``
    have been used. A subsequent repair request is sent to the authorized appeal
    provider with the current governed context plus a mechanical record of the
    failed primary repair sequence. The wrapper records and routes; it does not
    interpret scientific merit or alter either provider's scientific decision.
    """

    def __init__(
        self,
        *,
        primary: ResearchDirectorProvider,
        appeal: ResearchDirectorProvider,
        primary_repair_attempts: int = 3,
    ) -> None:
        if primary_repair_attempts < 0:
            raise ValueError("primary_repair_attempts cannot be negative")
        self._primary = primary
        self._appeal = appeal
        self._primary_repair_attempts = primary_repair_attempts
        self._repair_attempts = 0
        self._failed_primary_repairs: list[Mapping[str, object]] = []

    def _reset_repair_sequence(self) -> None:
        self._repair_attempts = 0
        self._failed_primary_repairs = []

    def begin_research(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision:
        self._reset_repair_sequence()
        return self._primary.begin_research(
            mission=mission,
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )

    def resume_research(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        prior_decision: ResearchDecision,
        evidence_continuity: Mapping[str, object],
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision:
        self._reset_repair_sequence()
        return self._primary.resume_research(
            mission=mission,
            subject=subject,
            prior_decision=prior_decision,
            evidence_continuity=evidence_continuity,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )

    def repair_request(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        prior_decision: ResearchDecision,
        defects: Sequence[ContractDefect],
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision:
        if self._repair_attempts < self._primary_repair_attempts:
            self._repair_attempts += 1
            decision = self._primary.repair_request(
                mission=mission,
                subject=subject,
                prior_decision=prior_decision,
                defects=defects,
                evidence=evidence,
                available_methods=available_methods,
                nexus_context=nexus_context,
            )
            self._failed_primary_repairs.append(
                {
                    "attempt": self._repair_attempts,
                    "input_decision": asdict(prior_decision),
                    "objective_contract_defects": [asdict(item) for item in defects],
                    "returned_decision": asdict(decision),
                }
            )
            return decision

        appeal_context = dict(nexus_context)
        appeal_context["ai_appeal"] = {
            "authority": "AUTHORIZED_AI_SCIENTIFIC_APPEAL",
            "primary_repair_attempts_exhausted": self._primary_repair_attempts,
            "failed_primary_repair_sequence": tuple(self._failed_primary_repairs),
            "instruction": (
                "Adjudicate the current objective-contract impasse as the superior AI scientific "
                "authority for this appeal scope. You may affirm, revise, replace, or close the "
                "primary RD decision. Deterministic code will validate objective execution contracts "
                "but will not substitute scientific judgment."
            ),
        }
        return self._appeal.repair_request(
            mission=mission,
            subject=subject,
            prior_decision=prior_decision,
            defects=defects,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=appeal_context,
        )

    def interpret_result(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        request: AnalysisRequest,
        result: AnalysisResult,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision:
        self._reset_repair_sequence()
        return self._primary.interpret_result(
            mission=mission,
            subject=subject,
            request=request,
            result=result,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
