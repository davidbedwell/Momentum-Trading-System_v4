import unittest
import numpy as np
from Core.layered_ga.regime_liquidation import forced_exit_horizons,select_executable_returns
from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
class TestLiquidation(unittest.TestCase):
 def setUp(self):
  self.d=np.array(["2020-01-02","2020-01-03","2020-01-06","2020-01-07","2020-01-08"],dtype="datetime64[D]")
  self.ids=np.array(["ABC"]*5)
 def test_exit(self):
  np.testing.assert_array_equal(forced_exit_horizons(self.d,self.ids,["2020-01-07"],4),[3,2,1,0,-1])
 def test_none(self):
  np.testing.assert_array_equal(forced_exit_horizons(self.d,self.ids,[],4),[-1]*5)
 def test_short_horizon(self):
  np.testing.assert_array_equal(forced_exit_horizons(self.d,self.ids,["2020-01-07"],1),[-1,-1,1,0,-1])
 def test_missing_transition_date(self):
  with self.assertRaises(ValueError):forced_exit_horizons(self.d,self.ids,["2020-01-05"],4)
 def test_executable_return_and_cost(self):
  ret=np.tile(np.array([.01,.02,.03,.04]),(5,1));cost=np.tile(np.array([.001,.002,.003,.004]),(5,1))
  paths=ExecutionPaths(ret,ret,ret,ret);costs=ProspectiveCosts(cost,cost,cost,cost,cost,cost)
  gross,c,exit_h=select_executable_returns(paths,costs,"LONG",self.d,self.ids,["2020-01-07"],4)
  np.testing.assert_allclose(gross[:3],[.03,.02,.01]);np.testing.assert_allclose(c[:3],[.003,.002,.001])
  self.assertTrue(np.isnan(gross[3]));self.assertEqual(exit_h[3],0)
  short,_,_=select_executable_returns(paths,costs,"SHORT",self.d,self.ids,["2020-01-07"],4)
  self.assertAlmostEqual(short[0],-.03)
if __name__=="__main__":unittest.main()