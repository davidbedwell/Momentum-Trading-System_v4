from __future__ import annotations

import unittest

from MTS_V4.analysis import ExactMethodAnalysisExecutor
from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.contracts import AnalysisRequest, AnalysisResultInput, EvidenceDescriptor, ResearchDecision, ResearchPhase, SubjectMetadata
from MTS_V4.nexus import InMemoryResearchNexus
from MTS_V4.orchestrator import ResearchLoopOrchestrator
from MTS_V4.standard_methods import standard_analysis_methods, standard_method_catalog
from MTS_V4.validation import ObjectiveContractValidator


class _ComposeRD:
    def __init__(self) -> None:
        self.results = []

    def begin_research(self, **kwargs):
        return ResearchDecision(
            continue_research=True,
            next_request=AnalysisRequest(
                request_id="req:forward",
                subject_id="equity:AAPL",
                question="Measure an RD-selected forward path.",
                method_id="analysis.path.forward_measurement",
                evidence_ids=("evidence:AAPL",),
                analysis_inputs=(),
                parameters={"price_column": "close", "horizon": 2, "direction": "LONG"},
                research_phase=ResearchPhase.EXPLORATION,
            ),
        )

    def resume_research(self, **kwargs):
        raise AssertionError("resume not expected")

    def repair_request(self, **kwargs):
        raise AssertionError(f"unexpected contract repair: {kwargs['defects']}")

    def interpret_result(self, **kwargs):
        result = kwargs["result"]
        self.results.append(result)
        if len(self.results) == 1:
            return ResearchDecision(
                continue_research=True,
                next_request=AnalysisRequest(
                    request_id="req:compose",
                    subject_id="equity:AAPL",
                    question="Align the derived terminal return with raw volume by source-row lineage.",
                    method_id="analysis.dataset.compose",
                    evidence_ids=("evidence:AAPL",),
                    analysis_inputs=(
                        AnalysisResultInput(
                            result_id=result.result_id,
                            output_path=("derived_datasets", "forward_path_observations"),
                            input_name="forward_rows",
                        ),
                    ),
                    parameters={
                        "alignment": [
                            {"input_name": "evidence:AAPL", "key": {"mode": "ROW_POSITION"}},
                            {"input_name": "forward_rows", "key": {"mode": "COLUMN", "column": "index"}},
                        ],
                        "selections": [
                            {"input_name": "forward_rows", "column": "terminal_directional_return", "output_name": "terminal_directional_return"},
                            {"input_name": "evidence:AAPL", "column": "volume", "output_name": "volume"},
                        ],
                        "join_type": "INNER",
                    },
                    research_phase=ResearchPhase.EXPLORATION,
                ),
            )
        if len(self.results) == 2:
            return ResearchDecision(
                continue_research=True,
                next_request=AnalysisRequest(
                    request_id="req:corr",
                    subject_id="equity:AAPL",
                    question="Measure the RD-selected relationship on the composed dataset.",
                    method_id="analysis.relationship.correlation",
                    evidence_ids=(),
                    analysis_inputs=(
                        AnalysisResultInput(
                            result_id=result.result_id,
                            output_path=("derived_datasets", "composed_dataset"),
                            input_name="composed",
                        ),
                    ),
                    parameters={"columns": ["terminal_directional_return", "volume"], "correlation_type": "pearson"},
                    research_phase=ResearchPhase.EXPLORATION,
                ),
            )
        return ResearchDecision(continue_research=False, close_reason="COMPOSITION_CHAIN_COMPLETE")


class DatasetCompositionTests(unittest.TestCase):
    @staticmethod
    def _evidence() -> EvidenceDescriptor:
        return EvidenceDescriptor(
            evidence_id="evidence:AAPL",
            subject_id="equity:AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture",
            coverage_start="2026-01-01",
            coverage_end="2026-01-06",
            row_count=6,
            schema=("date", "close", "volume"),
            cache_key="cache:AAPL",
        )

    def test_raw_row_position_and_derived_index_compose_then_feed_correlation(self):
        cache = TemporaryResearchCache()
        cache.put(
            "cache:AAPL",
            [
                {"date": "2026-01-01", "close": 100.0, "volume": 10.0},
                {"date": "2026-01-02", "close": 101.0, "volume": 20.0},
                {"date": "2026-01-03", "close": 103.0, "volume": 30.0},
                {"date": "2026-01-04", "close": 102.0, "volume": 40.0},
                {"date": "2026-01-05", "close": 106.0, "volume": 50.0},
                {"date": "2026-01-06", "close": 109.0, "volume": 60.0},
            ],
        )
        catalog = standard_method_catalog()
        executor = ExactMethodAnalysisExecutor()
        for method in standard_analysis_methods():
            executor.register(method)
        rd = _ComposeRD()
        outcome = ResearchLoopOrchestrator(
            mission="test",
            rd=rd,
            validator=ObjectiveContractValidator(catalog),
            analysis=executor,
            nexus=InMemoryResearchNexus(),
            cache=cache,
            available_methods=catalog.capability_payloads(),
        ).run(
            subject=SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL"),
            evidence=(self._evidence(),),
            max_analyses=3,
        )

        self.assertTrue(outcome.closed)
        self.assertEqual(outcome.analyses_executed, 3)
        forward, composed, correlation = rd.results
        rows = composed.outputs["derived_datasets"]["composed_dataset"]
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["alignment_key"], 0)
        self.assertEqual(rows[0]["volume"], 10.0)
        self.assertAlmostEqual(rows[0]["terminal_directional_return"], 0.03)
        self.assertEqual(
            composed.outputs["derived_dataset_catalog"]["composed_dataset"]["schema"],
            ["alignment_key", "terminal_directional_return", "volume"],
        )
        self.assertEqual(composed.evidence_ids, ("evidence:AAPL",))
        self.assertEqual(
            composed.execution_metadata["analysis_input_lineage"],
            [{
                "input_name": "forward_rows",
                "result_id": forward.result_id,
                "output_path": ["derived_datasets", "forward_path_observations"],
            }],
        )
        self.assertEqual(correlation.outputs["n"], 4)
        self.assertIsNotNone(correlation.outputs["correlation"])
        self.assertEqual(correlation.evidence_ids, ("evidence:AAPL",))
        self.assertEqual(
            correlation.execution_metadata["analysis_input_lineage"][0]["result_id"],
            composed.result_id,
        )

    def test_composition_contract_is_neutral_and_explicit(self):
        payload = standard_method_catalog().get("analysis.dataset.compose").capability_payload()
        self.assertIn("RD-selected", payload["description"])
        parameter_names = [item["name"] for item in payload["parameters"]]
        self.assertEqual(parameter_names, ["alignment", "selections", "join_type"])
        self.assertEqual(payload["parameters"][2]["allowed_values"], ["INNER"])
        self.assertEqual(payload["metadata"]["scientific_selection"], "none")
        self.assertFalse("volume" in payload["description"].lower())
        self.assertFalse("terminal_directional_return" in payload["description"].lower())

    def test_composition_does_not_infer_missing_selected_column(self):
        executor = ExactMethodAnalysisExecutor()
        for method in standard_analysis_methods():
            executor.register(method)
        request = AnalysisRequest(
            request_id="req:bad-compose",
            subject_id="equity:AAPL",
            question="Attempt an explicitly invalid selection.",
            method_id="analysis.dataset.compose",
            evidence_ids=(),
            analysis_inputs=(),
            parameters={
                "alignment": [
                    {"input_name": "left", "key": {"mode": "ROW_POSITION"}},
                    {"input_name": "right", "key": {"mode": "COLUMN", "column": "index"}},
                ],
                "selections": [
                    {"input_name": "left", "column": "missing", "output_name": "x"},
                ],
                "join_type": "INNER",
            },
            research_phase=ResearchPhase.EXPLORATION,
        )
        result = executor.execute(
            request,
            {
                "left": [{"value": 1.0}, {"value": 2.0}],
                "right": [{"index": 0, "other": 3.0}, {"index": 1, "other": 4.0}],
            },
        )
        self.assertIn("execution_error", result.outputs)
        self.assertIn("selected column 'missing'", result.outputs["execution_error"])
        self.assertEqual(
            result.outputs["interpretation_boundary"],
            "OBJECTIVE_EXECUTION_ERROR_RD_DECIDES_NEXT_STEP",
        )


if __name__ == "__main__":
    unittest.main()
