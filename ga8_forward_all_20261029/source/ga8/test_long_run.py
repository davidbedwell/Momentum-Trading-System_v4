import unittest
from .long_run import update_frontier, offspring
from .engine import Gene, Manager, identity
from dataclasses import asdict
import random


def row(cagr, mdd, calmar, feasible=False):
    genes=[Gene('trend'),Gene('momentum'),Gene('breadth')]
    return dict(id=str((cagr,mdd,calmar)),metrics=dict(cagr=cagr,max_drawdown=mdd,calmar=calmar,feasible=feasible),
                genes=list(map(asdict,genes)),manager=asdict(Manager()),marginal=[dict(gene=i,incremental_nav=i) for i in range(3)])

class FrontierTests(unittest.TestCase):
    def test_tradeoffs_and_feasibility_archives(self):
        a=row(.1,.1,1)
        frontier,_=update_frontier([],a)
        frontier,changed=update_frontier(frontier,row(.11,.15,.8))
        self.assertTrue(changed)
        self.assertEqual(len(frontier),2)
        frontier,changed=update_frontier(frontier,row(.09,.16,.7))
        self.assertFalse(changed)
        frontier,changed=update_frontier(frontier,row(.2,.09,2,True))
        self.assertTrue(changed)
        self.assertEqual(len(frontier),3)
    def test_noise_does_not_reset_stagnation(self):
        a=row(.1,.1,1)
        _,changed=update_frontier([a],row(.100001,.1,1))
        self.assertFalse(changed)
    def test_material_pareto_progress(self):
        from .long_run import material_pareto_improvement,pareto_reference
        a=row(.20,.10,2.0,True)
        ref=pareto_reference([a])
        self.assertFalse(material_pareto_improvement([row(.201,.10,2.01,True)],ref))
        self.assertTrue(material_pareto_improvement([row(.20,.09,2.0,True)],ref))
        self.assertTrue(material_pareto_improvement([row(.20,.10,2.3,True)],ref))
        self.assertTrue(material_pareto_improvement([row(.21,.10,2.0,True)],ref))
        self.assertFalse(material_pareto_improvement([row(.22,.16,2.0,True)],ref))
        self.assertFalse(material_pareto_improvement([row(.21,.10,2.0,False)],ref))
    def test_population_uniqueness(self):
        rows=[row(.1,.1,1),row(.2,.12,1.6,True)]
        population=offspring(rows,rows,48,random.Random(42))
        self.assertEqual(len(population),48)
        self.assertEqual(len({identity(g,m) for g,m,_ in population}),48)

class OptimizationTests(unittest.TestCase):
    def test_schedule_and_json_tree_roundtrip(self):
        import json
        from .long_run import population_size,decode
        self.assertEqual(population_size(500,0,0,1),500)
        self.assertEqual(population_size(500,.6,0,1),300)
        self.assertEqual(population_size(500,1,0,1),175)
        r=row(.1,.1,1)
        r['genes'][0]['entry_tree']=['and','trend',['or','trend','momentum']]
        genes,_=decode(json.loads(json.dumps(r)))
        hash(tuple(genes))
    def test_cached_evaluation_exact_and_read_only(self):
        from . import long_run as lr
        from .test_engine import AccountingTests
        from .engine import replay
        previous=lr.PANEL
        try:
            lr.PANEL=AccountingTests().panel()
            lr.cached_replay.cache_clear()
            lr.cached_signal.cache_clear()
            genes=[Gene('trend'),Gene('momentum')]
            manager=Manager()
            expected=replay(lr.PANEL,genes,manager,'2022-01-01','2023-01-01')
            result=lr.evaluate((genes,manager,'2023-01-01'))
            self.assertEqual(expected['metrics'],result['metrics'])
            self.assertEqual(expected['audit'],result['audit'])
            self.assertEqual(result,lr.evaluate((genes,manager,'2023-01-01')))
            self.assertGreater(lr.cached_replay.cache_info().hits,0)
        finally:
            lr.cached_replay.cache_clear()
            lr.cached_signal.cache_clear()
            lr.PANEL=previous
    def test_cached_signals_preserve_detailed_native_replay(self):
        import numpy as np
        from .engine import replay,scores
        from .test_engine import AccountingTests
        p=AccountingTests().panel()
        genes=[Gene('trend',entry_tree=('and','trend',('or','momentum','trend'))),Gene('momentum',niche=1)]
        baseline=replay(p,genes,Manager(),'2022','2023',True)
        signal=np.array([scores(p,[g])[0] for g in genes])
        self.assertEqual(baseline,replay(p,genes,Manager(),'2022','2023',True,signal=signal))
