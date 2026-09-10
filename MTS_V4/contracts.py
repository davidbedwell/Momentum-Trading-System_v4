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


ACQUISITION_ONLY_PROVENANCE_KEYS = frozenset(
    {
        "acquired_at",
        "acquired_at_utc",
        "fetched_at",
        "fetched_at_utc",
        "pulled_at",
        "pulled_at_utc",
        "requested_at",
        "requested_at_utc",
        "retrieved_at",
        "retrieved_at_utc",
    }
)


def meaningful_evidence_provenance(provenance: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return source metadata that participates in durable evidence identity.

    Acquisition timestamps remain useful campaign-local provenance, but they do
    not change the identity of otherwise identical evidence and may not cause a
    later reacquisition to rewrite or collide with metadata already referenced
    by durable findings.
    """
    return {
        str(key): value
        for key, value in provenance.items()
        if str(key).lower() not in ACQUISITION_ONLY_PROVENANCE_KEYS
    }


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
    content_identity: str | None = None

    def identity_equivalent(self, other: "EvidenceMetadata") -> bool:
        """Compare immutable evidence meaning while ignoring acquisition clocks.

        Equivalent reacquisitions keep the first durable record unchanged. This
        preserves historical finding references while allowing operationally new
        fetch timestamps for identical evidence.
        """
        if not isinstance(other, EvidenceMetadata):
            return False
        return (
            self.evidence_id == other.evidence_id
            and self.subject_id == other.subject_id
            and self.evidence_type == other.evidence_type
            and self.artifact_type == other.artifact_type
            and self.source_identity == other.source_identity
            and self.coverage_start == other.coverage_start
            and self.coverage_end == other.coverage_end
            and self.row_count == other.row_count
            and tuple(self.schema) == tuple(other.schema)
            and dict(meaningful_evidence_provenance(self.provenance))
            == dict(meaningful_evidence_provenance(other.provenance))
            and self.neutral_semantics == other.neutral_semantics
            and self.content_identity == other.content_identity
        )


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
    content_identity: str | None = None

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
            content_identity=self.content_identity,
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
    rp_id: str | None = None
    question_id: str | None = None
    parent_question_id: str | None = None
    parent_rp_id: str | None = None


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

    def durable_metadata(self) -> "AnalysisResultMetadata":
        future_information = self.execution_metadata.get("future_information", {})
        if not isinstance(future_information, Mapping):
            future_information = {"value": future_information}
        return AnalysisResultMetadata(
            result_id=self.result_id,
            request_id=self.request_id,
            subject_id=self.subject_id,
            method_id=self.method_id,
            evidence_ids=self.evidence_ids,
            future_information=dict(future_information),
            execution_metadata={
                key: value
                for key, value in self.execution_metadata.items()
                if key not in {"payload", "rows", "derived_datasets"}
            },
        )


@dataclass(frozen=True, slots=True)
class AnalysisResultMetadata:
    """Durable result identity and lineage without reproducible result payloads."""

    result_id: str
    request_id: str
    subject_id: str
    method_id: str
    evidence_ids: tuple[str, ...]
    future_information: Mapping[str, Any] = field(default_factory=dict)
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
    any of the scientific content represented here. ``rp_id`` identifies the
    coherent research package to which this decision belongs. Interpretation
    fields preserve what RD concluded from the immediately interpreted Analysis
    result without requiring that conclusion to be promoted as a significant
    Nexus finding. ``interpreted_future_information`` is objective Analysis
    lineage copied into the durable RP record; it is not authored scientific
    judgment.
    """

    continue_research: bool
    next_request: AnalysisRequest | None = None
    promote_findings: tuple[Finding, ...] = ()
    research_state: Mapping[str, Any] = field(default_factory=dict)
    close_reason: str | None = None
    rp_id: str | None = None
    analysis_interpretation: str | None = None
    interpreted_request_id: str | None = None
    interpreted_result_id: str | None = None
    interpreted_execution_status: str | None = None
    interpreted_future_information: Mapping[str, Any] = field(default_factory=dict)
