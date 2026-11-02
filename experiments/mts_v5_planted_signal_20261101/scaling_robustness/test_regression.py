"""Bounded regression tests. Fixed synthetic fixtures, no parameter search."""
import unittest
from dataclasses import replace
import audit as a
from discovery.competitive_ga.progressive_scaling import ScaleEvidence,allowed_target
from engines.portfolio_replay.kernel import Replay as OldReplay,Signal,Bar

E=ScaleEvidence(50,2,True,.01,True,True,False)

class Regression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (cls.old,cls.new),cls.kernel=a.prepare()

    def kernel_fixture(self,klass,gap=.03,other=.03):
        x=klass(cash=95000,shares={'A':50},fees=.0005,spread=.001,slippage=.0003,impact=.0002)
        x.pending=[Signal('A','GA7','a',.20,1,E,.02,gap,other)]
        x.day('2030-01-02',{'A':Bar(100,100)})
        return x

    def test_other_holdings_do_not_consume_candidate_budget(self):
        old=self.kernel_fixture(OldReplay);new=self.kernel_fixture(self.kernel.Replay)
        self.assertFalse(old.ledger)
        self.assertAlmostEqual(new.shares['A']*100/100000,.20)
        self.assertLessEqual(new.risk_audit[-1]['modeled_equity_loss'],.02)

    def test_candidate_entire_position_cost_inclusive_clip(self):
        x=self.kernel_fixture(self.kernel.Replay,gap=.24)
        self.assertAlmostEqual(x.risk_audit[-1]['allowed'],.02/.243)
        self.assertLessEqual(x.risk_audit[-1]['modeled_equity_loss'],.02+1e-12)
        self.assertLess(x.shares['A']*100/100000,.10)

    def manager_fixture(self,m,target):
        names=[f'SYN{j:02}' for j in range(10)]
        days=[(d,{t:Bar(100,100) for t in names}) for d in a.r.s1.DATES[:6]]
        def native(c,t,d,h):
            i=a.r.s1.DATES.index(d);j=int(t[3:])
            if i==0 and j<8:action,w='ENTER',.10
            elif i==1 and h:action,w='ADD',target
            elif i==3 and h:action,w='EXIT',0
            else:return None
            return a.r.NativeProposal(d,t,c.family,c.chromosome_id,action,w,.02,'net_return_fraction','TEST','TEST','2029-01-01')
        kw=dict(classify=lambda t,d:m.NicheObservation(d,'2029-01-01','TEST',(('synthetic',0),)),eligible=lambda *args:True,native=native,conditional_ev=lambda *args:.02,scaling_evidence=lambda *args:E)
        x=m.run_slice(days,[m.Candidate(t,'GA7','synthetic',.02,.03) for t in names],max_sessions=6,max_stocks=10,**a.r.s1.COSTS,**kw)
        a.r.s1.measure(x,days)
        self.assertTrue(all(z[2]>=-1e-8 for z in x['nav']))
        self.assertFalse(x['nav'][-1][3])
        return x

    def test_crowded_15_and_20_original_blocked_corrected_funded(self):
        for target in (.15,.20):
            old=self.manager_fixture(self.old,target);new=self.manager_fixture(self.new,target)
            d=a.r.s1.DATES[2]
            self.assertFalse(any(f[0]==d and f[2]=='BUY' for f in old['ledger']))
            self.assertTrue(any(f[0]==d and f[2]=='BUY' for f in new['ledger']))
            first=next(z for z in new['risk_audit'] if z['date']==d)
            self.assertAlmostEqual(first['allowed'],target)

    def test_denied_evidence_cannot_reserve_cash(self):
        # Pure policy boundary; manager's denied-reservation regressions also run separately.
        for n,target,want in [(29,.15,.10),(30,.15,.15),(49,.20,.15),(50,.20,.20)]:
            ev=replace(E,matured_trades=n)
            self.assertAlmostEqual(allowed_target(.10,target,ev,stop_distance=.02,gap_risk=.03),want)
        self.assertAlmostEqual(allowed_target(.10,.20,replace(E,position_profitable=False),stop_distance=.02,gap_risk=.03),.10)
        self.assertAlmostEqual(allowed_target(.10,.20,replace(E,forward_folds=1),stop_distance=.02,gap_risk=.03),.15)
        self.assertFalse(E.independent_confirmation) # This flag is NOT required by current 15/20 policy.

    def test_denied_evidence_releases_cash_in_corrected_manager(self):
        import test_reservation as prior
        saved=prior.m
        try:
            prior.m=self.new
            for cap in (.15,.20):
                x=prior.fixture(cap)
                buys=[f for f in x['ledger'] if f[0]==a.r.s1.DATES[2] and f[2]=='BUY']
                self.assertEqual({f[1] for f in buys},{'SYN08','SYN09'})
                self.assertGreater(sum(f[3]*f[4] for f in buys),19000)
        finally:prior.m=saved

    def test_unsettled_sales_still_unavailable(self):
        x=self.kernel.Replay(cash=0,shares={'A':1000},high_water=100000,settlement_sessions=1,**a.r.s1.COSTS)
        bars={t:Bar(100,100) for t in ('A','B')}
        x.pending=[Signal('A','GA7','a',0),Signal('B','GA7','b',.10,1,None,.02,.03)]
        x.day('2030-01-02',bars)
        self.assertFalse(x.shares);self.assertEqual(x.cash,0);self.assertTrue(x.unsettled)
        x.pending=[Signal('B','GA7','b',.10,1,None,.02,.03)]
        x.day('2030-01-03',bars);self.assertIn('B',x.shares)

    def test_mdd_latch_still_preserves_exit(self):
        x=self.kernel.Replay(cash=20000,shares={'A':800},high_water=100000,**a.r.s1.COSTS)
        bars={'A':Bar(50,50),'B':Bar(100,100)}
        x.pending=[Signal('B','GA7','b',.1,1,None,.02,.03)];x.day('2030-01-02',bars)
        self.assertTrue(x.admission_halted);self.assertNotIn('B',x.shares)
        x.pending=[Signal('A','GA7','a',0)];x.day('2030-01-03',bars);self.assertFalse(x.shares)

if __name__=='__main__':unittest.main(verbosity=2)
