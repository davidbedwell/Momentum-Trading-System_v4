from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence

from Core.research_nexus.models import ArtifactReference

from .canonical import semantic_fingerprint


class ResearchMode(str, Enum):
    EXPLORATORY = "EXPLORATORY"
    CONFIRMATORY = "CONFIRMATORY"
    VALIDATION = "VALIDATION"
    REPLICATION = "REPLICATION"
    ROBUSTNESS = "ROBUSTNESS"
    RETROSPECTIVE_CHARACTERIZATION = "RETROSPECTIVE_CHARACTERIZATION"


class CompatibilityState(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    MISSING_INPUT = "MISSING_INPUT"
    MISSING_MEASUREMENT = "MISSING_MEASUREMENT"
    INSUFFICIENT_SAMPLE = "INSUFFICIENT_SAMPLE"
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"
    HOLDOUT_CONFLICT = "HOLDOUT_CONFLICT"
    UNSUPPORTED_METHOD = "UNSUPPORTED_METHOD"
    MISSING_CAPABILITY = "MISSING_CAPABILITY"
    INVALID_SCOPE = "INVALID_SCOPE"


class ExecutionState(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    RETRYABLE_FAILURE = "RETRYABLE_FAILURE"


class ScientificOutcome(str, Enum):
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNSTABLE = "UNSTABLE"
    MISSING_CAPABILITY = "MISSING_CAPABILITY"


def _ref_dict(ref: ArtifactReference) -> dict[str, Any]:
    return {
        "artifact_id": ref.artifact_id,
        "artifact_version": ref.artifact_version,
    }


def _refs(values: Sequence[ArtifactReference]) -> list[dict[str, Any]]:
    return [_ref_dict(value) for value in values]


@dataclass(frozen=True, slots=True)
class AnalysisTask:
    task_id: str
    task_version: int
    research_plan_ref: ArtifactReference
    question_ref: ArtifactReference
    input_artifact_refs: tuple[ArtifactReference, ...]
    requested_objective: str
    requested_method_ids: tuple[str, ...] = ()
    allowed_method_families: tuple[str, ...] = ()
    method_selection_policy: str = "EXACT_OR_EXPLICITLY_ALLOWED"
    scope: Mapping[str, Any] = field(default_factory=dict)
    sample_spec: Mapping[str, Any] = field(default_factory=dict)
    temporal_spec: Mapping[str, Any] = field(default_factory=dict)
    overlap_spec: Mapping[str, Any] = field(default_factory=dict)
    outcome_spec: Mapping[str, Any] = field(default_factory=dict)
    comparison_spec: Mapping[str, Any] = field(default_factory=dict)
    required_evaluation_criteria: Mapping[str, Any] = field(default_factory=dict)
    stopping_conditions: Mapping[str, Any] = field(default_factory=dict)
    configuration: Mapping[str, Any] = field(default_factory=dict)
    random_seed: int | None = None
    authority_metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def task_type(self) -> str:
        return "ANALYSIS"

    def to_payload(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_version": self.task_version,
            "task_type": self.task_type,
            "research_plan_ref": _ref_dict(self.research_plan_ref),
            "question_ref": _ref_dict(self.question_ref),
            "input_artifact_refs": _refs(self.input_artifact_refs),
            "requested_objective": self.requested_objective,
            "requested_method_ids": list(self.requested_method_ids),
            "allowed_method_families": list(self.allowed_method_families),
            "method_selection_policy": self.method_selection_policy,
            "scope": dict(self.scope),
            "sample_spec": dict(self.sample_spec),
            "temporal_spec": dict(self.temporal_spec),
            "overlap_spec": dict(self.overlap_spec),
            "outcome_spec": dict(self.outcome_spec),
            "comparison_spec": dict(self.comparison_spec),
            "required_evaluation_criteria": dict(self.required_evaluation_criteria),
            "stopping_conditions": dict(self.stopping_conditions),
            "configuration": dict(self.configuration),
            "random_seed": self.random_seed,
            "authority_metadata": dict(self.authority_metadata),
        }


@dataclass(frozen=True, slots=True)
class ScientificExecutionContext:
    task_id: str
    research_plan_ref: ArtifactReference
    question_ref: ArtifactReference
    input_artifact_refs: tuple[ArtifactReference, ...]
    as_of_time: datetime
    universe_scope: Mapping[str, Any]
    date_range: Mapping[str, Any]
    eligible_population: Mapping[str, Any]
    sample_construction_rule: Mapping[str, Any]
    exclusion_rule: Mapping[str, Any]
    event_or_opportunity_definition: Mapping[str, Any]
    comparison_or_control_definition: Mapping[str, Any]
    overlap_policy: Mapping[str, Any]
    future_information_policy: Mapping[str, Any]
    research_mode: ResearchMode
    discovery_interval: Mapping[str, Any] = field(default_factory=dict)
    validation_interval: Mapping[str, Any] = field(default_factory=dict)
    holdout_interval: Mapping[str, Any] = field(default_factory=dict)
    method_specs: tuple[Mapping[str, Any], ...] = ()
    deterministic_computation_specs: tuple[Mapping[str, Any], ...] = ()
    parameters: Mapping[str, Any] = field(default_factory=dict)
    random_seed: int | None = None
    software_version: str = "analysis-v2"

    def __post_init__(self) -> None:
        if self.as_of_time.tzinfo is None:
            raise ValueError("as_of_time must be timezone-aware")

    def to_payload(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "research_plan_ref": _ref_dict(self.research_plan_ref),
            "question_ref": _ref_dict(self.question_ref),
            "input_artifact_refs": _refs(self.input_artifact_refs),
            "as_of_time": self.as_of_time.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "universe_scope": dict(self.universe_scope),
            "date_range": dict(self.date_range),
            "eligible_population": dict(self.eligible_population),
            "sample_construction_rule": dict(self.sample_construction_rule),
            "exclusion_rule": dict(self.exclusion_rule),
            "event_or_opportunity_definition": dict(self.event_or_opportunity_definition),
            "comparison_or_control_definition": dict(self.comparison_or_control_definition),
            "overlap_policy": dict(self.overlap_policy),
            "future_information_policy": dict(self.future_information_policy),
            "research_mode": self.research_mode.value,
            "discovery_interval": dict(self.discovery_interval),
            "validation_interval": dict(self.validation_interval),
            "holdout_interval": dict(self.holdout_interval),
            "method_specs": [dict(value) for value in self.method_specs],
            "deterministic_computation_specs": [
                dict(value) for value in self.deterministic_computation_specs
            ],
            "parameters": dict(self.parameters),
            "random_seed": self.random_seed,
            "software_version": self.software_version,
        }

    @property
    def context_fingerprint(self) -> str:
        return semantic_fingerprint(self.to_payload())


@dataclass(frozen=True, slots=True)
class CompatibilityAssessment:
    state: CompatibilityState
    method_id: str | None = None
    reasons: tuple[str, ...] = ()
    missing_inputs: tuple[str, ...] = ()
    missing_measurements: tuple[str, ...] = ()
    sample_observations: int | None = None
    temporal_conflicts: tuple[str, ...] = ()
    holdout_conflicts: tuple[str, ...] = ()
    capability_gaps: tuple[str, ...] = ()
    valid_alternatives: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "method_id": self.method_id,
            "reasons": list(self.reasons),
            "missing_inputs": list(self.missing_inputs),
            "missing_measurements": list(self.missing_measurements),
            "sample_observations": self.sample_observations,
            "temporal_conflicts": list(self.temporal_conflicts),
            "holdout_conflicts": list(self.holdout_conflicts),
            "capability_gaps": list(self.capability_gaps),
            "valid_alternatives": list(self.valid_alternatives),
        }


@dataclass(frozen=True, slots=True)
class AnalysisExecutionRecord:
    execution_id: str
    task_id: str
    context_fingerprint: str
    engine_version: str
    input_refs: tuple[ArtifactReference, ...]
    execution_state: ExecutionState
    method_executions: tuple[Mapping[str, Any], ...] = ()
    output_refs: tuple[ArtifactReference, ...] = ()
    limitations: tuple[str, ...] = ()
    retry_of: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "context_fingerprint": self.context_fingerprint,
            "engine_version": self.engine_version,
            "input_refs": _refs(self.input_refs),
            "execution_state": self.execution_state.value,
            "method_executions": [dict(value) for value in self.method_executions],
            "output_refs": _refs(self.output_refs),
            "limitations": list(self.limitations),
            "retry_of": self.retry_of,
        }


@dataclass(frozen=True, slots=True)
class AnalysisEvidence:
    evidence_id: str
    task_id: str
    execution_id: str
    context_fingerprint: str
    method_id: str
    method_version: str
    input_artifact_refs: tuple[ArtifactReference, ...]
    sample_definition: Mapping[str, Any]
    result: Mapping[str, Any]
    uncertainty: Mapping[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    research_mode: ResearchMode = ResearchMode.EXPLORATORY
    deterministic_computations_used: tuple[Mapping[str, Any], ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "task_id": self.task_id,
            "execution_id": self.execution_id,
            "context_fingerprint": self.context_fingerprint,
            "method_id": self.method_id,
            "method_version": self.method_version,
            "input_artifact_refs": _refs(self.input_artifact_refs),
            "sample_definition": dict(self.sample_definition),
            "result": dict(self.result),
            "uncertainty": dict(self.uncertainty),
            "limitations": list(self.limitations),
            "research_mode": self.research_mode.value,
            "deterministic_computations_used": [
                dict(value) for value in self.deterministic_computations_used
            ],
        }

    @property
    def semantic_fingerprint(self) -> str:
        return semantic_fingerprint(self.to_payload())


@dataclass(frozen=True, slots=True)
class AnalysisFinding:
    finding_id: str
    task_id: str
    research_plan_ref: ArtifactReference
    question_ref: ArtifactReference
    input_artifact_refs: tuple[ArtifactReference, ...]
    method_id: str
    method_version: str
    sample_definition: Mapping[str, Any]
    result_proposition: str
    scientific_outcome: ScientificOutcome
    effect_or_magnitude: Mapping[str, Any] = field(default_factory=dict)
    uncertainty: Mapping[str, Any] = field(default_factory=dict)
    supporting_evidence_refs: tuple[ArtifactReference, ...] = ()
    contradictory_evidence_refs: tuple[ArtifactReference, ...] = ()
    applicability: Mapping[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    temporal_scope: Mapping[str, Any] = field(default_factory=dict)
    validation_state: str = "UNVALIDATED"
    research_mode: ResearchMode = ResearchMode.EXPLORATORY
    producer: Mapping[str, Any] = field(default_factory=lambda: {
        "producer_type": "ENGINE",
        "producer_id": "analysis-engine",
    })

    def to_payload(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "task_id": self.task_id,
            "research_plan_ref": _ref_dict(self.research_plan_ref),
            "question_ref": _ref_dict(self.question_ref),
            "input_artifact_refs": _refs(self.input_artifact_refs),
            "method_id": self.method_id,
            "method_version": self.method_version,
            "sample_definition": dict(self.sample_definition),
            "result_proposition": self.result_proposition,
            "scientific_outcome": self.scientific_outcome.value,
            "effect_or_magnitude": dict(self.effect_or_magnitude),
            "uncertainty": dict(self.uncertainty),
            "supporting_evidence_refs": _refs(self.supporting_evidence_refs),
            "contradictory_evidence_refs": _refs(self.contradictory_evidence_refs),
            "applicability": dict(self.applicability),
            "limitations": list(self.limitations),
            "temporal_scope": dict(self.temporal_scope),
            "validation_state": self.validation_state,
            "research_mode": self.research_mode.value,
            "producer": dict(self.producer),
        }

    @property
    def semantic_fingerprint(self) -> str:
        return semantic_fingerprint(self.to_payload())


@dataclass(frozen=True, slots=True)
class MissingEvidenceReport:
    task_id: str
    affected_question: str
    required_input: str
    reason: str
    valid_alternative_available: bool
    scientific_consequence: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "report_type": "MISSING_EVIDENCE",
            "task_id": self.task_id,
            "affected_question": self.affected_question,
            "required_input": self.required_input,
            "reason": self.reason,
            "valid_alternative_available": self.valid_alternative_available,
            "scientific_consequence": self.scientific_consequence,
        }


@dataclass(frozen=True, slots=True)
class MissingCapabilityReport:
    task_id: str
    affected_question: str
    missing_capability: str
    why_required: str
    available_alternatives: tuple[str, ...]
    scientific_consequence: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "report_type": "MISSING_CAPABILITY",
            "task_id": self.task_id,
            "affected_question": self.affected_question,
            "missing_capability": self.missing_capability,
            "why_required": self.why_required,
            "available_alternatives": list(self.available_alternatives),
            "scientific_consequence": self.scientific_consequence,
        }


@dataclass(frozen=True, slots=True)
class AnalysisTaskResult:
    task_id: str
    execution_id: str
    execution_state: ExecutionState
    compatibility_state: CompatibilityState
    scientific_outcomes: tuple[ScientificOutcome, ...] = ()
    published_artifact_refs: tuple[ArtifactReference, ...] = ()
    finding_refs: tuple[ArtifactReference, ...] = ()
    evidence_refs: tuple[ArtifactReference, ...] = ()
    missing_evidence_refs: tuple[ArtifactReference, ...] = ()
    missing_capability_refs: tuple[ArtifactReference, ...] = ()
    limitations: tuple[str, ...] = ()
    retry_metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "execution_id": self.execution_id,
            "execution_state": self.execution_state.value,
            "compatibility_state": self.compatibility_state.value,
            "scientific_outcomes": [value.value for value in self.scientific_outcomes],
            "published_artifact_refs": _refs(self.published_artifact_refs),
            "finding_refs": _refs(self.finding_refs),
            "evidence_refs": _refs(self.evidence_refs),
            "missing_evidence_refs": _refs(self.missing_evidence_refs),
            "missing_capability_refs": _refs(self.missing_capability_refs),
            "limitations": list(self.limitations),
            "retry_metadata": dict(self.retry_metadata),
        }
