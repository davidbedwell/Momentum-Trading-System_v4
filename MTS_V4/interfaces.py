from __future__ import annotations

from typing import Mapping, Protocol, Sequence

from .contracts import (
    AnalysisRequest,
    AnalysisResult,
    ContractDefect,
    EvidenceDescriptor,
    ResearchDecision,
    SubjectMetadata,
)


class ResearchDirectorProvider(Protocol):
    """Scientific-authority interface implemented by Qwen, Sol, or another AI."""

    def begin_research(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision: ...

    def repair_request(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        prior_decision: ResearchDecision,
        defects: Sequence[ContractDefect],
        evidence: Sequence[EvidenceDescriptor],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision: ...

    def interpret_result(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        request: AnalysisRequest,
        result: AnalysisResult,
        evidence: Sequence[EvidenceDescriptor],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision: ...


class AnalysisExecutor(Protocol):
    """Executes the exact validated method requested by RD."""

    def execute(
        self,
        request: AnalysisRequest,
        evidence_payloads: Mapping[str, object],
    ) -> AnalysisResult: ...
