from datetime import datetime, timezone

import pytest

from Core.research_nexus.models import ArtifactReference
from Engines.Analysis import (
    AnalysisEvidence,
    AnalysisFinding,
    AnalysisTask,
    ResearchMode,
    ScientificExecutionContext,
    ScientificOutcome,
)


def ref(name: str) -> ArtifactReference:
    return ArtifactReference(f"artifact:{name}", 1)


def test_analysis_task_payload_uses_governed_references_not_paths():
    task = AnalysisTask(
        task_id="task:analysis:test",
        task_version=1,
        research_plan_ref=ref("plan"),
        question_ref=ref("question"),
        input_artifact_refs=(ref("market"),),
        requested_objective="Characterize dataset.",
    )
    payload = task.to_payload()
    assert payload["task_type"] == "ANALYSIS"
    assert payload["input_artifact_refs"] == [
        {"artifact_id": "artifact:market", "artifact_version": 1}
    ]
    assert "path" not in str(payload).lower()


def test_context_requires_timezone_aware_as_of_time():
    with pytest.raises(ValueError, match="timezone-aware"):
        ScientificExecutionContext(
            task_id="task:analysis:test",
            research_plan_ref=ref("plan"),
            question_ref=ref("question"),
            input_artifact_refs=(ref("market"),),
            as_of_time=datetime(2026, 8, 7, 12, 0, 0),
            universe_scope={},
            date_range={},
            eligible_population={},
            sample_construction_rule={},
            exclusion_rule={},
            event_or_opportunity_definition={},
            comparison_or_control_definition={},
            overlap_policy={},
            future_information_policy={},
            research_mode=ResearchMode.EXPLORATORY,
        )


def test_context_fingerprint_is_deterministic():
    kwargs = dict(
        task_id="task:analysis:test",
        research_plan_ref=ref("plan"),
        question_ref=ref("question"),
        input_artifact_refs=(ref("market"),),
        as_of_time=datetime(2026, 8, 7, 19, 0, tzinfo=timezone.utc),
        universe_scope={"symbols": ["SMH"]},
        date_range={"start": "2020-01-01", "end": "2026-07-31"},
        eligible_population={"rows": "all_valid"},
        sample_construction_rule={"rule": "all"},
        exclusion_rule={},
        event_or_opportunity_definition={},
        comparison_or_control_definition={},
        overlap_policy={"policy": "ALLOW"},
        future_information_policy={"predictors": "CONTEMPORANEOUS_ONLY"},
        research_mode=ResearchMode.EXPLORATORY,
    )
    first = ScientificExecutionContext(**kwargs)
    second = ScientificExecutionContext(**kwargs)
    assert first.context_fingerprint == second.context_fingerprint


def test_evidence_and_finding_have_distinct_scientific_identity():
    evidence = AnalysisEvidence(
        evidence_id="evidence:test",
        task_id="task:test",
        execution_id="execution:test",
        context_fingerprint="a" * 64,
        method_id="analysis.foundation.dataset-introspection",
        method_version="1",
        input_artifact_refs=(ref("market"),),
        sample_definition={"rows": 100},
        result={"mean": 1.0},
    )
    finding = AnalysisFinding(
        finding_id="finding:test",
        task_id="task:test",
        research_plan_ref=ref("plan"),
        question_ref=ref("question"),
        input_artifact_refs=(ref("market"),),
        method_id="analysis.foundation.dataset-introspection",
        method_version="1",
        sample_definition={"rows": 100},
        result_proposition="Dataset contains 100 eligible rows.",
        scientific_outcome=ScientificOutcome.SUPPORTED,
        supporting_evidence_refs=(ref("evidence"),),
    )
    assert evidence.semantic_fingerprint != finding.semantic_fingerprint
