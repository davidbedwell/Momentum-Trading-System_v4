import unittest
import run as r
from dataclasses import replace
class Functional(unittest.TestCase):
    def mini(self,ev,priority=None,evidence=None,gap=.03,niche='synthetic'):
        days=[(d,{'SYN00':r.s1.Bar(100,100)}) for d in r.s1.DATES[:5]]
        c=r.patched.Candidate('SYN00','GA7',niche,.02,gap)
        def native(c,t,d,held):
            action='ENTER' if not held else ('EXIT' if d==days[3][0] else 'ADD')
            return r.NativeProposal(d,t,c.family,c.chromosome_id,action,0 if action=='EXIT' else .20,.1,'net_return_fraction','TEST','TEST','2029-01-01')
        return r.patched.run_slice(days,[c],max_sessions=5,classify=lambda t,d:r.patched.NicheObservation(d,'2029-01-01','TEST',(('synthetic',0),)),eligible=lambda *a:True,native=native,conditional_ev=lambda *a:ev,allocation_priority=priority,scaling_evidence=evidence,**r.s1.COSTS)
    def test_admission_separate(self):
        self.assertFalse(self.mini(-.01,lambda *a:999)['ledger'])
        self.assertTrue(self.mini(.01,lambda *a:-999)['ledger'])
    def test_niche(self):self.assertFalse(self.mini(.01,niche='unrelated')['ledger'])
    def test_invalid_priority(self):
        with self.assertRaises(ValueError):self.mini(.01,lambda *a:float('nan'))
    def test_scaling_and_native_exit(self):
        for cap,n,folds in ((.15,30,0),(.20,50,2)):
            evidence=lambda *a:r.ScaleEvidence(n,folds,True,.01,True,True,False)
            x=self.mini(.01,evidence=evidence)
            self.assertAlmostEqual(x['risk_audit'][0]['allowed'],.10)
            self.assertAlmostEqual(max(a['allowed'] for a in x['risk_audit']),cap)
            self.assertEqual(x['nav'][-1][3],{})
    def test_missing_evidence(self):
        self.assertLessEqual(max(a['allowed'] for a in self.mini(.01)['risk_audit']),.10)
    def test_scaling_risk(self):
        e=lambda *a:r.ScaleEvidence(50,2,True,.01,True,True,False)
        self.assertLess(max(a['allowed'] for a in self.mini(.01,evidence=e,gap=.24)['risk_audit']),.10)
    def test_same_ev_across_priority_variants(self):
        days,tapes,_=r.s1.generate(1101)
        callbacks=[r.callbacks(tapes['strong'],'strong',v,1101,days)[0] for v in ('ev','risk','cluster')]
        c=r.patched.Candidate('SYN00','GA7','synthetic',.02,.03)
        for d in r.s1.DATES:
            values=[k['conditional_ev'](c,'SYN00',d,None,()) for k in callbacks]
            self.assertEqual(values,[values[0]]*3)
            actions=[k['native'](c,'SYN00',d,None) for k in callbacks]
            self.assertEqual(actions,[actions[0]]*3)
    def test_insufficient_evidence_and_concentration(self):
        e=lambda *a:r.ScaleEvidence(29,2,True,.01,True,True,False)
        self.assertLessEqual(max(a['allowed'] for a in self.mini(.01,evidence=e)['risk_audit']),.10)
        from discovery.competitive_ga.progressive_scaling import allowed_target
        evidence=r.ScaleEvidence(50,2,True,.01,True,True,False)
        self.assertEqual(allowed_target(.10,.20,evidence,stop_distance=.02,gap_risk=.03,other_equity_risk=.02),0)
    def test_existing_policy(self):self.assertTrue(r.s1.policy_probes())
if __name__=='__main__':unittest.main()
