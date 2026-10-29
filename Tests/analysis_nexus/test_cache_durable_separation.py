from datetime import datetime, timezone

from Core.research_nexus import ArtifactReference, ResearchNexusConfig, build_research_nexus
from Engines.Analysis.cache import ResearchCache
from Engines.Analysis.models import AnalysisEvidence, ResearchMode
from Engines.Analysis.nexus_adapter import AnalysisNexusAdapter
from Engines.Analysis.publication import AnalysisNexusPublisher


def ref(name):
    return ArtifactReference(f"artifact:{name}", 1)


def test_cache_deletion_does_not_delete_published_evidence(tmp_path):
    nexus = build_research_nexus(
        ResearchNexusConfig(runtime_root=tmp_path / "nexus")
    )
    cache = ResearchCache(tmp_path / "cache", task_id="task:cache-proof")
    cached = cache.put_json(
        "candidate-comparison",
        {"mean_difference": 0.123, "candidate_only": True},
    )

    evidence = AnalysisEvidence(
        evidence_id="evidence:cache-proof",
        task_id="task:cache-proof",
        execution_id="execution:cache-proof",
        context_fingerprint="a" * 64,
        method_id="analysis.comparison.cohort-outcome",
        method_version="1",
        input_artifact_refs=(ref("market"),),
        sample_definition={"rows": 10},
        result={"mean_difference": 0.123},
        research_mode=ResearchMode.EXPLORATORY,
    )
    published = AnalysisNexusPublisher(nexus).publish_evidence(
        evidence,
        created_at=datetime(2026, 8, 7, 19, tzinfo=timezone.utc),
    )

    cache.clear_task()
    assert not cached.path.exists()

    resolved = AnalysisNexusAdapter(nexus).resolve_artifact(
        published.artifact_ref,
        expected_artifact_types=("EVIDENCE",),
    )
    assert resolved.integrity_state == "VERIFIED"
    assert resolved.payload["result"]["mean_difference"] == 0.123
