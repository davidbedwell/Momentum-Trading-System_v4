import unittest
from Core.layered_ga.ga4_combination_evolution import evolve_combinations
from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces
from Core.layered_ga.stage2_evaluator_v3 import CurveEvaluation

class BroadDiscoveryTests(unittest.TestCase):
    def test_no_duplicate_evaluations_or_population_cap_on_archive(self):
        observed = []
        def evaluate(ch):
            observed.append(ch)
            score = len(str(ch))/1000
            return CurveEvaluation('LONG', ({'horizon':1,'ev_net':score,'lcb95':score-0.01,'mae_mean':-0.1,'mae_tail5':-0.2},), (), ())
        result = evolve_combinations(stage2_search_spaces(), evaluate, seed=19, population_size=8, generations=15)
        self.assertEqual(result['unique_evaluations'], 8*15)
        self.assertEqual(len(observed), 8*15)
        self.assertFalse(result['certified'])

if __name__ == '__main__':
    unittest.main()
