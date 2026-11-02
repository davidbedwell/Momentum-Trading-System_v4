"""Focused leakage, abstention, execution-policy tests; no full portfolios."""
import unittest
from dataclasses import replace
import experiment as e

class Focused(unittest.TestCase):
    def test_absolute_tiers_and_abstain(self):
        self.assertEqual([e.tier(v) for v in (-.01,-.004,0,.004,.01)],list(e.TIERS))
        self.assertEqual(e.infer(.004,.003,70,40),'UNKNOWN')
        self.assertEqual(e.infer(.01,.001,19,40),'UNKNOWN')
        self.assertEqual(e.infer(.01,.001,70,40),'GREAT')
    def test_fit_excludes_current_unmatured_holdout(self):
        days,f,p,t=e.generate(2101,'learnable');before=e.fit(days,f)
        changed=list(days);changed[124:]=[(d,{}) for d,_ in days[124:]]
        changedf=list(f);changedf[122:]=[[] for _ in f[122:]]
        self.assertEqual(before,e.fit(changed,changedf))
    def test_maturity_alignment_and_exact_cost(self):
        days,f,p,t=e.generate(2101,'learnable')
        self.assertAlmostEqual(e.observed(days,0,0),days[2][1]['SYN00'].open*.999*.9995/(days[1][1]['SYN00'].open*1.001*1.0005)-1)
    def test_point_in_time_callbacks_do_not_read_forward_rows(self):
        days,f,p,t=e.generate(2101,'misleading');cells=e.fit(days,f)
        cb=e.callbacks(f,p,cells,'tier10',days);d=e.s.DATES[126];c=e.m.Candidate('SYN00','GA7','synthetic',.02,.03)
        before=cb['native'](c,'SYN00',d,None)
        f[127:]=[[] for _ in f[127:]];p[127:]=[[] for _ in p[127:]]
        self.assertEqual(before,cb['native'](c,'SYN00',d,None))
    def test_entire_candidate_cost_inclusive_per_trade_risk(self):
        ev=e.r.ScaleEvidence(50,2,True,.01,True,True,False)
        for gap,target in ((.24,.02/.243),(.03,.20)):
            x=e.k.Replay(cash=95000,shares={'A':50},**e.s.COSTS)
            x.pending=[e.k.Signal('A','GA7','a',.20,1,ev,.02,gap,.9)]
            x.day('2030-01-02',{'A':e.k.Bar(100,100)})
            self.assertAlmostEqual(x.shares['A']*100/100000,target)
            self.assertLessEqual(x.risk_audit[-1]['modeled_equity_loss'],.02+1e-12)
    def test_tplus1(self):
        x=e.k.Replay(cash=0,shares={'A':1000},high_water=100000,settlement_sessions=1,**e.s.COSTS)
        bars={t:e.k.Bar(100,100) for t in ('A','B')}
        x.pending=[e.k.Signal('A','GA7','a',0),e.k.Signal('B','GA7','b',.1,1,None,.02,.03)]
        x.day('2030-01-02',bars);self.assertFalse(x.shares);self.assertEqual(x.cash,0);self.assertTrue(x.unsettled)
        x.pending=[e.k.Signal('B','GA7','b',.1,1,None,.02,.03)]
        x.day('2030-01-03',bars);self.assertIn('B',x.shares)
    def test_mdd_latch_keeps_exits(self):
        x=e.k.Replay(cash=20000,shares={'A':800},high_water=100000,**e.s.COSTS)
        bars={'A':e.k.Bar(50,50),'B':e.k.Bar(100,100)}
        x.pending=[e.k.Signal('B','GA7','b',.1,1,None,.02,.03)];x.day('2030-01-02',bars)
        self.assertTrue(x.admission_halted);self.assertNotIn('B',x.shares)
        x.pending=[e.k.Signal('A','GA7','a',0)];x.day('2030-01-03',bars);self.assertFalse(x.shares)
    def test_denied_add_releases_reservation(self):
        names=[f'SYN{j:02}' for j in range(10)];days=[(d,{t:e.k.Bar(100,100) for t in names}) for d in e.s.DATES[:5]]
        denied=e.r.ScaleEvidence(0,0,False,0,False,False,False)
        def native(c,t,d,h):
            i=e.s.DATES.index(d);j=int(t[3:])
            if i==0 and j<8:ac,w='ENTER',.1
            elif i==1:ac,w=('ADD',.2) if h else ('ENTER',.1)
            else:return None
            return e.r.NativeProposal(d,t,c.family,c.chromosome_id,ac,w,.02,'net_return_fraction','TEST','TEST','2029-01-01')
        result=e.m.run_slice(days,[e.m.Candidate(t,'GA7','synthetic',.02,.03) for t in names],max_sessions=5,max_stocks=10,**e.s.COSTS,classify=lambda t,d:e.m.NicheObservation(d,'2029-01-01','TEST',(('synthetic',0),)),eligible=lambda c,t,d:c.chromosome_id==t,native=native,conditional_ev=lambda *args:.02,scaling_evidence=lambda *args:denied)
        buys=[f for f in result['ledger'] if f[0]==e.s.DATES[2] and f[2]=='BUY']
        self.assertEqual({f[1] for f in buys},{'SYN08','SYN09'})
        e.s.measure(result,days)
if __name__=='__main__':unittest.main(verbosity=2)
