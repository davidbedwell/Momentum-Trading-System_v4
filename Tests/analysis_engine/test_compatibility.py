from datetime import datetime, timezone

from Core.research_nexus.models import ArtifactReference
from Engines.Analysis.compatibility import CompatibilityInput, CompatibilityService
from Engines.Analysis.models import (
    CompatibilityState,
    ResearchMode,
    ScientificExecutionContext,
)
from Engines.Analysis.nexus_adapter import ResolvedInput
from Engines.Analysis.registry import AnalysisMethodRegistry


def ref(name):
    return ArtifactReference(f"artifact:{name}", 1)


def context(mode=ResearchMode.EXPLORATORY, random_seed=None):
    return ScientificExecutionContext(
        task_id="task:test",
        research_plan_ref=ref("plan"),
        question_ref=ref("question"),
        input_artifact_refs=(ref("market"),),
        as_of_time=datetime(2026, 8, 7, 19, tzinfo=timezone.utc),
        universe_scope={},
        date_range={},
        eligible_population={},
        sample_construction_rule={},
        exclusion_rule={},
        event_or_opportunity_definition={},
        comparison_or_control_definition={},
        overlap_policy={"policy": "ALLOW"},
        future_information_policy={},
        research_mode=mode,
        random_seed=random_seed,
    )


def resolved():
    return ResolvedInput(
        artifact_ref=ref("market"),
        artifact_type="NORMALIZED_DATASET",
        schema_name="mts.market-history",
        schema_version=1,
        payload={"symbol": "SMH"},
        integrity_state="VERIFIED",
        provenance_summary={},
        media_type="application/json",
        content_hash="sha256:" + "a" * 64,
    )


def registry():
    return AnalysisMethodRegistry.from_csv(
        "Governance/Registries/Tool-System/ANALYSIS_METHOD_LIBRARY_V2.csv"
    )


def test_compatible_foundation_method():
    spec = registry().get("analysis.foundation.dataset-introspection")
    result = CompatibilityService().assess(
        spec,
        context(),
        CompatibilityInput((resolved(),), sample_observations=10),
    )
    assert result.state is CompatibilityState.COMPATIBLE


def test_insufficient_sample_is_explicit():
    spec = registry().get("analysis.relationship.redundancy")
    result = CompatibilityService().assess(
        spec,
        context(),
        CompatibilityInput((resolved(),), sample_observations=2),
    )
    assert result.state is CompatibilityState.INSUFFICIENT_SAMPLE


def test_research_mode_incompatibility_is_not_applicable():
    spec = registry().get("analysis.reliability.basic")
    result = CompatibilityService().assess(
        spec,
        context(ResearchMode.EXPLORATORY),
        CompatibilityInput((resolved(),), sample_observations=10),
    )
    assert result.state is CompatibilityState.NOT_APPLICABLE
