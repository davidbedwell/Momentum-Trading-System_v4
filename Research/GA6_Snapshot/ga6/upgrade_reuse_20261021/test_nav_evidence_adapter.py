import unittest
from ga6.upgrade_reuse_20261021.nav_evidence_adapter import nav_to_returns,from_replays

class NavEvidenceTests(unittest.TestCase):
 def test_first_day_uses_starting_cash(self):
  dates,returns=nav_to_returns([('2026-01-01',101),('2026-01-02',102.01)],100)
  self.assertAlmostEqual(returns[0],.01)
  self.assertAlmostEqual(returns[1],.01)
 def test_full_portfolio_alignment(self):
  dates=['2026-01-01','2026-01-02','2026-01-03']
  plan={'loss_differential':'candidate_net_return_minus_benchmark_net_return','calendar_start':dates[0],'calendar_end':dates[-1]}
  benchmark=list(zip(dates,[100,100,100]))
  result=from_replays({'c':{'status':'GUARDED_RESEARCH_ONLY','calendar_nav':list(zip(dates,[101,102,103]))}},benchmark,100,plan)
  self.assertEqual(result['differentials'].shape,(3,1))
 def test_missing_nav_fails(self):
  with self.assertRaises(ValueError):from_replays({'c':{'status':'GUARDED_RESEARCH_ONLY'}},[('2026-01-01',100)],100,{})
if __name__=='__main__':unittest.main()
