import unittest
import numpy as np
import pandas as pd
from ga10 import prepare,target,rebalance,run,SIZE,load

class Checks(unittest.TestCase):
    def test_prefix(self):
        rng=np.random.default_rng(4);dates=pd.bdate_range('2007-01-01',periods=600)
        c=pd.DataFrame(np.exp(np.cumsum(rng.normal(0,.015,(600,5)),axis=0)),index=dates,columns=list('ABCDE'))
        a=prepare(c,c);b=prepare(c.iloc[:400],c.iloc[:400])
        np.testing.assert_allclose(a['x'][:400],b['x'],equal_nan=True)
        np.testing.assert_array_equal(a['screen'][:400],b['screen'])
        g=np.zeros(SIZE);g[0]=1;g[27]=-1;g[18]=-1;g[9]=-1
        ma,na,ta=run(a,str(dates[260].date()),str(dates[399].date()),g,details=True)
        mb,nb,tb=run(b,str(dates[260].date()),str(dates[399].date()),g,details=True)
        pd.testing.assert_frame_equal(na,nb);pd.testing.assert_frame_equal(ta,tb)
        if len(ta):self.assertTrue((pd.to_datetime(ta.signal_date)<pd.to_datetime(ta.date)).all())
    def test_actions_and_screen(self):
        x=np.zeros((1,6));w=np.array([.04]);age=np.array([10]);pnl=np.array([0.])
        g=np.zeros(SIZE);g[[0,9,18,27]]=-1
        def act(gen,weight,screen):return target(gen,x,np.array([weight]),age,pnl,np.array([screen]),0)
        self.assertEqual(act(g,0,True)[0][0],0) # screen is no purchaser
        g[0]=1;self.assertGreater(act(g,0,True)[0][0],0)
        self.assertEqual(act(g,0,False)[0][0],0)
        self.assertEqual(act(g,.04,False)[1][0],'hold')
        g[9]=1;self.assertEqual(act(g,.04,False)[1][0],'add')
        g[18]=1;self.assertLess(act(g,.04,False)[0][0],.04)
        g[27]=1;self.assertEqual(act(g,.04,False)[0][0],0)
    def test_accounting(self):
        s,c,d,f,n=rebalance(np.zeros(2),1.,np.array([10.,20.]),np.array([.5,.5]))
        self.assertAlmostEqual(f,.001/1.001,places=10)
        self.assertAlmostEqual(c+sum(s*np.array([10.,20.]))+f,1.,places=10)
        s2,c2,d2,f2,n2=rebalance(s,c,np.array([10.,20.]),np.zeros(2))
        self.assertAlmostEqual(c2,n2-f2,places=10)
        with self.assertRaises(ValueError):rebalance(s,c,np.array([np.nan,20.]),np.zeros(2))
    def test_frozen_screen_matches_saved_membership(self):
        from pathlib import Path
        a=load();saved=pd.read_csv(Path(__file__).parent.parent/'dev79_rsi_fixed_full_2009_2018/selected_stocks.csv')
        expected=set(zip(saved.execution_date,saved.ticker))
        actual=set()
        for t in range(1,len(a['dates'])):
            d=a['dates'][t]
            if d.year>=2009 and d.to_period('M')!=a['dates'][t-1].to_period('M'):
                actual.update((str(d.date()),a['names'][j]) for j in np.flatnonzero(a['screen'][t]))
        self.assertEqual(actual,expected)

if __name__=='__main__':unittest.main()
