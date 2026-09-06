from __future__ import annotations

import tempfile
import unittest

from MTS_V4.bootstrap import build_runtime
from MTS_V4.contracts import AnalysisRequest, Finding, ResearchDecision, ResearchPhase, SubjectMetadata
from MTS_V4.intake import IntakeEngine, IntakePayload
from MTS_V4.standard_methods import standard_method_catalog


class _Source:
    def acquire(self, subject):
        yield IntakePayload(
            payload=[
                {"date": "2026-01-01", "close": 100.0, "volume": 10.0},
                {"date": "2026-01-02", "close": 101.0, "volume": 12.0},
                {"date": "2026-01-03", "close": 103.0, "volume": 15.0},
            ],
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="synthetic-proof",
            coverage_start="2026-01-01",
            coverage_end="2026-01-03",
            row_count=3,
            schema=("date", "close", "volume"),
            provenance={"purpose": "test"},
            neutral_semantics="Observed price path and aggregate volume; no intent inferred.",
        )


class _FakeAIResearchDirector:
    def __init__(self):
        self.seen_result = None

    def begin_research(self, *, subject, evidence, **kwargs):
        return ResearchDecision(
            continue_research=True,
            next_request=AnalysisRequest(
                request_id="r:1",
                subject_id=subject.subject_id,
                question="Does close co-vary with volume in this exploratory evidence?",
                method_id="analysis.relationship.correlation",
                evidence_ids=(evidence[0].evidence_id,),
                parameters={"columns": ["close", "volume"], "correlation_type": "pearson"},
                research_phase=ResearchPhase.EXPLORATION,
                rationale="AI selected an exploratory relationship test.",
            ),
        )

    def repair_request(self, **kwargs):
        raise AssertionError("valid AI request should not require repair")

    def interpret_result(self, *, subject, result, **kwargs):
        self.seen_result = result
        return ResearchDecision(
            continue_research=False,
            promote_findings=(
                Finding(
                    finding_id="finding:correlation-proof",
                    subject_id=subject.subject_id,
                    statement="The synthetic proof produced a positive close-volume relationship.",
                    supporting_result_ids=(result.result_id,),
                    evidence_ids=result.evidence_ids,
                    metadata={
                        "significance": "AI judged the proof worth retaining for runtime verification.",
                        "status": "EXPLORATORY",
                    },
                ),
            ),
            close_reason="PROOF_COMPLETE",
        )


class V4StandardMethodsTests(unittest.TestCase):
    def test_catalog_requires_explicit_descriptive_columns(self):
        spec = standard_method_catalog().get("analysis.descriptive.statistics")
        columns = next(item for item in spec.parameters if item.name == "columns")
        self.assertTrue(columns.required)
        self.assertEqual(columns.minimum_length, 1)

    def test_correlation_contract_requires_exactly_two_columns(self):
        spec = standard_method_catalog().get("analysis.relationship.correlation")
        columns = next(item for item in spec.parameters if item.name == "columns")
        self.assertEqual(columns.exact_length, 2)

    def test_credential_free_end_to_end_runtime(self):
        rd = _FakeAIResearchDirector()
        with tempfile.TemporaryDirectory() as directory:
            runtime = build_runtime(rd=rd, nexus_path=f"{directory}/nexus.json")
            subject = SubjectMetadata(subject_id="AAPL", ticker="AAPL")
            intake = IntakeEngine(runtime.cache)
            evidence = intake.ingest(subject=subject, source=_Source())
            outcome = runtime.orchestrator.run(
                subject=subject,
                evidence=evidence,
                max_analyses=1,
            )

            self.assertTrue(outcome.closed)
            self.assertEqual(outcome.close_reason, "PROOF_COMPLETE")
            self.assertEqual(outcome.analyses_executed, 1)
            self.assertEqual(outcome.findings_promoted, 1)
            self.assertEqual(rd.seen_result.method_id, "analysis.relationship.correlation")
            self.assertGreater(rd.seen_result.outputs["correlation"], 0.9)
            self.assertEqual(len(runtime.nexus.findings_for_subject("AAPL")), 1)
            # Raw evidence remains in temporary cache, not Nexus.
            self.assertEqual(len(runtime.cache.active_keys()), 1)


if __name__ == "__main__":
    unittest.main()
