from __future__ import annotations

import unittest

from MTS_V4.analysis import ExactMethodAnalysisExecutor
from MTS_V4.contracts import AnalysisRequest, ResearchPhase
from MTS_V4.standard_methods import standard_analysis_methods


class AlignmentIdentitySpaceGuardTests(unittest.TestCase):
    @staticmethod
    def _executor() -> ExactMethodAnalysisExecutor:
        executor = ExactMethodAnalysisExecutor()
        for method in standard_analysis_methods():
            executor.register(method)
        return executor

    @staticmethod
    def _events():
        return [
            {
                "index": 1,
                "value": -0.06,
                "__observation_lineage": {
                    "input_name": "aligned",
                    "input_row_start": 1,
                    "input_row_end": 1,
                    "input_row_anchor": 1,
                    "semantics": "MECHANICAL_INPUT_ROW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION",
                },
            },
            {
                "index": 3,
                "value": -0.07,
                "__observation_lineage": {
                    "input_name": "aligned",
                    "input_row_start": 3,
                    "input_row_end": 3,
                    "input_row_anchor": 3,
                    "semantics": "MECHANICAL_INPUT_ROW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION",
                },
            },
        ]

    @staticmethod
    def _request(second_key):
        return AnalysisRequest(
            request_id="req:identity-space",
            subject_id="equity:AAPL",
            question="Compose only if the selected keys share a mechanically proven identity space.",
            method_id="analysis.dataset.compose",
            evidence_ids=(),
            analysis_inputs=(),
            parameters={
                "alignment": [
                    {"input_name": "events", "key": {"mode": "COLUMN", "column": "index"}},
                    {"input_name": "aligned", "key": second_key},
                ],
                "selections": [
                    {"input_name": "events", "column": "value", "output_name": "event_value"},
                    {"input_name": "aligned", "column": "return", "output_name": "return"},
                ],
                "join_type": "INNER",
            },
            research_phase=ResearchPhase.EXPLORATION,
        )

    def test_rejects_proven_parent_row_position_joined_to_unproven_column_identity(self):
        result = self._executor().execute(
            self._request({"mode": "COLUMN", "column": "anchor_index"}),
            {
                "events": self._events(),
                "aligned": [
                    {"anchor_index": 10, "return": 0.01},
                    {"anchor_index": 11, "return": 0.02},
                    {"anchor_index": 12, "return": 0.03},
                    {"anchor_index": 13, "return": 0.04},
                ],
            },
        )

        self.assertEqual(result.execution_metadata["execution_status"], "ERROR")
        self.assertIn("alignment identity-space defect", result.outputs["execution_error"])
        self.assertIn("anchor_index", result.outputs["execution_error"])
        self.assertEqual(
            result.outputs["interpretation_boundary"],
            "OBJECTIVE_EXECUTION_ERROR_RD_DECIDES_NEXT_STEP",
        )

    def test_accepts_proven_parent_row_position_joined_to_parent_row_position(self):
        result = self._executor().execute(
            self._request({"mode": "ROW_POSITION"}),
            {
                "events": self._events(),
                "aligned": [
                    {"return": 0.01},
                    {"return": 0.02},
                    {"return": 0.03},
                    {"return": 0.04},
                ],
            },
        )

        self.assertEqual(result.execution_metadata["execution_status"], "SUCCESS")
        rows = result.outputs["derived_datasets"]["composed_dataset"]
        self.assertEqual([row["alignment_key"] for row in rows], [1, 3])
        self.assertEqual([row["return"] for row in rows], [0.02, 0.04])


if __name__ == "__main__":
    unittest.main()
