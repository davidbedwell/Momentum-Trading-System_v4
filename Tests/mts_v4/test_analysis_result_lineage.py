from __future__ import annotations

import unittest

from MTS_V4.analysis import ExactMethodAnalysisExecutor, RegisteredAnalysisMethod
from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.contracts import (
    AnalysisRequest,
    AnalysisResultInput,
    EvidenceDescriptor,
    ResearchDecision,
    ResearchPhase,
    SubjectMetadata,
)
from MTS_V4.nexus import InMemoryResearchNexus
from MTS_V4.orchestrator import ResearchLoopOrchestrator
from MTS_V4.scientific_toolkit import scientific_toolkit_analysis_method, scientific_toolkit_method_spec
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
        if len(self.results) == 1:
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
                            result_id=result.result_id,
                            output_path=("derived_datasets", "percent_change"),
                            input_name="daily_returns",
                        ),
                    ),
                    parameters={"columns": ["value"]},
                    research_phase=ResearchPhase.EXPLORATION,
                ),
            )
        if len(self.results) == 2:
            source_result_id = self.results[0].result_id
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
                            result_id=source_result_id,
                            output_path=("derived_datasets", "percent_change"),
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
                {"date": "2026-01-05", "close": 103.0, "volume": 50},
                {"date": "2026-01-06", "close": 115.0, "volume": 60},
                {"date": "2026-01-07", "close": 109.0, "volume": 70},
                {"date": "2026-01-08", "close": 121.0, "volume": 80},
                {"date": "2026-01-09", "close": 118.0, "volume": 90},
                {"date": "2026-01-10", "close": 130.0, "volume": 100},
            ],
        )
        catalog = standard_method_catalog()
        validator = ObjectiveContractValidator(catalog)
        executor = ExactMethodAnalysisExecutor()
        for method in standard_analysis_methods():
            executor.register(method)
        return cache, validator, executor, catalog

    def _evidence(self) -> EvidenceDescriptor:
        return EvidenceDescriptor(
            evidence_id="evidence:AAPL",
            subject_id="equity:AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture",
            coverage_start="2026-01-01",
            coverage_end="2026-01-10",
            row_count=10,
            schema=("date", "close", "volume"),
            cache_key="cache:AAPL",
        )

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
        outcome = orchestrator.run(
            subject=SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL"),
            evidence=(self._evidence(),),
            max_analyses=3,
        )

        self.assertTrue(outcome.closed)
        self.assertEqual(outcome.analyses_executed, 3)
        self.assertEqual(len(rd.results), 3)

        returns, described, rolling = rd.results
        self.assertEqual(returns.outputs["observation_count"], 9)
        catalog_entry = returns.outputs["derived_dataset_catalog"]["percent_change"]
        self.assertEqual(catalog_entry["output_path"], ["derived_datasets", "percent_change"])
        self.assertEqual(catalog_entry["schema"], ["index", "value"])
        self.assertAlmostEqual(
            returns.outputs["derived_datasets"]["percent_change"][0]["value"],
            0.10,
        )

        value_summary = described.outputs["columns"]["value"]
        self.assertEqual(value_summary["count"], 9)
        self.assertEqual(described.evidence_ids, ("evidence:AAPL",))
        self.assertEqual(
            described.execution_metadata["analysis_input_lineage"],
            [{
                "input_name": "daily_returns",
                "result_id": returns.result_id,
                "output_path": ["derived_datasets", "percent_change"],
            }],
        )

        self.assertEqual(len(rolling.outputs["observations"]), 8)
        self.assertEqual(rolling.evidence_ids, ("evidence:AAPL",))
        self.assertEqual(
            rolling.execution_metadata["analysis_input_lineage"][0]["result_id"],
            returns.result_id,
        )

    def test_forward_horizon_is_rd_parameter_and_terminal_rows_can_feed_scipy_skew(self):
        cache, _, executor, catalog = self._runtime_parts()
        catalog.register(scientific_toolkit_method_spec())
        executor.register(scientific_toolkit_analysis_method())
        validator = ObjectiveContractValidator(catalog)

        forward = AnalysisRequest(
            request_id="req:forward",
            subject_id="equity:AAPL",
            question="Measure the RD-selected five-row forward path.",
            method_id="analysis.path.forward_measurement",
            evidence_ids=("evidence:AAPL",),
            parameters={"price_column": "close", "horizon": 5, "direction": "LONG"},
            research_phase=ResearchPhase.EXPLORATION,
        )
        first = executor.execute(forward, {"evidence:AAPL": cache.get("cache:AAPL")})
        dataset = first.outputs["derived_datasets"]["forward_path_observations"]
        self.assertEqual(len(dataset), 5)
        self.assertEqual(first.outputs["horizon"], 5)
        self.assertEqual(
            first.outputs["derived_dataset_catalog"]["forward_path_observations"]["output_path"],
            ["derived_datasets", "forward_path_observations"],
        )

        skew = AnalysisRequest(
            request_id="req:skew",
            subject_id="equity:AAPL",
            question="Calculate skewness of the derived terminal return distribution.",
            method_id="analysis.toolkit.scientific_function",
            evidence_ids=(),
            analysis_inputs=(
                AnalysisResultInput(
                    result_id=first.result_id,
                    output_path=("derived_datasets", "forward_path_observations"),
                    input_name="forward_returns",
                ),
            ),
            parameters={
                "tool_id": "scipy.stats.skew",
                "args": [{"column": "terminal_directional_return"}],
            },
            research_phase=ResearchPhase.EXPLORATION,
        )
        defects = validator.validate(skew, {}, {first.result_id: first})
        self.assertEqual(defects, ())
        resolved = validator.resolve_analysis_input(skew.analysis_inputs[0], first)
        second = executor.execute(skew, {"forward_returns": resolved})
        self.assertNotIn("execution_error", second.outputs)
        self.assertEqual(second.outputs["tool_id"], "scipy.stats.skew")
        self.assertIn("result", second.outputs)

    def test_analysis_execution_error_is_returned_not_raised(self):
        executor = ExactMethodAnalysisExecutor()

        def fail(payloads, parameters):
            raise ValueError("fixture failure")

        executor.register(RegisteredAnalysisMethod("analysis.fixture.fail", fail))
        result = executor.execute(
            AnalysisRequest(
                request_id="req:fail",
                subject_id="equity:AAPL",
                question="Exercise objective execution failure.",
                method_id="analysis.fixture.fail",
                evidence_ids=("evidence:AAPL",),
                parameters={},
                research_phase=ResearchPhase.EXPLORATION,
            ),
            {"evidence:AAPL": [{"value": 1.0}]},
        )
        self.assertEqual(result.execution_metadata["execution_status"], "ERROR")
        self.assertIn("ValueError: fixture failure", result.outputs["execution_error"])
        self.assertEqual(
            result.outputs["interpretation_boundary"],
            "OBJECTIVE_EXECUTION_ERROR_RD_DECIDES_NEXT_STEP",
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
                    result_id="analysis-result:missing",
                    output_path=("derived_datasets", "percent_change"),
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
                    output_path=("outputs", "derived_datasets", "percent_change"),
                    input_name="derived",
                ),
            ),
            parameters={"columns": ["value"]},
            research_phase=ResearchPhase.EXPLORATION,
        )
        defects = validator.validate(request, {}, {source.result_id: source})
        self.assertEqual(len(defects), 1)
        self.assertEqual(defects[0].code, "MISSING_ANALYSIS_OUTPUT")
        self.assertIn("outputs", defects[0].message)


if __name__ == "__main__":
    unittest.main()
