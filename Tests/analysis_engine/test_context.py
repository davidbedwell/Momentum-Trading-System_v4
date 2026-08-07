from datetime import datetime, timezone

import pytest

from Core.research_nexus.models import ArtifactReference
from Engines.Analysis import AnalysisTask, ResearchMode
from Engines.Analysis.context import ContextConstructionError, ScientificContextBuilder
from Engines.Analysis.nexus_adapter import ResolvedInput


def ref(name):
    return ArtifactReference(f"artifact:{name}", 1)


def resolved(name):
    return ResolvedInput(
        artifact_ref=ref(name),
        artifact_type="NORMALIZED_DATASET",
        schema_name="mts.market-history",
        schema_version=1,
        payload={"symbol": "SMH"},
        integrity_state="VERIFIED",
        provenance_summary={"software_version": "intake-v2"},
        media_type="application/json",
        content_hash="sha256:" + "a" * 64,
    )


def task():
    return AnalysisTask(
        task_id="task:phase-c",
        task_version=1,
        research_plan_ref=ref("plan"),
        question_ref=ref("question"),
        input_artifact_refs=(ref("market"),),
        requested_objective="Build scientific context.",
        requested_method_ids=("analysis.foundation.dataset-introspection",),
        scope={"universe": {"symbols": ["SMH"]}},
        sample_spec={
            "date_range": {
                "start": "2020-01-01T00:00:00Z",
                "end": "2026-07-31T00:00:00Z",
            },
            "research_mode": "EXPLORATORY",
            "overlap_policy": {"policy": "ALLOW"},
        },
        temporal_spec={
            "future_information_policy": {
                "predictors": "CONTEMPORANEOUS_ONLY"
            }
        },
    )


def test_context_builder_preserves_governed_task_identity_and_mode():
    result = ScientificContextBuilder().build(
        task(),
        (resolved("market"),),
        as_of_time=datetime(2026, 8, 7, 19, tzinfo=timezone.utc),
    )
    assert result.context.task_id == "task:phase-c"
    assert result.context.research_mode is ResearchMode.EXPLORATORY
    assert result.context.input_artifact_refs == (ref("market"),)
    assert len(result.context.context_fingerprint) == 64


def test_context_builder_rejects_resolved_input_mismatch():
    with pytest.raises(ContextConstructionError, match="exactly match"):
        ScientificContextBuilder().build(
            task(),
            (resolved("wrong"),),
            as_of_time=datetime(2026, 8, 7, 19, tzinfo=timezone.utc),
        )


def test_context_fingerprint_repeats_for_same_context():
    builder = ScientificContextBuilder()
    as_of = datetime(2026, 8, 7, 19, tzinfo=timezone.utc)
    first = builder.build(task(), (resolved("market"),), as_of_time=as_of)
    second = builder.build(task(), (resolved("market"),), as_of_time=as_of)
    assert first.context.context_fingerprint == second.context.context_fingerprint
