import unittest
from unittest.mock import patch
from Core.layered_ga.ga4_combination_evolution import evolve_combinations


class Gene:
    gene_id = "x"
    values = tuple(range(20))


class Space:
    genes = (Gene(),)


class Curve:
    points = tuple({"horizon": h, "ev_net": 0.01, "lcb95": 0.001,
                    "mae_mean": -0.02, "mae_tail5": -0.03}
                   for h in range(1, 64))


class TestCombinationEvolution(unittest.TestCase):
    def test_evaluates_before_selection(self):
        observations = []
        def evaluate(chromosomes):
            observations.append(tuple(chromosomes))
            return Curve()
        def select(population, size):
            self.assertTrue(observations)
            return population[:size], {}
        with patch("Core.layered_ga.ga4_combination_evolution.environmental_selection", side_effect=select):
            result = evolve_combinations({"A": Space(), "B": Space()}, evaluate,
                                         seed=19, population_size=6, generations=3)
        self.assertGreaterEqual(result["unique_evaluations"], 6)
        self.assertEqual(len(result["generations"]), 3)
        self.assertTrue(all(1 <= len(x) <= 4 for x in observations))
        self.assertFalse(result["certified"])


if __name__ == "__main__":
    unittest.main()
