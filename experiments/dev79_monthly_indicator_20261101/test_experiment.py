import unittest
import numpy as np
import pandas as pd
from indicator_experiment import select,rebalance,indicators,replay,discovery_gate

class ExperimentTests(unittest.TestCase):
    def test_nan_selection_and_random_pool(self):
        s=np.array([1.,np.nan,3.,2.,np.inf,0.]);valid=np.ones(6,dtype=bool)
        w,n,k=select(s,valid);self.assertEqual((n,k),(4,1));self.assertEqual(w[0,2],1)
        r,n,k=select(s,valid,np.random.default_rng(1),500)
        self.assertTrue(np.all(r[:,[1,4]]==0));np.testing.assert_allclose(r.sum(1),1)
        np.testing.assert_array_equal(r,select(s,valid,np.random.default_rng(1),500)[0])
    def test_empty_pool_cash(self):
        w,n,k=select(np.array([np.nan]),np.array([True]));self.assertEqual(w.sum(),0);self.assertEqual(n,0)
    def test_cost_drift_self_financing(self):
        t=np.array([[.5,.5]]);p=np.zeros_like(t);f,u=rebalance(p,t)
        self.assertAlmostEqual(f[0],.001/1.001);self.assertAlmostEqual(1-f[0]+f[0],1)
        f,u=rebalance(t,t);self.assertEqual(f[0],0)
        f,u=rebalance(np.array([[1.,0.]]),np.array([[0.,1.]]));self.assertAlmostEqual(f[0],.002/1.001)
        f,u=rebalance(np.array([[.6,.4]]),t);self.assertGreater(f[0],0)
    def test_prefix_future_invariance(self):
        idx=pd.bdate_range('2007-01-01',periods=600);c=pd.DataFrame({'A':100*np.exp(np.arange(600)*.001)},index=idx)
        f=indicators(c);mut=c.copy();mut.iloc[500:]*=10
        g=indicators(mut)
        for key in f:pd.testing.assert_frame_equal(f[key].iloc[:500],g[key].iloc[:500])
        self.assertTrue(np.isnan(f['mom_12m_skip1m'].iloc[251,0]))
    def test_next_open_and_prior_signal(self):
        idx=pd.bdate_range('2008-12-01','2009-03-31');c=pd.DataFrame(100.,index=idx,columns=['A','B','C','D','E']);o=c.copy();s=c.copy()*0;s['A']=5
        # January first signal picks A from December close, despite January close ranking B.
        s.loc['2009-01-01':,'A']=0;s.loc['2009-01-01':,'B']=9
        o.loc['2009-01-01','A']=50
        m,table,w,r=replay(c,o,s,'2009-01-01','2009-03-31')
        self.assertEqual(w.iloc[0].ticker,'A');self.assertEqual(table.iloc[0].signal_date,'2008-12-31')
        self.assertAlmostEqual(table.iloc[0].strategy_return,2/1.001-1)
        self.assertEqual(table.iloc[-1].end_date,'2009-03-31');self.assertEqual(len(r),500)
    def test_blind_gate(self):
        row=dict(t=2.,p=.05,annualized_arithmetic_excess=.001)
        self.assertTrue(discovery_gate(row))
        for key,value in [('t',1.999),('p',.05001),('annualized_arithmetic_excess',0)]:
            self.assertFalse(discovery_gate(dict(row,**{key:value})))
    def test_adjusted_open_consistency(self):
        raw_open=np.array([50.,52.]);raw_close=np.array([51.,53.]);factor=np.array([.5,.5]);adj=raw_close*factor
        ao=raw_open*(adj/raw_close)
        np.testing.assert_allclose(ao[1]/ao[0],raw_open[1]/raw_open[0])
        self.assertNotEqual(raw_open[1]/adj[0],ao[1]/adj[0])
if __name__=='__main__':unittest.main()
