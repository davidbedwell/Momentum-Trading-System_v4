#!/usr/bin/env python3
from pathlib import Path

path = Path("Governance/Utilities/run_smh_analysis_vertical_proof.py")
text = path.read_text()

imports_old = "from Engines.Analysis.compatibility import CompatibilityInput\nfrom Engines.Analysis.context import ScientificContextBuilder\n"
imports_new = "from Engines.Analysis.cache import ResearchCache\nfrom Engines.Analysis.compatibility import CompatibilityInput\nfrom Engines.Analysis.context import ScientificContextBuilder\n"
if imports_old not in text:
    raise SystemExit("Expected Analysis import anchor not found.")
text = text.replace(imports_old, imports_new, 1)

anchor_old = """        first = analyze_once(task, resolved, as_of)
        second = analyze_once(task, resolved, as_of)

        evidence_same = (
"""
anchor_new = """        first = analyze_once(task, resolved, as_of)
        second = analyze_once(task, resolved, as_of)

        research_cache = ResearchCache(
            Path(temp) / "analysis-cache",
            task_id=task.task_id,
        )
        cache_entry = research_cache.put_json(
            "candidate-comparison",
            {
                "pairwise": first["pairwise"],
                "sample_fingerprint": first["sample"].record.sample_fingerprint,
                "candidate_only": True,
            },
        )
        cache_created = research_cache.exists(cache_entry)

        evidence_same = (
"""
if anchor_old not in text:
    raise SystemExit("Expected vertical-proof execution anchor not found.")
text = text.replace(anchor_old, anchor_new, 1)

retrieval_old = """        loaded_f = analysis_nexus.resolve_artifact(
            first_f.artifact_ref,
            expected_artifact_types=("FINDING",),
        )

        retry_e = publisher.publish_evidence(
"""
retrieval_new = """        loaded_f = analysis_nexus.resolve_artifact(
            first_f.artifact_ref,
            expected_artifact_types=("FINDING",),
        )

        research_cache.clear_task()
        cache_deleted = not cache_entry.path.exists()

        retry_e = publisher.publish_evidence(
"""
if retrieval_old not in text:
    raise SystemExit("Expected durable retrieval anchor not found.")
text = text.replace(retrieval_old, retrieval_new, 1)

assertion_old = """            "deterministic_library_access": (
                set(first["deterministic"].measurements_computed)
                == {"return_close", "sma_20"}
            ),
            "finding_schema_valid": loaded_f.schema_name == "mts.analysis-finding",
"""
assertion_new = """            "deterministic_library_access": (
                set(first["deterministic"].measurements_computed)
                == {"return_close", "sma_20"}
            ),
            "cache_is_transient": (
                cache_created
                and cache_entry.persistence_class == "CLASS_III"
                and cache_entry.authoritative is False
                and cache_deleted
            ),
            "durable_output_survives_cache_deletion": (
                loaded_e.integrity_state == "VERIFIED"
                and loaded_f.integrity_state == "VERIFIED"
            ),
            "finding_schema_valid": loaded_f.schema_name == "mts.analysis-finding",
"""
if assertion_old not in text:
    raise SystemExit("Expected assertion anchor not found.")
text = text.replace(assertion_old, assertion_new, 1)

report_old = """            f"methods_executed: {tuple(first['outcomes'])}",
            f"comparison: {json.dumps(first['pairwise'], sort_keys=True)}",
"""
report_new = """            f"methods_executed: {tuple(first['outcomes'])}",
            f"cache_created: {cache_created}",
            f"cache_persistence_class: {cache_entry.persistence_class}",
            f"cache_authoritative: {cache_entry.authoritative}",
            f"cache_deleted_before_final_retry: {cache_deleted}",
            f"comparison: {json.dumps(first['pairwise'], sort_keys=True)}",
"""
if report_old not in text:
    raise SystemExit("Expected report anchor not found.")
text = text.replace(report_old, report_new, 1)

path.write_text(text)
print("SMH vertical proof patched for Research Cache separation.")
