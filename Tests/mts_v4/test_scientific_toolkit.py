from __future__ import annotations

import unittest

from MTS_V4.scientific_toolkit import (
    ScientificToolkitError,
    execute_scientific_toolkit,
    scientific_tool_count,
    scientific_toolkit_method_spec,
)


class ScientificToolkitTests(unittest.TestCase):
    def test_toolkit_exposes_hundreds_of_neutral_calculation_resources(self):
        count = scientific_tool_count()
        self.assertGreaterEqual(count, 500)
        spec = scientific_toolkit_method_spec()
        self.assertEqual(spec.metadata["tool_count"], count)
        self.assertFalse(spec.metadata["deterministic_ranking"])
        self.assertEqual(spec.metadata["scientific_selection"], "AI_RESEARCH_DIRECTOR_ONLY")
        index = spec.metadata["tool_index"]
        self.assertTrue(any(str(item).startswith("scipy.stats.pearsonr") for item in index))
        self.assertTrue(any(str(item).startswith("scipy.stats.spearmanr") for item in index))
        self.assertTrue(any(str(item).startswith("scipy.signal.") for item in index))
        self.assertTrue(any(str(item).startswith("scipy.special.") for item in index))

    def test_rd_selected_pearsonr_returns_inferential_output(self):
        rows = [
            {"x": 1.0, "y": 2.0},
            {"x": 2.0, "y": 4.1},
            {"x": 3.0, "y": 5.9},
            {"x": 4.0, "y": 8.2},
            {"x": 5.0, "y": 10.1},
        ]
        result = execute_scientific_toolkit(
            {"evidence:1": rows},
            {
                "tool_id": "scipy.stats.pearsonr",
                "args": [{"column": "x"}, {"column": "y"}],
                "kwargs": {},
            },
        )
        self.assertEqual(result["tool_id"], "scipy.stats.pearsonr")
        self.assertEqual(result["interpretation_boundary"], "CALCULATION_ONLY_RD_INTERPRETS")
        payload = result["result"]
        self.assertIn("statistic", payload)
        self.assertIn("pvalue", payload)

    def test_toolkit_does_not_silently_drop_missing_values(self):
        rows = [{"x": 1.0}, {"x": None}, {"x": 3.0}]
        with self.assertRaises(ScientificToolkitError):
            execute_scientific_toolkit(
                {"evidence:1": rows},
                {
                    "tool_id": "scipy.stats.describe",
                    "args": [{"column": "x"}],
                    "kwargs": {},
                },
            )


if __name__ == "__main__":
    unittest.main()
