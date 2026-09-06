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
class EvidenceDescriptor:
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
    finding_id: str
    subject_id: str
    statement: str
    significance: str
    status: str
    supporting_result_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    applicability: Mapping[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    relationships: tuple[str, ...] = ()


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
