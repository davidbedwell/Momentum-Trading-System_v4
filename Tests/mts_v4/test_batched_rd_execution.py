from __future__ import annotations

import unittest

from MTS_V4.batch_compiler import (
    BatchCompilerContext,
    ScientificSpecificationCompiler,
    topological_analysis_order,
)
from MTS_V4.batch_contracts import (
    BatchResearchDecision,
    ResearchPackagePlan,
    ScientificAnalysisSpecification,
    ScientificInputReference,
)
from MTS_V4.batch_orchestrator import BatchResearchLoopOrchestrator
from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.contracts import AnalysisResult, EvidenceDescriptor, ResearchPhase, SubjectMetadata
from MTS_V4.method_catalog import MethodCatalog, MethodSpec
from MTS_V4.nexus import InMemoryResearchNexus
from MTS_V4.validation import ObjectiveContractValidator


class _FakeBatchAnalysis:
    def __init__(self):
        self.requests = []

    def execute(self, request, evidence_payloads):
        self.requests.append(request)
        outputs = {"value": len(self.requests)}
        if request.method_id == "derive":
            outputs = {
                "derived_dataset_catalog": {
                    "derived": {
                        "row_count": 2,
                        "schema": ["x"],
                        "output_path": ["derived_datasets", "derived"],
                        "temporary": True,
                    }
                },
                "derived_datasets": {"derived": [{"x": 1.0}, {"x": 2.0}]},
            }
        return AnalysisResult(
            result_id=f"result:{len(self.requests)}",
            request_id=request.request_id,
            subject_id=request.subject_id,
            method_id=request.method_id,
            outputs=outputs,
            evidence_ids=request.evidence_ids,
            execution_metadata={"execution_status": "SUCCESS"},
        )


class _FakeBatchRD:
    def __init__(self, first_decision):
        self.first_decision = first_decision
        self.interpret_calls = 0
        self.report_sizes = []

    def begin_batch_research(self, **kwargs):
        return self.first_decision

    def interpret_batch_results(self, *, report, **kwargs):
        self.interpret_calls += 1
        self.report_sizes.append(len(report.records))
        return BatchResearchDecision(
            continue_research=False,
            close_reason="BATCH_REVIEW_COMPLETE",
            batch_interpretation="Reviewed all completed branches together.",
        )


class _TwoBatchRD:
    def __init__(self, first_decision, second_decision):
        self.first_decision = first_decision
        self.second_decision = second_decision
        self.interpret_calls = 0
        self.reports = []

    def begin_batch_research(self, **kwargs):
        return self.first_decision

    def interpret_batch_results(self, *, report, **kwargs):
        self.interpret_calls += 1
        self.reports.append(report)
        if self.interpret_calls == 1:
            return self.second_decision
        return BatchResearchDecision(
            continue_research=False,
            close_reason="FOLLOW_UP_COMPLETE",
            batch_interpretation="Reviewed the follow-up batch.",
        )


class BatchedRDExecutionTests(unittest.TestCase):
    def setUp(self):
        self.subject = SubjectMetadata(subject_id="equity:AMD", ticker="AMD")
        self.evidence = EvidenceDescriptor(
            evidence_id="ev:amd",
            subject_id=self.subject.subject_id,
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="test",
            coverage_start="2020-01-01",
            coverage_end="2025-01-01",
            row_count=2,
            schema=("x",),
            cache_key="cache:amd",
        )

    def _spec(
        self,
        analysis_id,
        rp_id,
        method_id,
        inputs,
        *,
        parameters=None,
        question_id=None,
    ):
        return ScientificAnalysisSpecification(
            analysis_id=analysis_id,
            rp_id=rp_id,
            question_id=question_id or f"q:{analysis_id}",
            subject_id=self.subject.subject_id,
            question=f"Question for {analysis_id}",
            method_id=method_id,
            inputs=tuple(inputs),
            parameters={} if parameters is None else parameters,
            research_phase=ResearchPhase.EXPLORATION,
            rationale="AI-authored rationale",
        )

    def _runtime_parts(self):
        analysis = _FakeBatchAnalysis()
        catalog = MethodCatalog(
            [
                MethodSpec("derive", ("NORMALIZED_DATASET",)),
                MethodSpec("test", ("NORMALIZED_DATASET",)),
            ]
        )
        cache = TemporaryResearchCache()
        cache.put(self.evidence.cache_key, [{"x": 1.0}, {"x": 2.0}])
        return analysis, catalog, cache

    def _orchestrator(self, rd, analysis, catalog, cache):
        return BatchResearchLoopOrchestrator(
            mission="test mission",
            rd=rd,
            validator=ObjectiveContractValidator(catalog),
            analysis=analysis,
            nexus=InMemoryResearchNexus(),
            cache=cache,
            available_methods=catalog.capability_payloads(),
        )

    def test_compiler_resolves_logical_dependency_without_ai_result_id_or_output_path(self):
        prior = AnalysisResult(
            result_id="generated-runtime-result",
            request_id="generated-runtime-request",
            subject_id=self.subject.subject_id,
            method_id="derive",
            outputs={
                "derived_dataset_catalog": {
                    "only_dataset": {
                        "output_path": ["derived_datasets", "only_dataset"],
                    }
                },
                "derived_datasets": {"only_dataset": [{"x": 1.0}]},
            },
            evidence_ids=(self.evidence.evidence_id,),
            execution_metadata={"execution_status": "SUCCESS"},
        )
        spec = self._spec(
            "analysis:b",
            "rp:1",
            "compose-like",
            [ScientificInputReference(role="predictor", analysis_id="analysis:a")],
            parameters={
                "alignment": [
                    {"input_name": "predictor", "key": {"mode": "ROW_POSITION"}},
                ]
            },
        )

        compiled = ScientificSpecificationCompiler().compile(
            spec,
            context=BatchCompilerContext(
                evidence={self.evidence.evidence_id: self.evidence},
                results_by_analysis_id={"analysis:a": prior},
            ),
        )

        self.assertEqual(len(compiled.request.analysis_inputs), 1)
        self.assertEqual(compiled.request.analysis_inputs[0].result_id, "generated-runtime-result")
        self.assertEqual(
            compiled.request.analysis_inputs[0].output_path,
            ("derived_datasets", "only_dataset"),
        )
        runtime_alias = compiled.request.analysis_inputs[0].input_name
        self.assertNotEqual(runtime_alias, "predictor")
        self.assertEqual(
            compiled.request.parameters["alignment"][0]["input_name"],
            runtime_alias,
        )
        self.assertTrue(compiled.mechanical_repairs)

    def test_compiler_rejects_reusing_completed_logical_analysis_id(self):
        prior = AnalysisResult(
            result_id="result:old",
            request_id="request:old",
            subject_id=self.subject.subject_id,
            method_id="derive",
            outputs={},
            evidence_ids=(self.evidence.evidence_id,),
            execution_metadata={"execution_status": "SUCCESS"},
        )
        spec = self._spec(
            "analysis:a",
            "rp:1",
            "test",
            [ScientificInputReference(role="raw", evidence_id=self.evidence.evidence_id)],
        )
        with self.assertRaisesRegex(Exception, "already completed"):
            ScientificSpecificationCompiler().compile(
                spec,
                context=BatchCompilerContext(
                    evidence={self.evidence.evidence_id: self.evidence},
                    results_by_analysis_id={"analysis:a": prior},
                ),
            )

    def test_topological_order_preserves_ai_dependencies_without_inventing_edges(self):
        first = self._spec(
            "a",
            "rp:1",
            "derive",
            [ScientificInputReference(role="raw", evidence_id=self.evidence.evidence_id)],
        )
        second = self._spec(
            "b",
            "rp:1",
            "test",
            [ScientificInputReference(role="derived", analysis_id="a")],
        )
        independent = self._spec(
            "c",
            "rp:2",
            "test",
            [ScientificInputReference(role="raw", evidence_id=self.evidence.evidence_id)],
        )

        ordered = topological_analysis_order((second, independent, first))
        ids = [item.analysis_id for item in ordered]
        self.assertLess(ids.index("a"), ids.index("b"))
        self.assertIn("c", ids)

    def test_orchestrator_executes_multiple_rps_before_one_batch_interpretation(self):
        a = self._spec(
            "a",
            "rp:trend",
            "derive",
            [ScientificInputReference(role="raw", evidence_id=self.evidence.evidence_id)],
        )
        b = self._spec(
            "b",
            "rp:trend",
            "test",
            [ScientificInputReference(role="derived", analysis_id="a")],
        )
        c = self._spec(
            "c",
            "rp:gap",
            "test",
            [ScientificInputReference(role="raw", evidence_id=self.evidence.evidence_id)],
        )
        decision = BatchResearchDecision(
            continue_research=True,
            research_packages=(
                ResearchPackagePlan(
                    rp_id="rp:trend",
                    objective="Test trend continuation.",
                    analyses=(a, b),
                    decision_boundary="Return trend family before contingent extensions.",
                ),
                ResearchPackagePlan(
                    rp_id="rp:gap",
                    objective="Test gap behavior.",
                    analyses=(c,),
                ),
            ),
        )
        rd = _FakeBatchRD(decision)
        analysis, catalog, cache = self._runtime_parts()
        orchestrator = self._orchestrator(rd, analysis, catalog, cache)

        outcome = orchestrator.run(
            subject=self.subject,
            evidence=(self.evidence,),
        )

        self.assertEqual(outcome.decisions, 2)
        self.assertEqual(outcome.batches_executed, 1)
        self.assertEqual(outcome.analyses_executed, 3)
        self.assertEqual(len(analysis.requests), 3)
        self.assertEqual(rd.interpret_calls, 1)
        self.assertEqual(rd.report_sizes, [3])
        self.assertTrue(outcome.closed)
        self.assertEqual(outcome.close_reason, "BATCH_REVIEW_COMPLETE")

    def test_follow_up_batch_can_reference_prior_logical_analysis_id(self):
        a = self._spec(
            "a",
            "rp:trend",
            "derive",
            [ScientificInputReference(role="raw", evidence_id=self.evidence.evidence_id)],
        )
        first = BatchResearchDecision(
            continue_research=True,
            research_packages=(
                ResearchPackagePlan(
                    rp_id="rp:trend",
                    objective="Create the scientifically selected predictor.",
                    analyses=(a,),
                    decision_boundary="Review predictor before follow-up.",
                ),
            ),
        )
        b = self._spec(
            "b",
            "rp:trend",
            "test",
            [ScientificInputReference(role="predictor", analysis_id="a")],
        )
        second = BatchResearchDecision(
            continue_research=True,
            research_packages=(
                ResearchPackagePlan(
                    rp_id="rp:trend",
                    objective="Follow up the completed predictor result.",
                    analyses=(b,),
                ),
            ),
        )
        rd = _TwoBatchRD(first, second)
        analysis, catalog, cache = self._runtime_parts()
        orchestrator = self._orchestrator(rd, analysis, catalog, cache)

        outcome = orchestrator.run(
            subject=self.subject,
            evidence=(self.evidence,),
        )

        self.assertEqual(outcome.decisions, 3)
        self.assertEqual(outcome.batches_executed, 2)
        self.assertEqual(outcome.analyses_executed, 2)
        self.assertEqual(rd.interpret_calls, 2)
        self.assertEqual(len(analysis.requests), 2)
        follow_up = analysis.requests[1]
        self.assertEqual(len(follow_up.analysis_inputs), 1)
        self.assertEqual(follow_up.analysis_inputs[0].result_id, "result:1")
        self.assertEqual(
            follow_up.analysis_inputs[0].output_path,
            ("derived_datasets", "derived"),
        )
        self.assertEqual(outcome.close_reason, "FOLLOW_UP_COMPLETE")

    def test_failed_branch_does_not_stop_independent_batch_branch(self):
        broken = self._spec(
            "broken",
            "rp:broken",
            "test",
            [ScientificInputReference(role="missing", evidence_id="ev:missing")],
        )
        healthy = self._spec(
            "healthy",
            "rp:healthy",
            "test",
            [ScientificInputReference(role="raw", evidence_id=self.evidence.evidence_id)],
        )
        decision = BatchResearchDecision(
            continue_research=True,
            research_packages=(
                ResearchPackagePlan(
                    rp_id="rp:broken",
                    objective="Intentionally unavailable branch.",
                    analyses=(broken,),
                ),
                ResearchPackagePlan(
                    rp_id="rp:healthy",
                    objective="Independent executable branch.",
                    analyses=(healthy,),
                ),
            ),
        )
        rd = _FakeBatchRD(decision)
        analysis, catalog, cache = self._runtime_parts()
        orchestrator = self._orchestrator(rd, analysis, catalog, cache)

        outcome = orchestrator.run(
            subject=self.subject,
            evidence=(self.evidence,),
        )

        self.assertEqual(outcome.analyses_executed, 1)
        self.assertEqual(len(analysis.requests), 1)
        self.assertEqual(rd.interpret_calls, 1)
        report = outcome.last_report
        self.assertIsNotNone(report)
        statuses = {record.analysis_id: record.status for record in report.records}
        self.assertEqual(statuses["healthy"], "SUCCESS")
        self.assertEqual(statuses["broken"], "AMBIGUOUS_SCIENTIFIC_REPAIR_REQUIRED")


if __name__ == "__main__":
    unittest.main()
