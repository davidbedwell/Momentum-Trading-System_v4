"""Executable SYNTHETIC pipeline proofs; no market-performance claims."""
from copy import deepcopy
from dataclasses import replace
import unittest
import numpy as np
from .functionality_fixture import fixture, execute
from .execution import replay
from .alpaca_repair import reuse_benchmark
from pathlib import Path

class FunctionalityProof(unittest.TestCase):
    def test_pipeline_and_next_open_costs(self):
        p,g,m=fixture(); r=execute(p,g,m)
        entries=[f for f in r['fills'] if f['action']=='ENTRY']
        self.assertEqual({f['gene'] for f in entries[:2]}, {0,1})
        self.assertGreater(entries[0]['notional'],entries[1]['notional'])
        self.assertTrue(any(f['action']=='REDUCE' for f in r['fills']))
        self.assertTrue(any(f['action']=='EXIT' for f in r['fills']))
        self.assertTrue(any(e['decision']=='NO_TRADE' for e in r['events']))
        self.assertEqual(len(r['equity']),8)
        for f in r['fills']:
            ti=p.dates.get_loc(f['date']); self.assertEqual(f['decision_date'],str(p.dates[ti-1].date()))
            factor=1.0005 if f['action'] in ('ENTRY','ADD') else .9995
            self.assertAlmostEqual(f['price'],f['raw_open']*factor)
            self.assertGreater(f['cost'],0)
        for row in r['equity']:
            self.assertGreaterEqual(row['cash'],0)
            self.assertAlmostEqual(row['nav'],row['cash']+row['unsettled']+row['holdings'])
            self.assertLessEqual(row['drawdown'],.08)
        self.assertLess(r['audit']['max_identity_error'],1e-5)
        self.assertGreater(r['equity'][4]['unsettled'],0)

    def test_fallback_same_gates(self):
        for fallback in (False,True):
            for gate in ('membership','screen','threshold','cash','risk','sector','slots'):
                p,g,m=fixture()
                if fallback: g=[g[2]]
                if gate=='membership': p.eligible[:]=False
                if gate=='screen': p.screen_mask[:]=False
                if gate=='threshold': g=[replace(x,threshold=3) for x in g]
                if gate=='cash': m=replace(m,reserve=1)
                if gate=='risk': m=replace(m,risk_cap=0)
                if gate=='sector': m=replace(m,sector_cap=0)
                if gate=='slots': m=replace(m,slots=0)
                self.assertEqual(execute(p,g,m)['fills'],[],(fallback,gate))
        p,g,m=fixture(); p.features['momentum'][:]=0
        self.assertTrue(all(f['gene']==2 for f in execute(p,g,m)['fills']))

    def test_no_lookahead_and_counterfactual(self):
        p,g,m=fixture(); base=execute(p,g,m)
        changed=deepcopy(p)
        changed.open[4:]*=1.01; changed.close[4:]*=1.01
        for a in changed.features.values(): a[4:]=10
        changed.niche[4:]=2
        later=execute(changed,g,m)
        self.assertEqual(base['events'][:4],later['events'][:4])
        self.assertEqual([f for f in base['fills'] if f['date']<str(p.dates[4].date())],
                         [f for f in later['fills'] if f['date']<str(p.dates[4].date())])
        cf=execute(p,[g[2]],m)
        self.assertNotEqual(base['metrics']['final_nav'],cf['metrics']['final_nav'])
        # Eligibility revoked at execution prevents a previously queued entry.
        p.eligible[1:]=False
        self.assertEqual(execute(p,g,m)['fills'],[])

    def test_correlation_gate_for_specialists_and_fallback(self):
        for fallback in (False,True):
            p,g,m=fixture()
            p.dates=__import__('pandas').bdate_range('2030-01-07',periods=30)
            for name in ('open','close','dividends','niche','eligible','screen_mask','screen_score'):
                setattr(p,name,np.tile(getattr(p,name)[0],(30,1)))
            p.breadth=np.zeros(30)
            p.returns=np.repeat(np.sin(np.arange(30))[:,None]*.01,2,axis=1)
            p.features={k:np.zeros((30,2)) for k in p.features}
            p.features['momentum'][24]=1
            p.features['volume'][24]=2
            if fallback: g=[g[2]]
            r=execute(p,g,replace(m,reserve=0))
            self.assertGreater(r['audit']['correlation_rejections'],0)
            self.assertEqual(len([f for f in r['fills'] if f['action']=='ENTRY']),1)

    def test_ceiling_breach_fails_explicitly(self):
        p,g,m=fixture(); m=replace(m,reserve=0)
        p.open[2:]=1; p.close[2:]=1
        with self.assertRaisesRegex(RuntimeError,'PORTFOLIO_DRAWDOWN_CEILING_BREACHED'):
            execute(p,g,m)

    def test_cached_qqq_is_present_and_hash_verified(self):
        r=reuse_benchmark(Path(__file__).parent/'artifacts/alpaca_repair_live_batch_20261029')
        self.assertEqual(r['rows'],1003)
        self.assertEqual(r['status'],'VENDOR_RAW_ONLY_NOT_PIT_CERTIFIED')

if __name__=='__main__': unittest.main()
