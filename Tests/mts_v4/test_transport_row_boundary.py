from __future__ import annotations

import json
import unittest

from MTS_V4.contracts import AnalysisResult
from MTS_V4.openai_compatible_provider import OpenAICompatibleResearchDirector


class V4TransportRowBoundaryTests(unittest.TestCase):
    @staticmethod
    def _result(row_count: int) -> AnalysisResult:
        rows = [
            {"index": index, "value": float(index) / 1000.0}
            for index in range(row_count)
        ]
        return AnalysisResult(
            result_id="analysis-result:test",
            request_id="req:test",
            subject_id="equity:AAPL",
            method_id="analysis.transform.percent_change",
            outputs={
                "column": "close",
                "lag": 1,
                "observation_count": row_count,
                "observations": rows,
                "derived_dataset_catalog": {
                    "percent_change": {
                        "row_count": row_count,
                        "schema": ["index", "value"],
                        "output_path": ["derived_datasets", "percent_change"],
                        "temporary": True,
                    }
                },
                "derived_datasets": {"percent_change": rows},
                "interpretation_boundary": "MEASUREMENT_ONLY_RD_INTERPRETS",
            },
            evidence_ids=("ev:ohlcv",),
        )

    def test_exact_sibling_row_alias_is_withheld_and_remains_chainable(self):
        payload = OpenAICompatibleResearchDirector._analysis_result_payload(
            self._result(501)
        )
        outputs = payload["outputs"]
        self.assertNotIn("derived_datasets", outputs)
        self.assertNotIn("observations", outputs)
        self.assertEqual(outputs["observation_count"], 501)
        self.assertEqual(
            outputs["withheld_row_output_aliases"]["aliases"]["observations"]["output_path"],
            ["derived_datasets", "percent_change"],
        )
        self.assertEqual(
            outputs["derived_dataset_catalog"]["percent_change"]["row_count"], 501
        )

    def test_transport_size_does_not_scale_with_reproducible_row_count(self):
        small = OpenAICompatibleResearchDirector._analysis_result_payload(self._result(2))
        large = OpenAICompatibleResearchDirector._analysis_result_payload(self._result(501))
        small_size = len(json.dumps(small, sort_keys=True))
        large_size = len(json.dumps(large, sort_keys=True))
        self.assertLess(large_size - small_size, 100)


if __name__ == "__main__":
    unittest.main()
