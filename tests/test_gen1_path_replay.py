import unittest,numpy as np
from Core.layered_ga.gen1_path_replay import replay_trade_counterfactual
class ReplayTests(unittest.TestCase):
 def test_exits_use_checkpoint_and_cost_included(self):
  r=replay_trade_counterfactual(np.array([-.1,.2]),np.array([-.03,.01]),np.array([True,False]),np.array([True,True]))
  self.assertAlmostEqual(r['incremental_net_sum'],.07)
  self.assertEqual(r['exited'],1)
 def test_invalid_future_excluded(self):
  r=replay_trade_counterfactual(np.array([np.nan,.1]),np.array([np.nan,.0]),np.array([True,False]),np.array([False,True]))
  self.assertEqual(r['eligible'],1)
 def test_shape_fails(self):
  with self.assertRaises(ValueError):replay_trade_counterfactual([1],[1,2],[True],[True])
if __name__=='__main__':unittest.main()
