from datetime import datetime, timezone

from Core.research_nexus.models import ArtifactReference
from Engines.Analysis.methods.foundation import FoundationDatasetIntrospectionMethod
from Engines.Analysis.methods.base import AnalysisServices
from Engines.Analysis.models import ResearchMode, ScientificExecutionContext


def context(parameters=None):
    ref = ArtifactReference("artifact:x", 1)
    return ScientificExecutionContext(
        task_id="task:x", research_plan_ref=ref, question_ref=ref,
        input_artifact_refs=(ref,), as_of_time=datetime(2026,8,7,tzinfo=timezone.utc),
        universe_scope={}, date_range={}, eligible_population={},
        sample_construction_rule={}, exclusion_rule={}, event_or_opportunity_definition={},
        comparison_or_control_definition={}, overlap_policy={"policy":"ALLOW"},
        future_information_policy={}, research_mode=ResearchMode.EXPLORATORY,
        parameters=parameters or {},
    )


def test_foundation_introspection_reports_structure_without_trading_meaning():
    rows = [
        {"date":"2026-01-01T00:00:00Z","open":1.0,"high":2.0,"low":0.5,"close":1.5,"volume":100,"sma_20":1.2},
        {"date":"2026-01-02T00:00:00Z","open":1.5,"high":2.2,"low":1.0,"close":2.0,"volume":120,"sma_20":None},
    ]
    method = FoundationDatasetIntrospectionMethod()
    result = method.execute(context(), rows, AnalysisServices())
    assert result.scientific_result["row_count"] == 2
    assert result.scientific_result["missingness"]["sma_20"] == 1
    assert "sma_20" in result.scientific_result["measurement_columns"]
    assert method.validate(result, context()).passed
