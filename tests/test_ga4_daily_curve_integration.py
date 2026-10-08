"""Integration contract: GA4 evaluator retains every day 1..63 and EV/MAE."""
import unittest
import numpy as np
from Core.layered_ga.stage2_path_v3 import ExecutionPaths, ProspectiveCosts
from Core.layered_ga.stage2_evaluator_v3 import evaluate_curve


class TestGA4DailyCurveIntegration(unittest.TestCase):
    def make_arrays(self, horizon_count):
        n = 30
        shape = (n, horizon_count)
        endpoint = np.tile(np.arange(1, horizon_count + 1, dtype=float) / 1000, (n, 1))
        lows = -np.full(shape, .01)
        highs = np.full(shape, .02)
        days = np.tile(np.arange(1, horizon_count + 1, dtype=float), (n, 1))
        paths = ExecutionPaths(endpoint, lows, highs, days)
        zero = np.zeros(shape)
        costs = ProspectiveCosts(zero, zero, zero, zero, zero, zero)
        return paths, costs

    def test_all_horizons_and_risk(self):
        paths, costs = self.make_arrays(63)
        curve = evaluate_curve(np.ones(30, dtype=bool), paths, costs, "LONG", np.arange(30), min_raw_n=1, min_effective_n=1)
        self.assertEqual(tuple(p["horizon"] for p in curve.points), tuple(range(1, 64)))
        self.assertTrue(all("ev_net" in p and "mae_mean" in p for p in curve.points))

    def test_reject_sparse_path(self):
        paths, costs = self.make_arrays(7)
        with self.assertRaises(ValueError):
            evaluate_curve(np.ones(30, dtype=bool), paths, costs, "LONG", np.arange(30), min_raw_n=1, min_effective_n=1)


if __name__ == "__main__":
    unittest.main()
