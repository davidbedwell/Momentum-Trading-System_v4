import unittest
import numpy as np
import pandas as pd
from study import classify,ROOT,OUT,MODES,load_panel,SPY

class StudyTests(unittest.TestCase):
    def test_category_prefix_and_decision_bar_invariance(self):
        _,d=load_panel();spy=pd.read_parquet(SPY).set_index('date').close
        before,_=classify(d,spy);cut=pd.Timestamp('2018-01-02');n=d['close'].index.get_loc(cut)
        altered={k:v.copy() for k,v in d.items()}
        for v in altered.values():v.iloc[n:]*=1.7
        ss=spy.copy();ss.loc[cut:]*=1.5
        after,_=classify(altered,ss)
        pd.testing.assert_frame_equal(before.iloc[:n+1],after.iloc[:n+1])
        short,_=classify({k:v.iloc[:n] for k,v in d.items()},spy.iloc[:spy.index.get_loc(cut)])
        pd.testing.assert_frame_equal(before.iloc[:n],short)
        self.assertEqual(set(before.stack().unique()),{'unknown','acceleration','uptrend','consolidation','deterioration','reversal'})
    def test_missing_prior_bar_makes_unknown(self):
        _,d=load_panel();spy=pd.read_parquet(SPY).set_index('date').close
        d['volume'].iloc[300:301,0]=np.nan;st,_=classify(d,spy)
        self.assertEqual(st.iloc[301,0],'unknown')
        self.assertEqual(st.iloc[351,0],'unknown')
    def test_common_matching_and_hold_identity(self):
        baseline=None
        for mode in MODES:
            x=pd.read_csv(OUT/f'{mode}_opportunity_ledger.csv.gz',parse_dates=['date','execution_date','horizon_end','state_asof'])
            self.assertTrue((x.state_asof<x.date).all())
            g=x[x.valid]
            self.assertTrue((g.date<g.execution_date).all());self.assertTrue((g.execution_date<g.horizon_end).all())
            self.assertTrue((g.horizon_end<=pd.Timestamp('2026-09-14')).all())
            self.assertFalse(((g.segment=='discovery')&(g.horizon_end>pd.Timestamp('2017-12-29'))).any())
            self.assertTrue(np.allclose(g.incremental_pnl,g.delta*(g.end_open-g.execution_open)-g.fee-g.slippage_dollars))
            self.assertTrue(np.allclose(g.local_net_pnl-g.hold_pnl,g.incremental_pnl))
            z=g[g.delta==0];self.assertTrue(np.allclose(z.incremental_pnl,0))
            keys=x[['date','ticker','category','valid']]
            if baseline is None:baseline=keys
            else:pd.testing.assert_frame_equal(baseline,keys)
    def test_fill_and_category_reconciliation(self):
        summary=pd.read_csv(OUT/'category_summary.csv')
        for mode in MODES:
            fa=pd.read_csv(OUT/f'{mode}_fill_attribution.csv.gz');daily=pd.read_csv(OUT/mode/'daily.csv')
            self.assertAlmostEqual(fa.fee.sum(),daily.cumulative_fees.iloc[-1],places=6)
            self.assertAlmostEqual(fa.realized_pnl.sum(),daily.realized_pnl.iloc[-1],places=6)
            self.assertAlmostEqual(summary.loc[summary.policy==mode,'fees_all_fills'].sum(),fa.fee.sum(),places=6)
            original=ROOT.parent/'dev79_four_policy_comparison_20261101/artifacts'/mode
            for name in ['daily','fills','decisions']:
                pd.testing.assert_frame_equal(pd.read_csv(OUT/mode/f'{name}.csv'),pd.read_csv(original/f'{name}.csv'))
if __name__=='__main__':unittest.main()
