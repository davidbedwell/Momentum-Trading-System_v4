from datetime import datetime, timezone

from Core.research_nexus.models import ArtifactReference
from Engines.Analysis.compatibility import CompatibilityInput, CompatibilityService
from Engines.Analysis.deterministic import DeterministicMeasurementResolver
from Engines.Analysis.models import CompatibilityState, ResearchMode, ScientificExecutionContext
from Engines.Analysis.nexus_adapter import ResolvedInput
from Engines.Analysis.registry import AnalysisMethodRegistry


def ref(name):
    return ArtifactReference(f"artifact:{name}", 1)


def context():
    return ScientificExecutionContext(
        task_id="task:f",
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
        research_mode=ResearchMode.EXPLORATORY,
    )


def resolved():
    return ResolvedInput(
        artifact_ref=ref("market"),
        artifact_type="NORMALIZED_DATASET",
        schema_name="mts.market-history",
        schema_version=1,
        payload={},
        integrity_state="VERIFIED",
        provenance_summary={},
        media_type="application/json",
        content_hash="sha256:" + "a"*64,
    )


def test_computed_measurement_can_satisfy_compatibility_requirement(tmp_path):
    # Create a temporary clean-v2 method spec requiring sma_20.
    source = (
        "Governance/Registries/Tool-System/ANALYSIS_METHOD_LIBRARY_V2.csv"
    )
    text = open(source).read()
    text = text.replace(
        "analysis.foundation.dataset-introspection,Foundation Dataset Introspection,FOUNDATION,1,ACTIVE,NORMALIZED_DATASET,,,NORMALIZED_DATASET",
        "analysis.foundation.dataset-introspection,Foundation Dataset Introspection,FOUNDATION,1,ACTIVE,NORMALIZED_DATASET,,sma_20,NORMALIZED_DATASET",
        1,
    )
    registry_path = tmp_path / "registry.csv"
    registry_path.write_text(text)
    registry = AnalysisMethodRegistry.from_csv(registry_path)
    spec = registry.get("analysis.foundation.dataset-introspection")

    rows = [
        {
            "date": f"2026-01-{day:02d}T00:00:00Z",
            "open": float(100 + day),
            "high": float(101 + day),
            "low": float(99 + day),
            "close": float(100 + day),
            "volume": float(1000+day),
        }
        for day in range(1, 26)
    ]

    before = CompatibilityService().assess(
        spec,
        context(),
        CompatibilityInput((resolved(),), available_measurements=(), sample_observations=25),
    )
    assert before.state is CompatibilityState.MISSING_MEASUREMENT

    materialized = DeterministicMeasurementResolver().resolve(
        rows,
        required_measurements=spec.required_measurements,
    )

    after = CompatibilityService().assess(
        spec,
        context(),
        CompatibilityInput(
            (resolved(),),
            available_measurements=materialized.available_measurements,
            sample_observations=25,
        ),
    )
    assert after.state is CompatibilityState.COMPATIBLE
    assert materialized.measurements_computed == ("sma_20",)
