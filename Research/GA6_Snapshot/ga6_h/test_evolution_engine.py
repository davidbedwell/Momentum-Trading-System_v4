import tempfile,unittest,random
from pathlib import Path
from evolution_engine import nondominated,rank_records,breed,evaluate_population,run,diagnostic_evaluator
from context_free_genome import random_genome

class EvolutionTests(unittest.TestCase):
    def test_pareto(self):
        r=random.Random(1);a=random_genome(r);b=random_genome(r)
        records=[(a,{'net_ev':2,'ev_per_session':2,'reliability':2,'training_consistency':2,'opportunity_coverage':2}),
                 (b,{'net_ev':1,'ev_per_session':1,'reliability':1,'training_consistency':1,'opportunity_coverage':1})]
        self.assertEqual(nondominated(records),[[0],[1]])
    def test_tradeoff(self):
        r=random.Random(2);a=random_genome(r);b=random_genome(r)
        records=[(a,{'net_ev':2,'ev_per_session':1,'reliability':2,'training_consistency':2,'opportunity_coverage':2}),
                 (b,{'net_ev':1,'ev_per_session':2,'reliability':2,'training_consistency':2,'opportunity_coverage':2})]
        self.assertEqual(len(nondominated(records)[0]),2)
    def test_breeding_novelty(self):
        r=random.Random(3);members=[random_genome(r) for _ in range(20)]
        records=evaluate_population(members,diagnostic_evaluator)
        kids=breed(records,20,r)
        self.assertEqual(len({g.identity() for g in kids}),20)
    def test_parallel_parity(self):
        r=random.Random(4);members=[random_genome(r) for _ in range(8)]
        self.assertEqual(evaluate_population(members,diagnostic_evaluator,1),evaluate_population(members,diagnostic_evaluator,2))
    def test_checkpoint_resume(self):
        with tempfile.TemporaryDirectory() as d:
            first=run(d,population=12,generations=2,seed=3,workers=1,patience=100)
            self.assertEqual(first['generation'],2)
            second=run(d,population=12,generations=4,seed=3,workers=1,patience=100)
            self.assertEqual(second['generation'],4)
            self.assertEqual(len(list(Path(d).glob('generation_*.json'))),4)
    def test_stagnation(self):
        with tempfile.TemporaryDirectory() as d:
            out=run(d,population=12,generations=10,seed=3,patience=2)
            self.assertIn(out['stop_reason'],('stagnation','generation_limit'))
if __name__=='__main__':unittest.main()
