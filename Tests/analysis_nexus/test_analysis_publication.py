from datetime import datetime, timezone

from Core.research_nexus import (
    ArtifactReference,
    ResearchNexusConfig,
    build_research_nexus,
)
from Engines.Analysis.models import (
    AnalysisEvidence,
    AnalysisFinding,
    ResearchMode,
    ScientificOutcome,
)
from Engines.Analysis.nexus_adapter import AnalysisNexusAdapter
from Engines.Analysis.publication import AnalysisNexusPublisher


def ref(name: str) -> ArtifactReference:
    return ArtifactReference(f"artifact:{name}", 1)


def evidence():
    return AnalysisEvidence(
        evidence_id="evidence:test",
        task_id="task:test",
        execution_id="execution:test",
        context_fingerprint="a" * 64,
        method_id="analysis.comparison.cohort-outcome",
        method_version="1",
        input_artifact_refs=(ref("market"),),
        sample_definition={"rows": 100},
        result={"mean_difference": 0.01},
        research_mode=ResearchMode.EXPLORATORY,
    )


def finding(evidence_ref):
    return AnalysisFinding(
        finding_id="finding:test",
        task_id="task:test",
        research_plan_ref=ref("plan"),
        question_ref=ref("question"),
        input_artifact_refs=(ref("market"),),
        method_id="analysis.comparison.cohort-outcome",
        method_version="1",
        sample_definition={"rows": 100},
        result_proposition="Observed governed cohort mean difference was 0.01.",
        scientific_outcome=ScientificOutcome.SUPPORTED,
        effect_or_magnitude={"mean_difference": 0.01},
        supporting_evidence_refs=(evidence_ref,),
        research_mode=ResearchMode.EXPLORATORY,
    )


def test_evidence_and_finding_publish_retrieve_verify_and_reconcile(tmp_path):
    nexus = build_research_nexus(
        ResearchNexusConfig(runtime_root=tmp_path / "nexus")
    )
    publisher = AnalysisNexusPublisher(nexus)
    adapter = AnalysisNexusAdapter(nexus)
    created_at = datetime(2026, 8, 7, 19, tzinfo=timezone.utc)

    first_e = publisher.publish_evidence(evidence(), created_at=created_at)
    assert first_e.reconciled is False
    loaded_e = adapter.resolve_artifact(
        first_e.artifact_ref, expected_artifact_types=("EVIDENCE",)
    )
    assert loaded_e.schema_name == "mts.analysis-evidence"
    assert loaded_e.integrity_state == "VERIFIED"

    f = finding(first_e.artifact_ref)
    first_f = publisher.publish_finding(f, created_at=created_at)
    assert first_f.reconciled is False
    loaded_f = adapter.resolve_artifact(
        first_f.artifact_ref, expected_artifact_types=("FINDING",)
    )
    assert loaded_f.schema_name == "mts.analysis-finding"
    assert loaded_f.integrity_state == "VERIFIED"

    retry_e = publisher.publish_evidence(evidence(), created_at=created_at)
    retry_f = publisher.publish_finding(f, created_at=created_at)
    assert retry_e.artifact_ref == first_e.artifact_ref
    assert retry_f.artifact_ref == first_f.artifact_ref
    assert retry_e.reconciled is True
    assert retry_f.reconciled is True
