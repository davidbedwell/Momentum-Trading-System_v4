from __future__ import annotations

import unittest

from MTS_V4.analysis import ExactMethodAnalysisExecutor
from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.contracts import AnalysisRequest, EvidenceDescriptor, ResearchDecision, ResearchPhase, SubjectMetadata
from MTS_V4.nexus import InMemoryResearchNexus
from MTS_V4.orchestrator import ResearchLoopOrchestrator
from MTS_V4.standard_methods import standard_analysis_methods, standard_method_catalog
from MTS_V4.validation import ObjectiveContractValidator


class _CatalogRD:
    def __init__(self) -> None:
        self.begin_context = None
        self.interpret_context = None
        self.interpreted_result_id = None

    def begin_research(self, **kwargs):
        self.begin_context = kwargs["nexus_context"]
        return ResearchDecision(
            continue_research=True,
            next_request=AnalysisRequest(
                request_id="req:returns",
                subject_id="equity:AAPL",
                question="Generate returns.",
                method_id="analysis.transform.percent_change",
                evidence_ids=("evidence:AAPL",),
                analysis_inputs=(),
                parameters={"column": "close", "lag": 1},
                research_phase=ResearchPhase.EXPLORATION,
            ),
        )

    def resume_research(self, **kwargs):
        raise AssertionError("resume not expected")

    def repair_request(self, **kwargs):
        raise AssertionError(f"unexpected repair: {kwargs['defects']}")

    def interpret_result(self, **kwargs):
        self.interpret_context = kwargs["nexus_context"]
        self.interpreted_result_id = kwargs["result"].result_id
        return ResearchDecision(continue_research=False, close_reason="CATALOG_OBSERVED")


class CampaignResultCatalogAndObservationLineageTests(unittest.TestCase):
    @staticmethod
    def _executor() -> ExactMethodAnalysisExecutor:
        executor = ExactMethodAnalysisExecutor()
        for method in standard_analysis_methods():
            executor.register(method)
        return executor

    @staticmethod
    def _rows():
        return [
            {"date": "2026-01-01", "close": 100.0, "volume": 10.0},
            {"date": "2026-01-02", "close": 105.0, "volume": 20.0},
            {"date": "2026-01-03", "close": 102.0, "volume": 30.0},
            {"date": "2026-01-04", "close": 110.0, "volume": 40.0},
            {"date": "2026-01-05", "close": 115.0, "volume": 50.0},
        ]

    @staticmethod
    def _evidence() -> EvidenceDescriptor:
        return EvidenceDescriptor(
            evidence_id="evidence:AAPL",
            subject_id="equity:AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture",
            coverage_start="2026-01-01",
            coverage_end="2026-01-05",
            row_count=5,
            schema=("date", "close", "volume"),
            cache_key="cache:AAPL",
        )

    def test_rd_sees_compact_campaign_result_catalog_without_row_payloads(self):
        cache = TemporaryResearchCache()
        cache.put("cache:AAPL", self._rows())
        catalog = standard_method_catalog()
        rd = _CatalogRD()
        outcome = ResearchLoopOrchestrator(
            mission="test",
            rd=rd,
            validator=ObjectiveContractValidator(catalog),
            analysis=self._executor(),
            nexus=InMemoryResearchNexus(),
            cache=cache,
            available_methods=catalog.capability_payloads(),
        ).run(
            subject=SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL"),
            evidence=(self._evidence(),),
            max_analyses=1,
        )

        self.assertTrue(outcome.closed)
        self.assertEqual(rd.begin_context["campaign_analysis_result_catalog"], ())
        visible = rd.interpret_context["campaign_analysis_result_catalog"]
        self.assertEqual(len(visible), 1)
        entry = visible[0]
        self.assertEqual(entry["result_id"], rd.interpreted_result_id)
        self.assertTrue(entry["result_id"].startswith("analysis-result:"))
        self.assertEqual(entry["method_id"], "analysis.transform.percent_change")
        reusable = entry["reusable_derived_datasets"]["percent_change"]
        self.assertEqual(reusable["output_path"], ["derived_datasets", "percent_change"])
        self.assertEqual(reusable["schema"], ["index", "value"])
        self.assertIn("observation_lineage", reusable)
        self.assertNotIn("derived_datasets", entry)
        policy = rd.interpret_context["campaign_analysis_result_catalog_policy"]
        self.assertEqual(policy["persistence"], "CAMPAIGN_LOCAL_NOT_NEXUS")
        self.assertFalse(policy["contains_row_payloads"])

    def test_percent_change_and_forward_rows_get_hidden_mechanical_lineage(self):
        executor = self._executor()
        rows = self._rows()
        percent = executor.execute(
            AnalysisRequest(
                request_id="req:pct",
                subject_id="equity:AAPL",
                question="Percent change.",
                method_id="analysis.transform.percent_change",
                evidence_ids=("evidence:AAPL",),
                analysis_inputs=(),
                parameters={"column": "close", "lag": 2},
                research_phase=ResearchPhase.EXPLORATION,
            ),
            {"evidence:AAPL": rows},
        )
        first_pct = percent.outputs["derived_datasets"]["percent_change"][0]
        self.assertEqual(first_pct["index"], 2)
        self.assertEqual(
            first_pct["__observation_lineage"],
            {
                "input_name": "evidence:AAPL",
                "input_row_start": 0,
                "input_row_end": 2,
                "input_row_anchor": 2,
                "semantics": "MECHANICAL_INPUT_ROW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION",
            },
        )
        self.assertEqual(
            percent.outputs["derived_dataset_catalog"]["percent_change"]["schema"],
            ["index", "value"],
        )

        forward = executor.execute(
            AnalysisRequest(
                request_id="req:forward",
                subject_id="equity:AAPL",
                question="Forward path.",
                method_id="analysis.path.forward_measurement",
                evidence_ids=("evidence:AAPL",),
                analysis_inputs=(),
                parameters={"price_column": "close", "horizon": 2, "direction": "LONG"},
                research_phase=ResearchPhase.EXPLORATION,
            ),
            {"evidence:AAPL": rows},
        )
        first_forward = forward.outputs["derived_datasets"]["forward_path_observations"][0]
        self.assertEqual(first_forward["index"], 0)
        self.assertEqual(first_forward["__observation_lineage"]["input_row_start"], 0)
        self.assertEqual(first_forward["__observation_lineage"]["input_row_end"], 2)
        self.assertEqual(first_forward["__observation_lineage"]["input_row_anchor"], 0)

    def test_hidden_lineage_tracks_immediate_input_on_derived_of_derived_work(self):
        executor = self._executor()
        rows = self._rows()
        percent = executor.execute(
            AnalysisRequest(
                request_id="req:pct",
                subject_id="equity:AAPL",
                question="Percent change.",
                method_id="analysis.transform.percent_change",
                evidence_ids=("evidence:AAPL",),
                analysis_inputs=(),
                parameters={"column": "close", "lag": 1},
                research_phase=ResearchPhase.EXPLORATION,
            ),
            {"evidence:AAPL": rows},
        )
        derived_rows = percent.outputs["derived_datasets"]["percent_change"]
        rolling = executor.execute(
            AnalysisRequest(
                request_id="req:rolling",
                subject_id="equity:AAPL",
                question="Rolling mean.",
                method_id="analysis.rolling.statistics",
                evidence_ids=(),
                analysis_inputs=(),
                parameters={"column": "value", "window": 2, "statistic": "mean"},
                research_phase=ResearchPhase.EXPLORATION,
            ),
            {"daily_returns": derived_rows},
        )
        first = rolling.outputs["derived_datasets"]["rolling_statistic"][0]
        self.assertEqual(first["__observation_lineage"]["input_name"], "daily_returns")
        self.assertEqual(first["__observation_lineage"]["input_row_start"], 0)
        self.assertEqual(first["__observation_lineage"]["input_row_end"], 1)
        self.assertEqual(first["__observation_lineage"]["input_row_anchor"], 1)


if __name__ == "__main__":
    unittest.main()
