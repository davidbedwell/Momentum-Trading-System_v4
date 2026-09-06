from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class ResearchPhase(str, Enum):
    EXPLORATION = "EXPLORATION"
    VALIDATION = "VALIDATION"


@dataclass(frozen=True, slots=True)
class SubjectMetadata:
    subject_id: str
    ticker: str
    asset_class: str = "EQUITY"
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EvidenceMetadata:
    """Durable evidence metadata with no reproducible payload/cache location."""

    evidence_id: str
    subject_id: str
    evidence_type: str
    artifact_type: str
    source_identity: str
    coverage_start: str | None
    coverage_end: str | None
    row_count: int | None
    schema: tuple[str, ...]
    provenance: Mapping[str, Any] = field(default_factory=dict)
    neutral_semantics: str = ""


@dataclass(frozen=True, slots=True)
class EvidenceDescriptor:
    """Campaign-local evidence reference, including the temporary cache key."""

    evidence_id: str
    subject_id: str
    evidence_type: str
    artifact_type: str
    source_identity: str
    coverage_start: str | None
    coverage_end: str | None
    row_count: int | None
    schema: tuple[str, ...]
    cache_key: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    neutral_semantics: str = ""

    def durable_metadata(self) -> EvidenceMetadata:
        return EvidenceMetadata(
            evidence_id=self.evidence_id,
            subject_id=self.subject_id,
            evidence_type=self.evidence_type,
            artifact_type=self.artifact_type,
            source_identity=self.source_identity,
            coverage_start=self.coverage_start,
            coverage_end=self.coverage_end,
            row_count=self.row_count,
            schema=self.schema,
            provenance=dict(self.provenance),
            neutral_semantics=self.neutral_semantics,
        )


@dataclass(frozen=True, slots=True)
class AnalysisResultInput:
    """Explicit RD-authored reference to a prior campaign-local Analysis output.

    Deterministic code may verify that the result and output path exist and then
    resolve exactly that value for execution. It may not select a prior result,
    output path, alias, transformation, or substitute another input.
    """

    result_id: str
    output_path: tuple[str | int, ...]
    input_name: str


@dataclass(frozen=True, slots=True)
class AnalysisRequest:
    request_id: str
    subject_id: str
    question: str
    method_id: str
    evidence_ids: tuple[str, ...]
    parameters: Mapping[str, Any]
    research_phase: ResearchPhase
    rationale: str = ""
    analysis_inputs: tuple[AnalysisResultInput, ...] = ()


@dataclass(frozen=True, slots=True)
class ContractDefect:
    code: str
    message: str
    field: str | None = None
    method_id: str | None = None


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    result_id: str
    request_id: str
    subject_id: str
    method_id: str
    outputs: Mapping[str, Any]
    evidence_ids: tuple[str, ...]
    limitations: tuple[str, ...] = ()
    execution_metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Finding:
    """Minimal durable envelope around open-ended AI-authored science.

    Deterministic code may enforce only the identity and lineage envelope below.
    The ``metadata`` namespace is intentionally open: RD may create arbitrary
    scientific labels, nested structures, classifications, caveats, confidence
    judgments, relationships, applicability descriptions, or new concepts that
    were not anticipated by deterministic code.
    """

    finding_id: str
    subject_id: str
    statement: str
    supporting_result_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FindingRetraction:
    """Durable audit record that quarantines a finding from active research memory.

    Retraction is an externally initiated governance action, not a deterministic
    scientific judgment. The original finding remains preserved for audit while
    normal Nexus retrieval excludes it from future Research Director context.
    """

    finding_id: str
    reason: str
    initiated_by: str
    retracted_at_utc: str
    replacement_finding_id: str | None = None


@dataclass(frozen=True, slots=True)
class ResearchDecision:
    """Scientific decision authored by the AI Research Director.

    Deterministic code may validate the representation but does not manufacture
    any of the scientific content represented here.
    """

    continue_research: bool
    next_request: AnalysisRequest | None = None
    promote_findings: tuple[Finding, ...] = ()
    research_state: Mapping[str, Any] = field(default_factory=dict)
    close_reason: str | None = None
