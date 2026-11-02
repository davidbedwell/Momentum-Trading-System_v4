import unittest
from dataclasses import replace
import numpy as np
import pandas as pd
from .execution import Panel, Gene, Manager, replay, load_panel, scores, metrics

class AccountingTests(unittest.TestCase):
    def panel(self):
        n=14
        c=np.array([100,100,102,104,103,98,97,99,101,102,100,99,101,102.],dtype=float)[:,None]
        o=c.copy()
        o[1:]=c[:-1]
        r=np.r_[0,(c[1:,0]/c[:-1,0]-1)][:,None]
        f={'trend':np.ones_like(c),'momentum':np.ones_like(c)}
        f['trend'][7:9]=-1
        return Panel(pd.bdate_range('2022-01-03',periods=n),['X'],o,c,np.zeros_like(c),r,f,np.ones_like(c,dtype=int),np.ones(n))
    def test_execution_conservation_dividend_settlement(self):
        p=self.panel()
        p.dividends[3]=1
        r=replay(p,[Gene('trend',weight=.06,add=.01,hold_sessions=4)],Manager(),'2022','2023',True)
        self.assertEqual(r['fills'][0]['date'],str(p.dates[1].date()))
        self.assertAlmostEqual(r['fills'][0]['price'],p.open[1,0]*1.0005)
        self.assertLess(r['audit']['max_identity_error'],1e-6)
        self.assertGreater(r['audit']['min_cash'],0)
        self.assertTrue(any(x['unsettled']>0 for x in r['equity']))
        self.assertTrue(any(x['action']=='ADD' for x in r['fills']))
        self.assertTrue(any(x['action']=='EXIT' for x in r['fills']))
        self.assertGreater(r['metrics']['costs'],0)
        for row in r['equity']:
            self.assertAlmostEqual(row['nav'],row['cash']+row['holdings']+row['unsettled'])
    def test_future_values_cannot_change_past_fills(self):
        p=self.panel()
        a=replay(p,[Gene('trend')],Manager(),'2022','2023',True)
        p.close[10:]*=10
        p.open[10:]*=10
        b=replay(p,[Gene('trend')],Manager(),'2022','2023',True)
        cutoff=str(p.dates[9].date())
        self.assertEqual([x for x in a['fills'] if x['date']<=cutoff],[x for x in b['fills'] if x['date']<=cutoff])
    def test_abstain_and_no_cash_creation(self):
        p=self.panel()
        r=replay(p,[Gene('trend',threshold=100)],Manager(),'2022','2023',True)
        self.assertEqual(r['metrics']['final_nav'],100000)
        self.assertEqual(r['fills'],[])
        self.assertGreater(r['audit']['abstentions'],0)
    def test_drawdown_includes_initial_capital(self):
        m=metrics([99000,98000],[],[0,0],2)
        self.assertAlmostEqual(m['max_drawdown'],.02)
        self.assertTrue(m['feasible'])  # 2% absolute MDD passes; no Calmar gate in GA9

class RealDataCausalityTests(unittest.TestCase):
    def test_feature_prefix_matches_and_no_missing_listing_fill(self):
        # Independent truncated source checks rolling, EWMA, ranks and niche assignment.
        import tempfile
        from pathlib import Path
        raw=Path('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet')
        d=pd.read_parquet(raw)
        d=d[(d.date>='2022-01-01') & (d.date<'2023-01-01')]
        with tempfile.TemporaryDirectory() as root:
            a,b=Path(root)/'a.parquet',Path(root)/'b.parquet'
            d.to_parquet(a)
            d[d.date<'2022-09-01'].to_parquet(b)
            full,_=load_panel(a)
            prefix,_=load_panel(b)
            for k in full.features:
                np.testing.assert_allclose(full.features[k][:len(prefix.dates)],prefix.features[k],equal_nan=True)
            np.testing.assert_array_equal(full.niche[:len(prefix.dates)],prefix.niche)

if __name__=='__main__': unittest.main()

class DividendAndGrammarTests(unittest.TestCase):
    def test_dividend_receivable_cannot_be_spent_without_payment_date(self):
        p=AccountingTests().panel()
        base=replay(p,[Gene('trend',add=100,hold_sessions=100)],Manager(),'2022','2023',True)
        p.dividends[3]=10
        paid=replay(p,[Gene('trend',add=100,hold_sessions=100)],Manager(),'2022','2023',True)
        # Ex-date distribution increases NAV / receivables but not settled cash.
        self.assertAlmostEqual(base['equity'][3]['cash'],paid['equity'][3]['cash'])
        self.assertGreater(paid['equity'][3]['unsettled'],base['equity'][3]['unsettled'])
        self.assertGreater(paid['equity'][3]['nav'],base['equity'][3]['nav'])
    def test_nested_tree_and_independent_native_exit(self):
        from .execution import evaluate_tree
        p=AccountingTests().panel()
        tree=('and','trend',('or','momentum','trend'))
        self.assertEqual(evaluate_tree(p.features,tree)[0,0],1)
        g=Gene('momentum',exit_family='trend',hold_sessions=100,add=100)
        r=replay(p,[g],Manager(),'2022','2023',True)
        self.assertTrue(any(x['reason']=='native_exit' for x in r['fills']))

class GapPolicyTests(unittest.TestCase):
    def test_loss_trigger_fills_next_open_with_gap(self):
        p=AccountingTests().panel()
        p.close[2]=97
        p.open[3]=90
        r=replay(p,[Gene('trend',add=100,hold_sessions=100)],Manager(),'2022','2023',True)
        exits=[x for x in r['fills'] if x['reason']=='loss_policy']
        self.assertTrue(exits)
        self.assertEqual(exits[0]['date'],str(p.dates[3].date()))
        self.assertAlmostEqual(exits[0]['price'],90*.9995)

class SampleUniverseTests(unittest.TestCase):
    def test_sample_selection_precedes_ranks_and_gev_pit_mask(self):
        raw='/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet'
        sample=['ACN','COST','GEV']
        full,_=load_panel(raw,end='2024-05-01',sample=sample)
        prefix,_=load_panel(raw,end='2024-04-02',sample=sample)
        self.assertEqual(full.symbols,sorted(sample))
        j=full.symbols.index('GEV')
        self.assertTrue(np.isnan(prefix.close[:,j]).all())
        for k in full.features:
            np.testing.assert_allclose(full.features[k][:len(prefix.dates)],prefix.features[k],equal_nan=True)
        # With two listed sample members, PIT relative-strength ranks have only two values.
        ranks=prefix.features['relative_strength'][-1]
        np.testing.assert_allclose(sorted(ranks[np.isfinite(ranks)]),[0.,1.])
