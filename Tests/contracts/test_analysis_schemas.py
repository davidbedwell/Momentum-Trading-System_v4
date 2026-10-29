from datetime import datetime, timezone

import pytest

from Core.research_nexus.models import ArtifactReference
from Core.research_nexus.schema_registry import SchemaRegistry
from Core.research_nexus.validation import SchemaValidationError, SchemaValidator
from Engines.Analysis import AnalysisTask, ResearchMode, ScientificExecutionContext


ANALYSIS_SCHEMAS = {
    "mts.analysis-task",
    "mts.scientific-execution-context",
    "mts.analysis-execution",
    "mts.analysis-evidence",
    "mts.analysis-finding",
    "mts.analysis-missing-evidence",
    "mts.analysis-missing-capability",
}


def ref(name: str) -> ArtifactReference:
    return ArtifactReference(f"artifact:{name}", 1)


def test_analysis_schemas_are_registered():
    registry = SchemaRegistry()
    identities = set(registry.identities())
    for schema_id in ANALYSIS_SCHEMAS:
        assert (schema_id, 1) in identities


def test_analysis_task_validates():
    task = AnalysisTask(
        task_id="task:analysis:test",
        task_version=1,
        research_plan_ref=ref("plan"),
        question_ref=ref("question"),
        input_artifact_refs=(ref("market"),),
        requested_objective="Characterize governed market history.",
    )
    SchemaValidator().validate(
        task.to_payload(),
        schema_id="mts.analysis-task",
        schema_version=1,
    )


def test_context_validates():
    context = ScientificExecutionContext(
        task_id="task:analysis:test",
        research_plan_ref=ref("plan"),
        question_ref=ref("question"),
        input_artifact_refs=(ref("market"),),
        as_of_time=datetime(2026, 8, 7, 19, 0, tzinfo=timezone.utc),
        universe_scope={"symbols": ["SMH"]},
        date_range={"start": "2020-01-01", "end": "2026-07-31"},
        eligible_population={"rule": "all_valid_rows"},
        sample_construction_rule={"rule": "all_valid_rows"},
        exclusion_rule={},
        event_or_opportunity_definition={},
        comparison_or_control_definition={},
        overlap_policy={"policy": "ALLOW"},
        future_information_policy={"predictors": "CONTEMPORANEOUS_ONLY"},
        research_mode=ResearchMode.EXPLORATORY,
    )
    SchemaValidator().validate(
        context.to_payload(),
        schema_id="mts.scientific-execution-context",
        schema_version=1,
    )


def test_analysis_task_rejects_local_path_substitution_for_reference():
    payload = AnalysisTask(
        task_id="task:analysis:test",
        task_version=1,
        research_plan_ref=ref("plan"),
        question_ref=ref("question"),
        input_artifact_refs=(ref("market"),),
        requested_objective="Characterize governed market history.",
    ).to_payload()
    payload["input_artifact_refs"] = [{"path": "/tmp/market.parquet"}]

    with pytest.raises(SchemaValidationError):
        SchemaValidator().validate(
            payload,
            schema_id="mts.analysis-task",
            schema_version=1,
        )
