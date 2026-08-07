from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .compatibility import CompatibilityInput, CompatibilityService
from .methods.base import AnalysisMethod, AnalysisServices, MethodResult
from .models import CompatibilityAssessment, CompatibilityState, ScientificExecutionContext
from .registry import AnalysisMethodRegistry, AnalysisMethodSpec


class AnalysisMethodExecutionError(RuntimeError):
    pass


class AnalysisMethodValidationError(AnalysisMethodExecutionError):
    pass


@dataclass(frozen=True, slots=True)
class MethodExecutionOutcome:
    method_id: str
    method_version: str
    compatibility: CompatibilityAssessment
    result: MethodResult | None
    validation_passed: bool | None
    validation_reasons: tuple[str, ...] = ()


class MethodImplementationRegistry:
    """Runtime implementation map separate from governed capability metadata."""

    def __init__(self, implementations: Sequence[AnalysisMethod] = ()) -> None:
        self._implementations = {}
        for implementation in implementations:
            key = (implementation.method_id, implementation.version)
            if key in self._implementations:
                raise AnalysisMethodExecutionError(
                    f"Duplicate Analysis method implementation: {key}"
                )
            self._implementations[key] = implementation

    def get(self, method_id: str, version: str) -> AnalysisMethod:
        try:
            return self._implementations[(method_id, version)]
        except KeyError as exc:
            raise AnalysisMethodExecutionError(
                f"No runtime implementation for {method_id}@{version}"
            ) from exc


class MethodExecutionService:
    """Bounded local method execution under governed registry + context."""

    def __init__(
        self,
        *,
        registry: AnalysisMethodRegistry,
        implementations: MethodImplementationRegistry,
        compatibility: CompatibilityService | None = None,
    ) -> None:
        self.registry = registry
        self.implementations = implementations
        self.compatibility = compatibility or CompatibilityService()

    def resolve_specs(
        self,
        context: ScientificExecutionContext,
        *,
        requested_method_ids: Sequence[str] = (),
        allowed_method_families: Sequence[str] = (),
    ) -> tuple[AnalysisMethodSpec, ...]:
        if requested_method_ids:
            return tuple(self.registry.get(method_id) for method_id in requested_method_ids)

        resolved = []
        for family in allowed_method_families:
            resolved.extend(self.registry.by_family(family))
        # deterministic order and de-duplication by method_id
        unique = {spec.method_id: spec for spec in resolved}
        return tuple(unique[key] for key in sorted(unique))

    def execute_one(
        self,
        spec: AnalysisMethodSpec,
        *,
        context: ScientificExecutionContext,
        compatibility_input: CompatibilityInput,
        method_inputs: Any,
        services: AnalysisServices | None = None,
    ) -> MethodExecutionOutcome:
        assessment = self.compatibility.assess(spec, context, compatibility_input)
        if assessment.state is not CompatibilityState.COMPATIBLE:
            return MethodExecutionOutcome(
                method_id=spec.method_id,
                method_version=spec.version,
                compatibility=assessment,
                result=None,
                validation_passed=None,
            )

        implementation = self.implementations.get(spec.method_id, spec.version)
        result = implementation.execute(
            context,
            method_inputs,
            services or AnalysisServices(),
        )
        validation = implementation.validate(result, context)
        if not validation.passed:
            raise AnalysisMethodValidationError(
                f"Method validation failed for {spec.method_id}@{spec.version}: "
                f"{validation.reasons}"
            )
        return MethodExecutionOutcome(
            method_id=spec.method_id,
            method_version=spec.version,
            compatibility=assessment,
            result=result,
            validation_passed=True,
            validation_reasons=validation.reasons,
        )
