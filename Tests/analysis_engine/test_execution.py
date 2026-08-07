from datetime import datetime, timezone
from pathlib import Path

import pytest

from Core.research_nexus.models import ArtifactReference
from Engines.Analysis.compatibility import CompatibilityInput
from Engines.Analysis.execution import (
    AnalysisMethodValidationError,
    MethodExecutionService,
    MethodImplementationRegistry,
)
from Engines.Analysis.methods.base import AnalysisServices, MethodResult, MethodValidationResult
from Engines.Analysis.models import (
    CompatibilityAssessment,
    CompatibilityState,
    ResearchMode,
    ScientificExecutionContext,
)
from Engines.Analysis.nexus_adapter import ResolvedInput
from Engines.Analysis.registry import AnalysisMethodRegistry


class FoundationStub:
    method_id = "analysis.foundation.dataset-introspection"
    version = "1"

    def assess(self, context, inputs):
        return CompatibilityAssessment(
            state=CompatibilityState.COMPATIBLE,
            method_id=self.method_id,
        )

    def execute(self, context, inputs, services):
        return MethodResult(scientific_result={"rows": len(inputs)})

    def validate(self, result, context):
        return MethodValidationResult(passed=True)


class InvalidFoundationStub(FoundationStub):
    def validate(self, result, context):
        return MethodValidationResult(passed=False, reasons=("synthetic failure",))


def ref(name):
    return ArtifactReference(f"artifact:{name}", 1)


def context():
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
        research_mode=ResearchMode.EXPLORATORY,
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


def service(impl):
    registry = AnalysisMethodRegistry.from_csv(
        "Governance/Registries/Tool-System/ANALYSIS_METHOD_LIBRARY_V2.csv"
    )
    return MethodExecutionService(
        registry=registry,
        implementations=MethodImplementationRegistry((impl,)),
    )


def test_explicit_method_resolution_wins():
    specs = service(FoundationStub()).resolve_specs(
        context(),
        requested_method_ids=("analysis.foundation.dataset-introspection",),
        allowed_method_families=("DESCRIPTIVE",),
    )
    assert [spec.method_id for spec in specs] == [
        "analysis.foundation.dataset-introspection"
    ]


def test_execution_occurs_only_when_compatible_and_valid():
    svc = service(FoundationStub())
    spec = svc.registry.get("analysis.foundation.dataset-introspection")
    outcome = svc.execute_one(
        spec,
        context=context(),
        compatibility_input=CompatibilityInput((resolved(),), sample_observations=1),
        method_inputs=({"x": 1}, {"x": 2}),
        services=AnalysisServices(),
    )
    assert outcome.validation_passed is True
    assert outcome.result.scientific_result == {"rows": 2}


def test_incompatible_method_is_not_executed():
    svc = service(FoundationStub())
    spec = svc.registry.get("analysis.foundation.dataset-introspection")
    wrong = ResolvedInput(
        artifact_ref=ref("wrong"),
        artifact_type="FINDING",
        schema_name="mts.analysis-finding",
        schema_version=1,
        payload={},
        integrity_state="VERIFIED",
        provenance_summary={},
        media_type="application/json",
        content_hash="sha256:" + "b" * 64,
    )
    outcome = svc.execute_one(
        spec,
        context=context(),
        compatibility_input=CompatibilityInput((wrong,), sample_observations=1),
        method_inputs=(),
    )
    assert outcome.compatibility.state is CompatibilityState.INVALID_SCOPE
    assert outcome.result is None


def test_method_validation_failure_raises():
    svc = service(InvalidFoundationStub())
    spec = svc.registry.get("analysis.foundation.dataset-introspection")
    with pytest.raises(AnalysisMethodValidationError, match="synthetic failure"):
        svc.execute_one(
            spec,
            context=context(),
            compatibility_input=CompatibilityInput((resolved(),), sample_observations=1),
            method_inputs=(),
        )
