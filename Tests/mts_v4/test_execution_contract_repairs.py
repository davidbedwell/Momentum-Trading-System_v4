from __future__ import annotations

import unittest

from MTS_V4.scientific_toolkit import (
    ScientificToolkitError,
    _single_rows,
    scientific_toolkit_method_spec,
)
from MTS_V4.standard_methods import compose_aligned_dataset


class ExecutionContractRepairTests(unittest.TestCase):
    def test_composition_preserves_first_rd_authored_alignment_input_order(self):
        raw_rows = [{"value": float(index)} for index in range(12)]
        derived_rows = [{"index": index, "derived": float(index * 10)} for index in range(12)]

        result = compose_aligned_dataset(
            {"raw": raw_rows, "derived": derived_rows},
            {
                "alignment": [
                    {"input_name": "raw", "key": {"mode": "ROW_POSITION"}},
                    {"input_name": "derived", "key": {"mode": "COLUMN", "column": "index"}},
                ],
                "selections": [
                    {"input_name": "raw", "column": "value", "output_name": "value"},
                    {"input_name": "derived", "column": "derived", "output_name": "derived"},
                ],
                "join_type": "INNER",
            },
        )

        rows = result["derived_datasets"]["composed_dataset"]
        self.assertEqual([row["alignment_key"] for row in rows], list(range(12)))
        self.assertEqual(
            result["output_order"],
            "PRESERVES_FIRST_RD_AUTHORED_ALIGNMENT_INPUT_ORDER",
        )

    def test_composition_preserves_non_sorted_first_input_order(self):
        first = [
            {"key": 3, "x": 30.0},
            {"key": 1, "x": 10.0},
            {"key": 2, "x": 20.0},
        ]
        second = [
            {"key": 1, "y": 100.0},
            {"key": 2, "y": 200.0},
            {"key": 3, "y": 300.0},
        ]

        result = compose_aligned_dataset(
            {"first": first, "second": second},
            {
                "alignment": [
                    {"input_name": "first", "key": {"mode": "COLUMN", "column": "key"}},
                    {"input_name": "second", "key": {"mode": "COLUMN", "column": "key"}},
                ],
                "selections": [
                    {"input_name": "first", "column": "x", "output_name": "x"},
                    {"input_name": "second", "column": "y", "output_name": "y"},
                ],
                "join_type": "INNER",
            },
        )

        rows = result["derived_datasets"]["composed_dataset"]
        self.assertEqual([row["alignment_key"] for row in rows], [3, 1, 2])

    def test_toolkit_capability_discloses_exactly_one_resolved_dataset(self):
        payload = scientific_toolkit_method_spec().capability_payload()
        contract = payload["metadata"]["input_payload_contract"]

        self.assertEqual(contract["required_payload_count"], 1)
        self.assertIn("evidence_ids", contract["counting_rule"])
        self.assertIn("analysis_inputs", contract["counting_rule"])
        self.assertIn("evidence_ids=[]", contract["derived_dataset_rule"])
        self.assertIn("exactly one analysis_inputs", contract["derived_dataset_rule"])
        self.assertIn("lineage", contract["derived_dataset_rule"])

    def test_toolkit_multi_payload_error_names_full_payload_contract(self):
        with self.assertRaises(ScientificToolkitError) as caught:
            _single_rows(
                {
                    "raw": [{"x": 1.0}],
                    "derived": [{"x": 2.0}],
                }
            )

        message = str(caught.exception)
        self.assertIn("exactly one resolved dataset payload", message)
        self.assertIn("evidence_ids", message)
        self.assertIn("analysis_inputs", message)


if __name__ == "__main__":
    unittest.main()
