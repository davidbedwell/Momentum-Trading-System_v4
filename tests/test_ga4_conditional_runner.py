import unittest
from types import SimpleNamespace
import numpy as np
from Core.layered_ga.ga4_conditional_runner import evaluate_conditional_candidate
from Core.layered_ga.stage2_path_v3 import ExecutionPaths, ProspectiveCosts


class StubCompiler:
    def __init__(self, n):
        self.frame = list(range(n))
    def compile(self, family, genome):
        n = len(self.frame)
        if family == "A":
            return np.arange(n) % 2 == 0
        return np.arange(n) % 3 == 0


class TestGA4ConditionalRunner(unittest.TestCase):
    def setUp(self):
        n = 90
        shape = (n, 63)
        self.paths = ExecutionPaths(
            np.tile(np.arange(1, 64) / 1000, (n, 1)),
            np.full(shape, -.02), np.full(shape, .03),
            np.tile(np.arange(1, 64), (n, 1)))
        z = np.zeros(shape)
        self.costs = ProspectiveCosts(z, z, z, z, z, z)
        self.compiler = StubCompiler(n)
        self.context = np.arange(n) % 5 != 0
        self.clusters = np.arange(n)

    def evaluate(self, chromosomes, context_mask=None):
        return evaluate_conditional_candidate(
            compiler=self.compiler, chromosomes=chromosomes,
            context_mask=self.context if context_mask is None else context_mask,
            context={"market": "fixture"}, paths=self.paths, costs=self.costs,
            cluster_ids=self.clusters, fold="DEV80-1",
            data_provenance="synthetic-test-only", min_raw_n=1, min_effective_n=1)

    def test_two_chromosome_interaction_and_63_day_evidence(self):
        record = self.evaluate([("A", {"x": 1}), ("B", {"x": 2})])
        self.assertEqual(len(record["daily_horizon_evidence"]), 63)
        expected = sum(i % 2 == 0 and i % 3 == 0 and i % 5 != 0 for i in range(90))
        self.assertEqual(record["daily_horizon_evidence"][0]["n"], expected)
        self.assertEqual(record["daily_horizon_evidence"][62]["horizon"], 63)
        self.assertFalse(record["certified"])

    def test_reject_nonboolean_context(self):
        with self.assertRaises(ValueError):
            self.evaluate([("A", {"x": 1})], np.ones(90, dtype=int))

    def test_reject_duplicate_chromosome(self):
        with self.assertRaises(ValueError):
            self.evaluate([("A", {"x": 1}), ("A", {"x": 1})])


if __name__ == "__main__":
    unittest.main()
