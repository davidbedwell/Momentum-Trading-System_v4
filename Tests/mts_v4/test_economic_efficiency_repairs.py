from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from MTS_V4.batch_contracts import (
    BatchResearchDecision,
    ResearchPackagePlan,
    ScientificAnalysisSpecification,
)
from MTS_V4.bootstrap import build_batch_runtime
from MTS_V4.contracts import EvidenceDescriptor, ResearchPhase, SubjectMetadata
from MTS_V4.group_aggregation import group_aggregate
from MTS_V4.neutral_analysis_substrate import (
    LOGICAL_ANALYSIS_ID,
    build_for_subject,
)
from MTS_V4.openai_compatible_provider import OpenAICompatibleResearchDirector
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector
from MTS_V4.sol_spend_guard import SolResearchProgressEstimate


class _NoopRD:
    def begin_batch_research(self, **kwargs):
        return BatchResearchDecision(continue_research=False, close_reason="done")


def _progress() -> SolResearchProgressEstimate:
    return SolResearchProgressEstimate(50, 1, 1, "medium", "one batch remains")


class EconomicEfficiencyRepairTests(unittest.TestCase):
    def test_group_aggregate_values_remain_visible_after_row_transport_boundary(self):
        outputs = group_aggregate(
            {"rows": [{"month": 1, "value": 2}, {"month": 1, "value": 4}]},
            {
                "group_by": ["month"],
                "aggregations": [
                    {"column": "value", "statistic": "mean", "output_name": "value_mean"}
                ],
            },
        )
        from MTS_V4.contracts import AnalysisResult

        result = AnalysisResult(
            "r", "q", "equity:AAPL", "analysis.dataset.group_aggregate", outputs, ("ev",)
        )
        transported = OpenAICompatibleResearchDirector._analysis_result_payload(result)["outputs"]
        self.assertNotIn("derived_datasets", transported)
        self.assertEqual(
            transported["group_summaries"]['{"month":1}']["value_mean"],
            3.0,
        )

    def test_compact_prior_decision_uses_ai_authored_state_not_analysis_bodies(self):
        analysis = ScientificAnalysisSpecification(
            analysis_id="a:1",
            rp_id="rp:1",
            question_id="q:1",
            subject_id="equity:AAPL",
            question="test",
            method_id="analysis.descriptive.statistics",
            inputs=(),
            parameters={"columns": ["close"]},
            research_phase=ResearchPhase.EXPLORATION,
        )
        decision = BatchResearchDecision(
            continue_research=True,
            research_packages=(ResearchPackagePlan("rp:1", "objective", (analysis,)),),
            research_state={
                "scientific_continuation_state": {
                    "active_hypotheses": ["AI-authored hypothesis"]
                }
            },
            research_progress=_progress(),
        )
        compact = SolBatchResearchDirector._compact_prior_batch_decision(decision)
        self.assertEqual(
            compact["scientific_continuation_state"]["active_hypotheses"],
            ["AI-authored hypothesis"],
        )
        serialized = json.dumps(compact)
        self.assertNotIn("analysis.descriptive.statistics", serialized)
        self.assertIn("a:1", serialized)

    def test_continuing_decision_requires_ai_authored_continuation_state(self):
        with TemporaryDirectory() as directory:
            provider = SolBatchResearchDirector(
                research_package_store=JsonResearchPackageStore(Path(directory)),
                base_url="https://example.invalid",
                model="test",
                api_key="test",
            )
            decision = BatchResearchDecision(
                continue_research=True,
                research_packages=(
                    ResearchPackagePlan(
                        "rp:1",
                        "objective",
                        (
                            ScientificAnalysisSpecification(
                                "a:1", "rp:1", "q:1", "equity:AAPL", "question",
                                "analysis.descriptive.statistics", (), {"columns": ["close"]},
                                ResearchPhase.EXPLORATION,
                            ),
                        ),
                    ),
                ),
                research_progress=_progress(),
            )
            self.assertIn("scientific_continuation_state", provider._batch_decision_defect(decision))

    def test_standard_substrate_is_unranked_and_chainable(self):
        subject = SubjectMetadata("equity:AAPL", "AAPL")
        rows = []
        start = date(2020, 1, 1)
        for index in range(90):
            close = 100.0 + index * 0.2 + (index % 7) * 0.1
            rows.append(
                {
                    "date": (start + timedelta(days=index)).isoformat(),
                    "open": close - 0.2,
                    "high": close + 0.7,
                    "low": close - 0.8,
                    "close": close,
                    "volume": 1_000_000 + index * 1000,
                }
            )
        evidence = EvidenceDescriptor(
            "ev:ohlcv", subject.subject_id, "OHLCV", "NORMALIZED_DATASET", "fixture",
            rows[0]["date"], rows[-1]["date"], len(rows), tuple(rows[0]), "cache:ohlcv",
        )
        runtime = build_batch_runtime(rd=_NoopRD())
        runtime.cache.put(evidence.cache_key, rows)
        results = build_for_subject(
            subject=subject,
            evidence=(evidence,),
            cache=runtime.cache,
            analysis=runtime.analysis,
        )
        result = results[LOGICAL_ANALYSIS_ID]
        self.assertFalse(result.outputs["policy"]["deterministic_scientific_selection_or_ranking"])
        self.assertFalse(result.outputs["policy"]["findings_created"])
        self.assertGreater(len(result.outputs["unranked_relationship_measurements"]), 0)
        self.assertIn("standard_ohlcv_panel", result.outputs["derived_dataset_catalog"])
        self.assertTrue(
            result.execution_metadata["future_information"]["contains_future_information"]
        )


if __name__ == "__main__":
    unittest.main()
