from __future__ import annotations

import unittest

from MTS_V4.analysis import ExactMethodAnalysisExecutor
from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.contracts import (
    AnalysisRequest,
    AnalysisResultInput,
    EvidenceDescriptor,
    ResearchDecision,
    ResearchPhase,
    SubjectMetadata,
)
from MTS_V4.method_catalog import MethodCatalog
from MTS_V4.nexus import InMemoryResearchNexus
from MTS_V4.orchestrator import ResearchLoopOrchestrator
from MTS_V4.standard_methods import standard_analysis_methods, standard_method_catalog
from MTS_V4.validation import ObjectiveContractValidator


class _ChainingRD:
    def __init__(self) -> None:
        self.results = []
        self.repairs = []

    @staticmethod
    def _returns_request() -> AnalysisRequest:
        return AnalysisRequest(
            request_id="req:returns",
            subject_id="equity:AAPL",
            question="Compute daily percent changes.",
            method_id="analysis.transform.percent_change",
            evidence_ids=("evidence:AAPL",),
            parameters={"column": "close", "lag": 1},
            research_phase=ResearchPhase.EXPLORATION,
        )

    def begin_research(self, **kwargs):
        return ResearchDecision(continue_research=True, next_request=self._returns_request())

    def resume_research(self, **kwargs):
        raise AssertionError("resume not expected")

    def repair_request(self, **kwargs):
        self.repairs.append(tuple(kwargs["defects"]))
        return ResearchDecision(continue_research=False, close_reason="OBJECTIVE_DEFECT_OBSERVED")

    def interpret_result(self, **kwargs):
        result = kwargs["result"]
        self.results.append(result)
        if result.result_id == "analysis-result:1":
            return ResearchDecision(
                continue_research=True,
                next_request=AnalysisRequest(
                    request_id="req:describe-returns",
                    subject_id="equity:AAPL",
                    question="Describe the daily percent-change distribution.",
                    method_id="analysis.descriptive.statistics",
                    evidence_ids=(),
                    analysis_inputs=(
                        AnalysisResultInput(
                            result_id="analysis-result:1",
                            output_path=("observations",),
                            input_name="daily_returns",
                        ),
                    ),
                    parameters={"columns": ["value"]},
                    research_phase=ResearchPhase.EXPLORATION,
                ),
            )
        if result.result_id == "analysis-result:2":
            return ResearchDecision(
                continue_research=True,
                next_request=AnalysisRequest(
                    request_id="req:rolling-returns",
                    subject_id="equity:AAPL",
                    question="Measure rolling volatility of daily percent changes.",
                    method_id="analysis.rolling.statistics",
                    evidence_ids=(),
                    analysis_inputs=(
                        AnalysisResultInput(
                            result_id="analysis-result:1",
                            output_path=("observations",),
                            input_name="daily_returns",
                        ),
                    ),
                    parameters={"column": "value", "window": 2, "statistic": "stddev_sample"},
                    research_phase=ResearchPhase.EXPLORATION,
                ),
            )
        return ResearchDecision(continue_research=False, close_reason="CHAIN_COMPLETE")


class AnalysisResultLineageTests(unittest.TestCase):
    def _runtime_parts(self):
        cache = TemporaryResearchCache()
        cache.put(
            "cache:AAPL",
            [
                {"date": "2026-01-01", "close": 100.0, "volume": 10},
                {"date": "2026-01-02", "close": 110.0, "volume": 20},
                {"date": "2026-01-03", "close": 99.0, "volume": 30},
                {"date": "2026-01-04", "close": 108.9, "volume": 40},
            ],
        )
        catalog = standard_method_catalog()
        validator = ObjectiveContractValidator(catalog)
        executor = ExactMethodAnalysisExecutor()
        for method in standard_analysis_methods():
            executor.register(method)
        return cache, validator, executor, catalog

    def test_prior_result_rows_feed_later_methods_and_preserve_evidence_lineage(self):
        cache, validator, executor, catalog = self._runtime_parts()
        rd = _ChainingRD()
        orchestrator = ResearchLoopOrchestrator(
            mission="test",
            rd=rd,
            validator=validator,
            analysis=executor,
            nexus=InMemoryResearchNexus(),
            cache=cache,
            available_methods=catalog.capability_payloads(),
        )
        evidence = EvidenceDescriptor(
            evidence_id="evidence:AAPL",
            subject_id="equity:AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture",
            coverage_start="2026-01-01",
            coverage_end="2026-01-04",
            row_count=4,
            schema=("date", "close", "volume"),
            cache_key="cache:AAPL",
        )
        outcome = orchestrator.run(
            subject=SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL"),
            evidence=(evidence,),
            max_analyses=3,
        )

        self.assertTrue(outcome.closed)
        self.assertEqual(outcome.analyses_executed, 3)
        self.assertEqual(len(rd.results), 3)

        returns, described, rolling = rd.results
        self.assertEqual(returns.outputs["observation_count"], 3)
        self.assertAlmostEqual(returns.outputs["observations"][0]["value"], 0.10)

        value_summary = described.outputs["columns"]["value"]
        self.assertEqual(value_summary["count"], 3)
        self.assertAlmostEqual(value_summary["mean"], (0.10 - 0.10 + 0.10) / 3.0)
        self.assertEqual(described.evidence_ids, ("evidence:AAPL",))
        self.assertEqual(
            described.execution_metadata["analysis_input_lineage"],
            [{"input_name": "daily_returns", "result_id": "analysis-result:1", "output_path": ["observations"]}],
        )

        self.assertEqual(len(rolling.outputs["observations"]), 2)
        self.assertEqual(rolling.evidence_ids, ("evidence:AAPL",))
        self.assertEqual(
            rolling.execution_metadata["analysis_input_lineage"][0]["result_id"],
            "analysis-result:1",
        )

    def test_missing_prior_result_is_objective_defect_not_raw_evidence_fallback(self):
        _, validator, _, _ = self._runtime_parts()
        request = AnalysisRequest(
            request_id="req:missing",
            subject_id="equity:AAPL",
            question="Describe prior derived returns.",
            method_id="analysis.descriptive.statistics",
            evidence_ids=(),
            analysis_inputs=(
                AnalysisResultInput(
                    result_id="analysis-result:99",
                    output_path=("observations",),
                    input_name="returns",
                ),
            ),
            parameters={"columns": ["value"]},
            research_phase=ResearchPhase.EXPLORATION,
        )
        defects = validator.validate(request, {}, {})
        self.assertEqual(len(defects), 1)
        self.assertEqual(defects[0].code, "MISSING_ANALYSIS_RESULT")
        self.assertIn("regenerate", defects[0].message.lower())

    def test_invalid_output_path_is_rejected_exactly(self):
        cache, validator, executor, _ = self._runtime_parts()
        first = _ChainingRD._returns_request()
        source = executor.execute(first, {"evidence:AAPL": cache.get("cache:AAPL")})
        request = AnalysisRequest(
            request_id="req:bad-path",
            subject_id="equity:AAPL",
            question="Use a nonexistent derived output.",
            method_id="analysis.descriptive.statistics",
            evidence_ids=(),
            analysis_inputs=(
                AnalysisResultInput(
                    result_id=source.result_id,
                    output_path=("not_there",),
                    input_name="derived",
                ),
            ),
            parameters={"columns": ["value"]},
            research_phase=ResearchPhase.EXPLORATION,
        )
        defects = validator.validate(request, {}, {source.result_id: source})
        self.assertEqual(len(defects), 1)
        self.assertEqual(defects[0].code, "MISSING_ANALYSIS_OUTPUT")


if __name__ == "__main__":
    unittest.main()
