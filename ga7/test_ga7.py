"""Run with python -m unittest ga7.test_ga7 -v."""
import random
import unittest

from ga7.engine import FAMILIES, next_population, random_genome, pareto_fronts
from ga7.evaluator import Portfolio
from ga7.runner import FEATURES

class EvolutionTests(unittest.TestCase):
    def test_population(self):
        rng = random.Random(70079)
        population = [random_genome(rng, FEATURES, FAMILIES[i % 8]) for i in range(300)]
        scored = [(g, {"cagr": rng.random(), "mdd": rng.random(), "calmar": rng.random(),
                       "ev": rng.random(), "mae": -rng.random()}) for g in population]
        next_gen = next_population(scored, rng, FEATURES, 300)
        self.assertEqual(len(next_gen), 300)
        self.assertEqual(len({g.identity() for g in next_gen}), 300)
        self.assertEqual({g.family for g in next_gen}, set(FAMILIES))

    def test_pareto(self):
        rows = [(None, {"cagr": .20, "mdd": .10, "calmar": 2, "ev": .03, "mae": -.04}),
                (None, {"cagr": .10, "mdd": .20, "calmar": .5, "ev": .01, "mae": -.10})]
        self.assertEqual(pareto_fronts(rows), [[0], [1]])

class AccountingTests(unittest.TestCase):
    def test_liquidation_and_costs(self):
        p = Portfolio()
        p.session = 0
        self.assertTrue(p.buy("AAA", 100, .10, {"AAA": 100}))
        p.update_low("AAA", 95)
        p.mark("day1", {"AAA": 105})
        p.session = 1
        result = p.finish("day2", {"AAA": 110})
        self.assertFalse(p.positions)
        self.assertEqual(result["trades"], 1)
        self.assertLess(result["mae"], 0)
        self.assertGreater(result["final_nav"], 100000)

    def test_missing_price_fails_closed(self):
        p = Portfolio()
        p.buy("AAA", 100, .10, {"AAA": 100})
        with self.assertRaises(ValueError):
            p.mark("day1", {})

if __name__ == "__main__":
    unittest.main()
