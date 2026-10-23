import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from optimizer_v3 import fitness,evolve,research_diagnostic,NICHES
from test_ga5_chromosome_contract import seed
from test_ga5_evolution_pilot import EvolutionTests
class RedesignTests(unittest.TestCase):
 def test_drawdown_penalty(self):
  a={"cagr_diagnostic":.20,"mdd_diagnostic":-.05,"fills":10}
  b={**a,"mdd_diagnostic":-.24}
  self.assertGreater(fitness(a),fitness(b))
 def test_cash_penalty(self):
  self.assertLess(fitness({"cagr_diagnostic":0,"mdd_diagnostic":0,"fills":0}),0)
 def test_safeguards_fail_closed(self):
  with self.assertRaises(ValueError):evolve(None,seed())
  with self.assertRaises(NotImplementedError):
   evolve(None,seed(),blocked={},earnings_verified=True,membership={},
          risk_veto=lambda *x:True,settlement={},cash_proxy={})
 def test_niches_and_diversity(self):
  x=research_diagnostic(EvolutionTests().bars(),seed(),generations=1,population=28)
  self.assertEqual(x["evaluations"],28)
  self.assertEqual(set(x["best_by_niche"]),set(NICHES))
  self.assertTrue(all(v["unique"]==4 for v in x["history"][0]["niches"].values()))
if __name__=="__main__":unittest.main()
