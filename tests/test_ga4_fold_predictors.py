import unittest
from unittest.mock import patch
import pandas as pd

from Core.layered_ga.ga4_fold_isolation import freeze_fold_membership
from Core.layered_ga.ga4_fold_predictors import rebuild_fold_predictors


class TestFoldPredictors(unittest.TestCase):
    def setUp(self):
        self.membership = freeze_fold_membership(
            [f"D{i}" for i in range(80)], [f"H{i}" for i in range(37)])

    def test_recompute_receives_only_dev80(self):
        frame = pd.DataFrame({"security_id": self.membership["dev80"] + self.membership["dev37"],
                              "effective_date": ["2026-01-01"] * 117,
                              "return_252__v1": list(range(117))})
        seen = []
        def recompute(data):
            seen.extend(data["security_id"])
            return data
        with patch("Core.layered_ga.ga4_fold_predictors.recompute_cross_sectional", side_effect=recompute):
            result, scope = rebuild_fold_predictors(frame, self.membership, "DEV80")
        self.assertEqual(len(result), 80)
        self.assertEqual(set(seen), set(self.membership["dev80"]))
        self.assertTrue(scope.endswith(":DEV80:recomputed"))

    def test_reject_precomputed_cross_sectional_columns(self):
        frame = pd.DataFrame({"security_id": self.membership["dev80"],
                              "return_252_percentile__v1": [0.5] * 80})
        with self.assertRaises(ValueError):
            rebuild_fold_predictors(frame, self.membership, "DEV80")


if __name__ == "__main__":
    unittest.main()
