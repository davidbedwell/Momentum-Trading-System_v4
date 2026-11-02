"""Accounting, delay, inference and frozen-protocol checks; no market outcomes."""
import sys, unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze import simulate, metrics, inference, holm
from run import verify_protocol
class AnalysisChecks(unittest.TestCase):
 def panel(self):
  ix=pd.bdate_range('2020-01-01',periods=8)
  return pd.DataFrame({'SPY':[100,100,200,200,200,200,200,200],'XLB':[100,100,200,200,200,200,200,200]},index=ix)
 def test_delayed_monthly_execution(self):
  p=self.panel();t={p.index[2]:{'top':['XLB'],'bottom':['SPY'],'eligible':['XLB']}}
  d=simulate(p,t,'top',0,str(p.index[0].date()),str(p.index[-1].date()))
  self.assertEqual(d.index[0],p.index[3]);self.assertAlmostEqual(d['return'].sum(),0)
 def test_entry_exit_cost(self):
  p=self.panel();p[:]=100;c=.003
  d=simulate(p,None,'SPY',c,str(p.index[1].date()),str(p.index[-1].date()))
  self.assertAlmostEqual((1+d['return']).prod(),(1-c)/(1+c),places=12)
  self.assertLess(metrics(d)['mdd'],0)
 def test_drifting_holdings(self):
  p=self.panel();p['SPY']=100;t={p.index[0]:{'top':['XLB','SPY'],'bottom':[],'eligible':['XLB','SPY']}}
  d=simulate(p,t,'top',0,str(p.index[1].date()),str(p.index[-1].date()))
  self.assertAlmostEqual((1+d['return']).prod(),1.5)
 def test_holm(self):np.testing.assert_allclose(holm([.01,.04,.03]),[.03,.06,.06])
 def test_deterministic_bootstrap(self):self.assertEqual(inference(np.arange(40)/100),inference(np.arange(40)/100))
 def test_protocol(self):self.assertEqual(verify_protocol()['sha256'],'23a49749f06cfc44c4c7f5a203e5f18cd04343d5763e7541100c4f977a2f756f')
if __name__=='__main__':unittest.main()
