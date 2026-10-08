import unittest
from unittest.mock import patch
from Core.layered_ga.ga4_combination_evolution import evolve_combinations

class TestCanonicalEvolution(unittest.TestCase):
    def test_order_independent_identity_and_single_evaluation(self):
        a=('MOMENTUM',{'x':1})
        b=('TREND',{'x':2})
        calls=[]
        class Individual:
            def __init__(self,genome,curve,candidate_id):
                self.genome,self.curve,self.candidate_id=genome,curve,candidate_id
        def fake_propose(spaces,rng):
            return [b,a] if len(calls)==0 else [a,b]
        def evaluate(items):
            calls.append(items)
            return 'curve'
        with patch('Core.layered_ga.ga4_combination_evolution.propose',side_effect=[[b,a],[a,b]]):
            with patch('Core.layered_ga.ga4_combination_evolution.Individual',Individual):
                with patch('Core.layered_ga.ga4_combination_evolution.environmental_selection',side_effect=lambda pool,n:(pool[:n],{})):
                    result=evolve_combinations({},evaluate,seed=1,population_size=2,generations=1)
        self.assertEqual(result['unique_evaluations'],1)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0],tuple(sorted((a,b))))

if __name__=='__main__':unittest.main()
