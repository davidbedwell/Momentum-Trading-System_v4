from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from .models import AnalysisTask, ResearchMode, ScientificExecutionContext
from .nexus_adapter import ResolvedInput


class ContextConstructionError(ValueError):
    """Raised when a governed Analysis task cannot form a valid scientific context."""


@dataclass(frozen=True, slots=True)
class ContextConstructionResult:
    context: ScientificExecutionContext
    input_summaries: tuple[Mapping[str, Any], ...]


class ScientificContextBuilder:
    """Build an immutable scientific execution context from task + governed inputs."""

    def build(
        self,
        task: AnalysisTask,
        resolved_inputs: Sequence[ResolvedInput],
        *,
        as_of_time: datetime | None = None,
        software_version: str = "analysis-v2",
    ) -> ContextConstructionResult:
        if not resolved_inputs:
            raise ContextConstructionError("At least one resolved governed input is required")

        expected_refs = tuple(task.input_artifact_refs)
        actual_refs = tuple(item.artifact_ref for item in resolved_inputs)
        if actual_refs != expected_refs:
            raise ContextConstructionError(
                "Resolved input references must exactly match AnalysisTask input_artifact_refs "
                "in order and identity"
            )

        temporal = dict(task.temporal_spec)
        sample = dict(task.sample_spec)
        mode_text = str(
            temporal.get(
                "research_mode",
                sample.get("research_mode", task.configuration.get("research_mode", "EXPLORATORY")),
            )
        )
        try:
            research_mode = ResearchMode(mode_text)
        except ValueError as exc:
            raise ContextConstructionError(f"Unsupported research mode: {mode_text}") from exc

        selected_as_of = as_of_time or datetime.now(timezone.utc)
        if selected_as_of.tzinfo is None or selected_as_of.utcoffset() is None:
            raise ContextConstructionError("as_of_time must be timezone-aware")

        context = ScientificExecutionContext(
            task_id=task.task_id,
            research_plan_ref=task.research_plan_ref,
            question_ref=task.question_ref,
            input_artifact_refs=task.input_artifact_refs,
            as_of_time=selected_as_of,
            universe_scope=dict(task.scope.get("universe", task.scope)),
            date_range=dict(sample.get("date_range", {})),
            eligible_population=dict(sample.get("eligible_population", {})),
            sample_construction_rule={
                "version": sample.get("version", "sample-construction-v1"),
                "inclusion_rules": list(sample.get("inclusion_rules", [])),
                "exclusion_rules": list(sample.get("exclusion_rules", [])),
                "missing_data_policy": sample.get(
                    "missing_data_policy", "EXCLUDE_REQUIRED_MISSING"
                ),
            },
            exclusion_rule={"rules": list(sample.get("exclusion_rules", []))},
            event_or_opportunity_definition=dict(
                sample.get("event_definition", task.outcome_spec.get("event_definition", {}))
            ),
            comparison_or_control_definition=dict(
                sample.get("comparison_definition", task.comparison_spec)
            ),
            overlap_policy=dict(
                sample.get("overlap_policy", task.overlap_spec or {"policy": "ALLOW"})
            ),
            future_information_policy=dict(
                temporal.get(
                    "future_information_policy",
                    sample.get("selection_information_policy", {}),
                )
            ),
            research_mode=research_mode,
            discovery_interval=dict(temporal.get("discovery_interval", {})),
            validation_interval=dict(temporal.get("validation_interval", {})),
            holdout_interval=dict(temporal.get("holdout_interval", {})),
            method_specs=tuple(
                {"method_id": method_id} for method_id in task.requested_method_ids
            ),
            deterministic_computation_specs=tuple(
                task.configuration.get("deterministic_computation_specs", ())
            ),
            parameters=dict(task.configuration.get("parameters", {})),
            random_seed=task.random_seed,
            software_version=software_version,
        )

        return ContextConstructionResult(
            context=context,
            input_summaries=tuple(item.to_summary() for item in resolved_inputs),
        )
