import tempfile,unittest
from pathlib import Path
import numpy as np
import pandas as pd
from comparison import Ledger,features,run,INITIAL,FEE,SLIP,ROOT,SOURCE

class Tests(unittest.TestCase):
    def panel(self,n=140):
        d=type('Panel',(),{})();idx=pd.bdate_range('2020-01-01',periods=n)
        c=pd.DataFrame({'A':100*np.exp(np.arange(n)*.001),'B':100*np.exp(np.arange(n)*.0005)},index=idx)
        for key,value in dict(close=c,open=c*.999,high=c*1.01,low=c*.99,volume=c*0+1e6).items():setattr(d,key,value)
        return d
    def test_prefix_invariance_and_future_mutation(self):
        d=self.panel();before=features(d)
        for key in ('close','open','high','low','volume'):getattr(d,key).iloc[121:]*=3
        after=features(d)
        for k in before:pd.testing.assert_frame_equal(before[k].iloc[:121],after[k].iloc[:121])
        short=self.panel(121)
        for k,v in features(short).items():pd.testing.assert_frame_equal(before[k].iloc[:121],v)
    def test_partial_sale_cost_fees_and_settlement(self):
        b=Ledger();f=b.fill('A',100,10);self.assertAlmostEqual(f['price'],10*(1+SLIP));self.assertAlmostEqual(f['fee'],100*f['price']*FEE)
        cash=b.cash;b.fill('A',-40,12);self.assertEqual(b.cash,cash);self.assertGreater(b.due,0)
        self.assertAlmostEqual(b.accounts['A'].open_cost,60*10*(1+SLIP)*(1+FEE))
        nav=b.nav({'A':12});unreal=60*12-b.accounts['A'].open_cost
        self.assertAlmostEqual(nav,INITIAL+b.realized+unreal)
        due=b.due;b.settle();self.assertAlmostEqual(b.cash,cash+due);self.assertEqual(b.due,0)
    def test_cash_clip_and_no_double_split(self):
        b=Ledger();b.fill('A',1e9,100);self.assertGreaterEqual(b.cash,-1e-8)
        q=b.q['A'];self.assertAlmostEqual(b.nav({'A':100}),q*100);self.assertEqual(q,b.q['A'])
    def test_missing_window_blocks_eligibility(self):
        d=self.panel();d.close.iloc[110,0]=np.nan;f=features(d)
        self.assertFalse(f['eligible'].iloc[115,0]);self.assertTrue(pd.isna(f['trend'].iloc[115,0]))
    def test_next_open_and_missing_next_open_cancellation(self):
        d=self.panel();d.open.iloc[1,0]=np.nan;f=features(d);f['close']=d.close
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);run('buy_hold',d,f,out,str(d.close.index[0].date()),str(d.close.index[4].date()))
            fills=pd.read_csv(out/'fills.csv');orders=pd.read_csv(out/'orders.csv')
            self.assertTrue((pd.to_datetime(fills.date)>pd.to_datetime(fills.signal_date)).all())
            self.assertTrue((orders.status=='CANCEL_MISSING_NEXT_OPEN').any())
            # Missing open is never invented; retry requires a new close decision.
            self.assertFalse(((fills.ticker=='A')&(fills.date==str(d.close.index[1].date()))).any())
    def test_historical_fills_match_archived_next_session_open(self):
        base=ROOT/'artifacts'
        if not (base/'metrics.json').exists():self.skipTest('run historical replay first')
        raw=pd.read_parquet(SOURCE,columns=['date','ticker','open'],use_threads=False)
        raw.date=raw.date.dt.strftime('%Y-%m-%d')
        days=sorted(raw.date.unique());nxt=dict(zip(days[:-1],days[1:]))
        for mode in ['manager','claude_approx','gemini_approx','grok_dev79_approx']:
            fills=pd.read_csv(base/mode/'fills.csv')
            self.assertEqual(list(fills.date),[nxt[d] for d in fills.signal_date])
            joined=fills.merge(raw,on=['date','ticker'],suffixes=('_fill','_raw'),validate='many_to_one')
            self.assertEqual(len(fills),len(joined))
            self.assertTrue(np.allclose(joined.open_fill,joined.open_raw,rtol=0,atol=1e-8))
        decisions=pd.read_csv(base/'manager/decisions.csv')
        self.assertEqual(set(decisions.action),{'enter','hold','add','reduce','exit','abstain'})
        positions=pd.read_csv(base/'manager/positions.csv')
        self.assertLessEqual(positions.groupby('date').size().max(),10)

    def test_historical_artifacts_independent_reconstruction(self):
        base=ROOT/'artifacts'
        if not (base/'metrics.json').exists():self.skipTest('run historical replay first')
        for mode in ['manager','claude_approx','gemini_approx','grok_dev79_approx']:
            p=base/mode;daily=pd.read_csv(p/'daily.csv');fills=pd.read_csv(p/'fills.csv');positions=pd.read_csv(p/'positions.csv')
            groups={d:x for d,x in fills.groupby('date')};pg={d:x for d,x in positions.groupby('date')}
            cash=INITIAL;due=0.;shares={}
            for row in daily.itertuples():
                cash+=due;due=0.
                if row.date in groups:
                    for f in groups[row.date].itertuples():
                        self.assertLess(f.signal_date,f.date)
                        sign=1 if f.side=='BUY' else -1
                        self.assertAlmostEqual(f.price,f.open*(1+sign*SLIP),places=7)
                        self.assertAlmostEqual(f.fee,f.notional*FEE,places=7)
                        if sign==1:cash-=f.notional+f.fee
                        else:due+=f.notional-f.fee
                        shares[f.ticker]=shares.get(f.ticker,0)+sign*f.shares
                self.assertGreaterEqual(cash,-1e-6);self.assertAlmostEqual(cash,row.cash,places=5);self.assertAlmostEqual(due,row.unsettled,places=5)
                equity=0.
                if row.date in pg:
                    for pos in pg[row.date].itertuples():
                        self.assertAlmostEqual(shares[pos.ticker],pos.shares,places=6);equity+=pos.shares*pos.mark
                self.assertAlmostEqual(cash+due+equity,row.nav,places=5)
                self.assertTrue(all(q>=-1e-7 for q in shares.values()))
if __name__=='__main__':unittest.main(verbosity=2)
