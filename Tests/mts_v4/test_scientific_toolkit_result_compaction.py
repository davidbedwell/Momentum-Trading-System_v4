from __future__ import annotations

import json
import unittest

from MTS_V4.scientific_toolkit import execute_scientific_toolkit


class ScientificToolkitResultCompactionTests(unittest.TestCase):
    def test_pearsonr_named_result_excludes_private_execution_state(self):
        rows = [
            {"x": float(index), "y": float(index * 2 + (index % 3))}
            for index in range(1, 503)
        ]
        result = execute_scientific_toolkit(
            {"evidence:1": rows},
            {
                "tool_id": "scipy.stats.pearsonr",
                "args": [{"column": "x"}, {"column": "y"}],
                "kwargs": {},
            },
        )

        self.assertEqual(result["interpretation_boundary"], "CALCULATION_ONLY_RD_INTERPRETS")
        payload = result["result"]
        self.assertIn("statistic", payload)
        self.assertIn("pvalue", payload)
        self.assertFalse(any(str(key).startswith("_") for key in payload))
        self.assertNotIn("_x", payload)
        self.assertNotIn("_y", payload)
        self.assertLess(len(json.dumps(payload, sort_keys=True)), 1000)


if __name__ == "__main__":
    unittest.main()
