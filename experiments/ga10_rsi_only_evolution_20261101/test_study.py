import unittest
import numpy as np
import pandas as pd
from study import prepare,simulate,arrays,SIZE,frontier_add
from prototype import rebalance
class Checks(unittest.TestCase):
 def fixture(self):
  dates=pd.bdate_range('2007-01-01',periods=600);rng=np.random.default_rng(4)
  c=pd.DataFrame(np.exp(np.cumsum(rng.normal(0,.015,(600,10)),axis=0)),index=dates)
  return c,prepare(c,c)
 def test_causal_screen(self):
  c,d=self.fixture();p=prepare(c.iloc[:400],c.iloc[:400])
  np.testing.assert_allclose(d['x'][:400],p['x'],equal_nan=True);np.testing.assert_array_equal(d['screen'][:400],p['screen'])
  np.testing.assert_array_equal(d['screen'],d['rsi'])
  self.assertTrue((d['screen'][300:].sum(axis=1)==2).all())
 def test_actions_screen_offscreen_reduce_reentry(self):
  T=100;prior=np.ones((T,1));opens=prior.copy();close=prior.copy();x=np.zeros((T,1,6));screen=np.zeros((T,1),dtype=bool);screen[0]=True
  monthly=np.zeros(T,dtype=bool);monthly[0]=True
  g=np.zeros(SIZE);g[0]=1;g[9]=-1;g[18]=-1;g[27]=-1
  # Entry on screen, subsequent offscreen hold; reduce score depends on age.
  g[18]=-0.001;g[26]=1
  m,p,c,e=simulate(g,prior,opens,close,x,screen,monthly)
  self.assertGreater(c[0],0);self.assertGreater(c[3],0);self.assertTrue(np.any(e[1:]==4))
  self.assertFalse(np.any(e[1:]==1))
  # Crash triggers liquidation; cash can re-enter while total performance drawdown persists.
  screen[:]=True;g[18]=-1;g[50]=-8;g[51]=-8;g[48]=8;g[49]=8;g[45]=8;g[36]=8
  close[2:]=.2;prior[3:]=.2;opens[3:]=.2
  m,p,c,e=simulate(g,prior,opens,close,x,screen,monthly)
  self.assertGreater(c[4],0);self.assertGreater(np.count_nonzero(e==1),1);self.assertGreater(m[1],.08)
 def test_accounting_and_missing(self):
  s,c,d,f,n=rebalance(np.zeros(2),1.,np.array([10.,20.]),np.array([.5,.5]))
  self.assertAlmostEqual(c+(s*np.array([10.,20.])).sum()+f,1.)
  with self.assertRaises(ValueError):rebalance(s,c,np.array([np.nan,20.]),np.zeros(2))
 def test_replay_baselines_and_fee(self):
  c,d=self.fixture();a=arrays(d,'2008-01-01','2008-12-31');g=np.zeros(SIZE)
  m,p,_,_=simulate(g,*a,2);self.assertEqual(m[0],0);self.assertEqual(m[1],0);self.assertEqual(m[3],1)
  m,p,_,_=simulate(g,*a,1);m2,p2,_,_=simulate(g,*a,1);np.testing.assert_array_equal(p,p2)
  self.assertGreater(m[4],0);self.assertTrue((p[:,3]<=1+1e-9).all())
 def test_frontier(self):
  f=[]
  for v in [[.1,.2,.5],[.2,.3,.7],[.09,.21,.4]]:f,_=frontier_add(f,{'m':v})
  self.assertEqual(len(f),2)
if __name__=='__main__':unittest.main()
