from Engines.Analysis.execution import MethodExecutionService, MethodImplementationRegistry
from Engines.Analysis.compatibility import CompatibilityInput
from Engines.Analysis.methods import INITIAL_METHODS
from Engines.Analysis.registry import AnalysisMethodRegistry
from Engines.Analysis.nexus_adapter import ResolvedInput
from Core.research_nexus.models import ArtifactReference
from Tests.analysis_methods.test_foundation import context


def test_all_initial_registry_methods_have_runtime_implementations():
    registry = AnalysisMethodRegistry.from_csv(
        "Governance/Registries/Tool-System/ANALYSIS_METHOD_LIBRARY_V2.csv"
    )
    implementations = MethodImplementationRegistry(INITIAL_METHODS)
    for spec in registry.active():
        impl = implementations.get(spec.method_id, spec.version)
        assert impl.method_id == spec.method_id


def test_foundation_runs_through_phase_d_execution_chassis():
    registry = AnalysisMethodRegistry.from_csv(
        "Governance/Registries/Tool-System/ANALYSIS_METHOD_LIBRARY_V2.csv"
    )
    service = MethodExecutionService(
        registry=registry,
        implementations=MethodImplementationRegistry(INITIAL_METHODS),
    )
    ref = ArtifactReference("artifact:market", 1)
    resolved = ResolvedInput(
        artifact_ref=ref,
        artifact_type="NORMALIZED_DATASET",
        schema_name="mts.market-history",
        schema_version=1,
        payload={},
        integrity_state="VERIFIED",
        provenance_summary={},
        media_type="application/json",
        content_hash="sha256:" + "a"*64,
    )
    spec = registry.get("analysis.foundation.dataset-introspection")
    rows = [{"date":"2026-01-01T00:00:00Z","close":1.0}]
    outcome = service.execute_one(
        spec,
        context=context(),
        compatibility_input=CompatibilityInput((resolved,), sample_observations=1),
        method_inputs=rows,
    )
    assert outcome.validation_passed is True
    assert outcome.result.scientific_result["row_count"] == 1
