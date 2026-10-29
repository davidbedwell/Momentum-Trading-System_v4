from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, runtime_checkable

from Engines.Analysis.models import CompatibilityAssessment, ScientificExecutionContext


@dataclass(frozen=True, slots=True)
class AnalysisServices:
    """Explicit task-local services available to Analysis methods.

    Phase D intentionally keeps this generic. Later phases may supply governed
    deterministic computation, cache, and publication services without methods
    reaching into global engine state.
    """

    values: Mapping[str, Any] = field(default_factory=dict)

    def get(self, name: str, default: Any = None) -> Any:
        return self.values.get(name, default)


@dataclass(frozen=True, slots=True)
class MethodResult:
    scientific_result: Mapping[str, Any] = field(default_factory=dict)
    candidate_intermediates: tuple[Mapping[str, Any], ...] = ()
    durable_evidence_candidates: tuple[Mapping[str, Any], ...] = ()
    finding_candidates: tuple[Mapping[str, Any], ...] = ()
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    deterministic_computations_used: tuple[Mapping[str, Any], ...] = ()
    sample_record: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class MethodValidationResult:
    passed: bool
    reasons: tuple[str, ...] = ()


@runtime_checkable
class AnalysisMethod(Protocol):
    method_id: str
    version: str

    def assess(
        self,
        context: ScientificExecutionContext,
        inputs: Any,
    ) -> CompatibilityAssessment:
        ...

    def execute(
        self,
        context: ScientificExecutionContext,
        inputs: Any,
        services: AnalysisServices,
    ) -> MethodResult:
        ...

    def validate(
        self,
        result: MethodResult,
        context: ScientificExecutionContext,
    ) -> MethodValidationResult:
        ...
