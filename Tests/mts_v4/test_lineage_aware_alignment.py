from __future__ import annotations

import unittest

from MTS_V4.contracts import AnalysisRequest, ResearchPhase
from MTS_V4.lineage_analysis import LineageAwareExactMethodAnalysisExecutor
from MTS_V4.standard_methods import standard_analysis_methods


class LineageAwareAlignmentTests(unittest.TestCase):
    @staticmethod
    def _executor() -> LineageAwareExactMethodAnalysisExecutor:
        executor = LineageAwareExactMethodAnalysisExecutor()
        for method in standard_analysis_methods():
            executor.register(method)
        return executor

    @staticmethod
    def _request(alignment, selections, request_id="req:compose") -> AnalysisRequest:
        return AnalysisRequest(
            request_id=request_id,
            subject_id="equity:AAPL",
            question="Mechanically align already-selected scientific inputs.",
            method_id="analysis.dataset.compose",
            evidence_ids=(),
            analysis_inputs=(),
            parameters={
                "alignment": alignment,
                "selections": selections,
                "join_type": "INNER",
            },
            research_phase=ResearchPhase.EXPLORATION,
        )

    @staticmethod
    def _lineaged_rows(parent: str, count: int, *, include_index: bool = False):
        rows = []
        for index in range(count):
            row = {
                "value": float(index),
                "__observation_lineage": {
                    "input_name": parent,
                    "input_row_start": index,
                    "input_row_end": index,
                    "input_row_anchor": index,
                    "semantics": "MECHANICAL_INPUT_ROW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION",
                },
            }
            if include_index:
                row["index"] = index
            rows.append(row)
        return rows

    def test_accepts_row_position_dataset_proven_to_share_column_parent_identity(self):
        executor = self._executor()
        request = self._request(
            [
                {"input_name": "states", "key": {"mode": "ROW_POSITION"}},
                {"input_name": "forward", "key": {"mode": "COLUMN", "column": "index"}},
            ],
            [
                {"input_name": "states", "column": "value", "output_name": "state"},
                {"input_name": "forward", "column": "value", "output_name": "forward"},
            ],
        )
        result = executor.execute(
            request,
            {
                "states": self._lineaged_rows("evidence:ohlcv", 4),
                "forward": self._lineaged_rows("evidence:ohlcv", 4, include_index=True),
            },
        )
        self.assertEqual(result.execution_metadata["execution_status"], "SUCCESS")
        rows = result.outputs["derived_datasets"]["composed_dataset"]
        self.assertEqual([row["alignment_key"] for row in rows], [0, 1, 2, 3])
        self.assertTrue(all(row["__observation_lineage"]["input_name"] == "evidence:ohlcv" for row in rows))

    def test_rejects_unproven_column_against_proven_parent_identity(self):
        executor = self._executor()
        request = self._request(
            [
                {"input_name": "events", "key": {"mode": "COLUMN", "column": "index"}},
                {"input_name": "other", "key": {"mode": "COLUMN", "column": "anchor"}},
            ],
            [
                {"input_name": "events", "column": "value", "output_name": "event"},
                {"input_name": "other", "column": "value", "output_name": "other"},
            ],
        )
        events = self._lineaged_rows("parent", 3, include_index=True)
        other = [{"anchor": i, "value": float(i)} for i in range(3)]
        result = executor.execute(request, {"events": events, "other": other})
        self.assertEqual(result.execution_metadata["execution_status"], "ERROR")
        self.assertIn("alignment identity-space defect", result.outputs["execution_error"])

    def test_compose_output_propagates_only_proven_common_identity(self):
        executor = self._executor()
        first = self._request(
            [
                {"input_name": "left", "key": {"mode": "COLUMN", "column": "index"}},
                {"input_name": "right", "key": {"mode": "COLUMN", "column": "index"}},
            ],
            [
                {"input_name": "left", "column": "value", "output_name": "left_value"},
                {"input_name": "right", "column": "value", "output_name": "right_value"},
            ],
            request_id="req:first",
        )
        result = executor.execute(
            first,
            {
                "left": self._lineaged_rows("evidence:ohlcv", 3, include_index=True),
                "right": self._lineaged_rows("evidence:ohlcv", 3, include_index=True),
            },
        )
        self.assertEqual(result.execution_metadata["execution_status"], "SUCCESS")
        composed = result.outputs["derived_datasets"]["composed_dataset"]
        self.assertEqual(
            LineageAwareExactMethodAnalysisExecutor._parent_row_position_identity(
                composed, "alignment_key"
            ),
            "evidence:ohlcv",
        )


if __name__ == "__main__":
    unittest.main()
