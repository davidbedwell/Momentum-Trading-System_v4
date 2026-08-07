from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .models import CompatibilityAssessment, CompatibilityState, ScientificExecutionContext
from .nexus_adapter import ResolvedInput
from .registry import AnalysisMethodSpec


@dataclass(frozen=True, slots=True)
class CompatibilityInput:
    resolved_inputs: tuple[ResolvedInput, ...]
    available_measurements: tuple[str, ...] = ()
    sample_observations: int | None = None


class CompatibilityService:
    """Evaluate registry-declared method requirements before execution."""

    def assess(
        self,
        spec: AnalysisMethodSpec,
        context: ScientificExecutionContext,
        inputs: CompatibilityInput,
    ) -> CompatibilityAssessment:
        reasons = []

        if spec.status != "ACTIVE":
            return CompatibilityAssessment(
                state=CompatibilityState.NOT_APPLICABLE,
                method_id=spec.method_id,
                reasons=(f"Method status is {spec.status}",),
            )

        artifact_types = tuple(item.artifact_type for item in inputs.resolved_inputs)
        if spec.required_inputs and not artifact_types:
            return CompatibilityAssessment(
                state=CompatibilityState.MISSING_INPUT,
                method_id=spec.method_id,
                reasons=("No governed inputs resolved.",),
                missing_inputs=spec.required_inputs,
            )

        incompatible = tuple(
            artifact_type
            for artifact_type in artifact_types
            if spec.compatible_artifact_types
            and artifact_type not in spec.compatible_artifact_types
        )
        if incompatible:
            return CompatibilityAssessment(
                state=CompatibilityState.INVALID_SCOPE,
                method_id=spec.method_id,
                reasons=(f"Incompatible artifact types: {incompatible}",),
            )

        missing_measurements = tuple(
            measurement
            for measurement in spec.required_measurements
            if measurement not in set(inputs.available_measurements)
        )
        if missing_measurements:
            return CompatibilityAssessment(
                state=CompatibilityState.MISSING_MEASUREMENT,
                method_id=spec.method_id,
                missing_measurements=missing_measurements,
                reasons=("Required deterministic measurements are unavailable in current input.",),
            )

        if (
            inputs.sample_observations is not None
            and inputs.sample_observations < spec.minimum_sample
        ):
            return CompatibilityAssessment(
                state=CompatibilityState.INSUFFICIENT_SAMPLE,
                method_id=spec.method_id,
                sample_observations=inputs.sample_observations,
                reasons=(
                    f"Sample {inputs.sample_observations} < minimum {spec.minimum_sample}",
                ),
            )

        if (
            spec.research_mode_compatibility
            and context.research_mode not in spec.research_mode_compatibility
        ):
            return CompatibilityAssessment(
                state=CompatibilityState.NOT_APPLICABLE,
                method_id=spec.method_id,
                reasons=(
                    f"Research mode {context.research_mode.value} is not compatible.",
                ),
            )

        if spec.random_seed_requirement == "REQUIRED" and context.random_seed is None:
            return CompatibilityAssessment(
                state=CompatibilityState.INVALID_SCOPE,
                method_id=spec.method_id,
                reasons=("Method requires random_seed in ScientificExecutionContext.",),
            )

        return CompatibilityAssessment(
            state=CompatibilityState.COMPATIBLE,
            method_id=spec.method_id,
            reasons=tuple(reasons),
            sample_observations=inputs.sample_observations,
        )
