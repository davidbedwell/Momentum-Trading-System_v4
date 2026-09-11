from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .contracts import AnalysisRequest, AnalysisResult, Finding, ResearchPhase


@dataclass(frozen=True, slots=True)
class ScientificInputReference:
    """AI-authored scientific input reference without runtime plumbing identities.

    Exactly one source must be supplied: an acquired evidence_id or a prior logical
    analysis_id from the same batch/campaign. ``role`` is a semantic name used by
    the AI inside method parameters; the deterministic compiler replaces that role
    with a safe executor binding. ``dataset_name`` is required only when a prior
    result exposes more than one reusable derived dataset.
    """

    role: str
    evidence_id: str | None = None
    analysis_id: str | None = None
    dataset_name: str | None = None


@dataclass(frozen=True, slots=True)
class ScientificAnalysisSpecification:
    """AI-authored scientific Analysis intent compiled into AnalysisRequest.

    ``parameters`` retain scientific method choices. Any method parameter field
    named ``input_name`` may use one of this specification's semantic input roles;
    the deterministic compiler rewrites it to the exact internal executor alias.
    """

    analysis_id: str
    rp_id: str
    question_id: str
    subject_id: str
    question: str
    method_id: str
    inputs: tuple[ScientificInputReference, ...]
    parameters: Mapping[str, Any]
    research_phase: ResearchPhase
    rationale: str = ""
    parent_question_id: str | None = None
    parent_rp_id: str | None = None


@dataclass(frozen=True, slots=True)
class ResearchPackagePlan:
    """One AI-authored coherent scientific line inside a batch decision."""

    rp_id: str
    objective: str
    analyses: tuple[ScientificAnalysisSpecification, ...]
    parent_rp_id: str | None = None
    decision_boundary: str | None = None


@dataclass(frozen=True, slots=True)
class BatchResearchDecision:
    """AI-authored program-level decision containing zero or more Research Packages."""

    continue_research: bool
    research_packages: tuple[ResearchPackagePlan, ...] = ()
    promote_findings: tuple[Finding, ...] = ()
    research_state: Mapping[str, Any] = field(default_factory=dict)
    close_reason: str | None = None
    batch_interpretation: str | None = None


@dataclass(frozen=True, slots=True)
class CompiledAnalysis:
    """Audit record connecting AI scientific intent to exact executor request."""

    analysis_id: str
    rp_id: str
    request: AnalysisRequest
    binding_map: Mapping[str, str] = field(default_factory=dict)
    mechanical_repairs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class BatchAnalysisRecord:
    """One completed or failed branch in a batch execution report."""

    analysis_id: str
    rp_id: str
    status: str
    compiled_request: AnalysisRequest | None = None
    result: AnalysisResult | None = None
    objective_defect: str | None = None
    binding_map: Mapping[str, str] = field(default_factory=dict)
    mechanical_repairs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class BatchExecutionReport:
    """Consolidated deterministic return after all executable batch branches finish."""

    records: tuple[BatchAnalysisRecord, ...]

    @property
    def successful(self) -> tuple[BatchAnalysisRecord, ...]:
        return tuple(record for record in self.records if record.status == "SUCCESS")

    @property
    def failed(self) -> tuple[BatchAnalysisRecord, ...]:
        return tuple(record for record in self.records if record.status != "SUCCESS")
