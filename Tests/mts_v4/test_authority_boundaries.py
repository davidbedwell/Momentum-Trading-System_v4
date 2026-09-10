from __future__ import annotations

import unittest

from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.contracts import AnalysisRequest, EvidenceDescriptor, Finding, ResearchDecision, ResearchPhase, SubjectMetadata
from MTS_V4.method_catalog import MethodCatalog, MethodSpec, ParameterContract
from MTS_V4.nexus import InMemoryResearchNexus
from MTS_V4.orchestrator import ResearchLoopOrchestrator
from MTS_V4.validation import ObjectiveContractValidator


class _FakeAnalysis:
    def __init__(self):
        self.requests = []

    def execute(self, request, evidence_payloads):
        from MTS_V4.contracts import AnalysisResult
        self.requests.append(request)
        return AnalysisResult(
            result_id="result:1",
            request_id=request.request_id,
            subject_id=request.subject_id,
            method_id=request.method_id,
            outputs={"correlation": 0.5},
            evidence_ids=request.evidence_ids,
        )


class _FakeRD:
    def __init__(self):
        self.repairs = []
        self.available_methods_seen = None

    def begin_research(self, *, available_methods, **kwargs):
        self.available_methods_seen = tuple(available_methods)
        return ResearchDecision(
            continue_research=True,
            next_request=AnalysisRequest(
                request_id="request:bad",
                subject_id="AAPL",
                question="Does price co-vary with volume?",
                method_id="relationship.correlation",
                evidence_ids=("ev:1",),
                parameters={"columns": ["close", "volume", "date"]},
                research_phase=ResearchPhase.EXPLORATION,
            ),
        )

    def repair_request(self, *, defects, **kwargs):
        self.repairs.append(tuple(defects))
        return ResearchDecision(
            continue_research=True,
            next_request=AnalysisRequest(
                request_id="request:repaired",
                subject_id="AAPL",
                question="Does price co-vary with volume?",
                method_id="relationship.correlation",
                evidence_ids=("ev:1",),
                parameters={"columns": ["close", "volume"]},
                research_phase=ResearchPhase.EXPLORATION,
            ),
        )

    def interpret_result(self, *, result, **kwargs):
        return ResearchDecision(
            continue_research=False,
            promote_findings=(
                Finding(
                    finding_id="finding:1",
                    subject_id="AAPL",
                    statement="Exploratory relationship result retained for future research.",
                    supporting_result_ids=(result.result_id,),
                    evidence_ids=result.evidence_ids,
                    metadata={
                        "significance": "RD judged this result materially informative.",
                        "status": "EXPLORATORY",
                        "novel_unanticipated_label": {
                            "name": "volume-path asymmetry candidate",
                            "confidence": "provisional",
                        },
                    },
                ),
            ),
            close_reason="RD_CLOSED",
        )


class V4AuthorityBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.catalog = MethodCatalog(
            [
                MethodSpec(
                    method_id="relationship.correlation",
                    artifact_types=("NORMALIZED_DATASET",),
                    description="Measure a pairwise relationship without inferring causation.",
                    parameters=(
                        ParameterContract(
                            name="columns",
                            required=True,
                            python_types=(list, tuple),
                            exact_length=2,
                            meaning="exactly two RD-selected relationship columns",
                        ),
                    ),
                )
            ]
        )
        self.validator = ObjectiveContractValidator(self.catalog)
        self.evidence = EvidenceDescriptor(
            evidence_id="ev:1",
            subject_id="AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="test-source",
            coverage_start="2020-01-01",
            coverage_end="2025-12-31",
            row_count=1000,
            schema=("date", "close", "volume"),
            cache_key="cache:aapl",
        )

    def test_cardinality_defect_is_precise_and_does_not_choose_replacement(self):
        request = AnalysisRequest(
            request_id="r1",
            subject_id="AAPL",
            question="AI-authored question",
            method_id="relationship.correlation",
            evidence_ids=("ev:1",),
            parameters={"columns": ["close", "volume", "date"]},
            research_phase=ResearchPhase.EXPLORATION,
        )
        defects = self.validator.validate(request, {"ev:1": self.evidence})
        self.assertEqual(len(defects), 1)
        self.assertEqual(defects[0].code, "INVALID_PARAMETER_CARDINALITY")
        self.assertIn("requires exactly 2 values; received 3", defects[0].message)
        self.assertEqual(request.method_id, "relationship.correlation")
        self.assertEqual(request.parameters["columns"], ["close", "volume", "date"])

    def test_analysis_result_in_evidence_ids_gets_namespace_repair_guidance_without_rewrite(self):
        result_id = "analysis-result:b3e00c2213304ffb8c69d2a735c51daf"
        request = AnalysisRequest(
            request_id="r:analysis-result-as-evidence",
            subject_id="AAPL",
            question="Characterize the derived forward path metrics.",
            method_id="relationship.correlation",
            evidence_ids=(result_id,),
            analysis_inputs=(),
            parameters={"columns": ["close", "volume"]},
            research_phase=ResearchPhase.EXPLORATION,
        )

        defects = self.validator.validate(request, {"ev:1": self.evidence})

        self.assertEqual(len(defects), 1)
        self.assertEqual(defects[0].code, "MISSING_EVIDENCE")
        self.assertEqual(defects[0].field, "evidence_ids")
        self.assertIn("analysis-result IDs are not evidence_ids", defects[0].message)
        self.assertIn("analysis_inputs", defects[0].message)
        self.assertIn("exact result_id", defects[0].message)
        self.assertIn("exact output_path", defects[0].message)
        self.assertEqual(request.evidence_ids, (result_id,))
        self.assertEqual(request.analysis_inputs, ())

    def test_failed_analysis_result_path_gets_explicit_repair_guidance_without_rewrite(self):
        from MTS_V4.contracts import AnalysisResult, AnalysisResultInput

        result_id = "analysis-result:389afccd7a7345bc955962ac9d85448d"
        bad_path = ("evidence", "equity:AAPL:d55932ce14a78f85aa33b1ec")
        result = AnalysisResult(
            result_id=result_id,
            request_id="req:derive_volume_dataset_v7",
            subject_id="AAPL",
            method_id="analysis.dataset.compose",
            outputs={"error": "compose execution failed"},
            evidence_ids=("ev:1",),
            execution_metadata={"execution_status": "ERROR"},
        )
        analysis_input = AnalysisResultInput(
            result_id=result_id,
            output_path=bad_path,
            input_name="ohlcv_input_1",
        )
        request = AnalysisRequest(
            request_id="r:failed-result-input",
            subject_id="AAPL",
            question="Compose a volume dataset.",
            method_id="relationship.correlation",
            evidence_ids=("ev:1",),
            analysis_inputs=(analysis_input,),
            parameters={"columns": ["close", "volume"]},
            research_phase=ResearchPhase.EXPLORATION,
        )

        defects = self.validator.validate(
            request,
            {"ev:1": self.evidence},
            analysis_results={result_id: result},
        )

        self.assertEqual(len(defects), 1)
        self.assertEqual(defects[0].code, "MISSING_ANALYSIS_OUTPUT")
        self.assertEqual(defects[0].field, "analysis_inputs")
        self.assertIn("execution_status=ERROR", defects[0].message)
        self.assertIn("cannot supply that analysis input", defects[0].message)
        self.assertIn("exact advertised derived_dataset_catalog output_path", defects[0].message)
        self.assertIn("Deterministic code will not choose among those options", defects[0].message)
        self.assertEqual(request.analysis_inputs, (analysis_input,))
        self.assertEqual(request.analysis_inputs[0].output_path, bad_path)

    def test_unknown_method_is_missing_capability_not_substitution(self):
        request = AnalysisRequest(
            request_id="r2",
            subject_id="AAPL",
            question="AI-authored question",
            method_id="does.not.exist",
            evidence_ids=("ev:1",),
            parameters={},
            research_phase=ResearchPhase.EXPLORATION,
        )
        defects = self.validator.validate(request, {"ev:1": self.evidence})
        self.assertEqual(defects[0].code, "MISSING_CAPABILITY")
        self.assertEqual(defects[0].method_id, "does.not.exist")

    def test_nexus_has_no_raw_dataset_publication_api(self):
        nexus = InMemoryResearchNexus()
        self.assertFalse(hasattr(nexus, "publish_dataset"))
        self.assertFalse(hasattr(nexus, "put_raw_data"))
        self.assertFalse(hasattr(nexus, "publish_artifact"))

    def test_invalid_contract_returns_to_rd_for_scientific_repair(self):
        rd = _FakeRD()
        analysis = _FakeAnalysis()
        nexus = InMemoryResearchNexus()
        cache = TemporaryResearchCache()
        cache.put("cache:aapl", [{"close": 1.0, "volume": 10}])
        orchestrator = ResearchLoopOrchestrator(
            mission="discover reproducible exploitable market conditions",
            rd=rd,
            validator=self.validator,
            analysis=analysis,
            nexus=nexus,
            cache=cache,
            available_methods=self.catalog.capability_payloads(),
        )
        outcome = orchestrator.run(
            subject=SubjectMetadata(subject_id="AAPL", ticker="AAPL"),
            evidence=(self.evidence,),
            max_analyses=2,
        )
        self.assertEqual(len(rd.repairs), 1)
        self.assertEqual(rd.repairs[0][0].code, "INVALID_PARAMETER_CARDINALITY")
        self.assertEqual(len(analysis.requests), 1)
        self.assertEqual(analysis.requests[0].request_id, "request:repaired")
        self.assertEqual(outcome.findings_promoted, 1)
        finding = nexus.findings_for_subject("AAPL")[0]
        self.assertEqual(finding.metadata["novel_unanticipated_label"]["confidence"], "provisional")
        self.assertEqual(rd.available_methods_seen[0]["method_id"], "relationship.correlation")
        self.assertNotIn("score", rd.available_methods_seen[0])
        self.assertNotIn("rank", rd.available_methods_seen[0])


if __name__ == "__main__":
    unittest.main()
