import os, sys, importlib.util, unittest
from pathlib import Path
import support as r
if os.getenv('PRE_FIX'):
    spec=importlib.util.spec_from_file_location('discovery.competitive_ga.prefx',Path(__file__).resolve().parent.parent/'stage2/functional_niche_manager.py')
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
else:m=r.patched

def fixture(cap,n=0,gap=.03,crowded=True):
    names=[f'SYN{j:02}' for j in range(10 if crowded else 2)]
    days=[(d,{t:r.s1.Bar(100,100) for t in names}) for d in r.s1.DATES[:6]]
    def native(c,t,d,h):
        i=r.s1.DATES.index(d);j=int(t[3:])
        if i==0 and j<(8 if crowded else 1):a,w='ENTER',.10
        elif i==1 and h:a,w='ADD',cap
        elif i==1 and not h:a,w='ENTER',.10
        elif i==3 and h:a,w='EXIT',0
        else:return None
        return r.NativeProposal(d,t,c.family,c.chromosome_id,a,w,.01,'net_return_fraction','TEST','TEST','2029-01-01')
    x=m.run_slice(days,[m.Candidate(t,'GA7','synthetic',.02,gap) for t in names],max_sessions=6,max_stocks=10,
        classify=lambda t,d:m.NicheObservation(d,'2029-01-01','TEST',(('synthetic',0),)),eligible=lambda *a:True,
        native=native,conditional_ev=lambda c,t,*a: .02 if int(t[3:])<8 else .01,
        scaling_evidence=lambda *a:r.ScaleEvidence(n,2,True,.01,True,True,False),**r.s1.COSTS)
    # Independent ledger reconstruction verifies fee debits, cash, settlement,
    # shares, NAV, no spending receivables and <=2% modeled admitted loss.
    r.s1.measure(x,days)
    assert all(nav[2]>=-1e-8 for nav in x['nav'])
    assert not x['nav'][-1][3]
    return x

class Regression(unittest.TestCase):
    def denied(self,cap):
        x=fixture(cap)
        buys=[f for f in x['ledger'] if f[0]==r.s1.DATES[2] and f[2]=='BUY']
        self.assertEqual({f[1] for f in buys},{'SYN08','SYN09'})
        # Both entrants receive all cash left after fees; denied adds spend zero.
        self.assertGreater(sum(f[3]*f[4] for f in buys),19000)
    def test_denied_15_releases_cash(self):self.denied(.15)
    def test_denied_20_releases_cash(self):self.denied(.20)
    def valid(self,cap,n):
        x=fixture(cap,n,crowded=False)
        a=next(a for a in x['risk_audit'] if a['date']==r.s1.DATES[2] and a['ticker']=='SYN00')
        self.assertAlmostEqual(a['allowed'],cap)
        self.assertTrue(any(f[0]==r.s1.DATES[2] and f[1]=='SYN00' and f[2]=='BUY' for f in x['ledger']))
    def test_valid_15(self):self.valid(.15,30)
    def test_valid_20(self):self.valid(.20,50)
    def test_risk_clip(self):
        x=fixture(.20,50,gap=.24,crowded=False)
        self.assertTrue(any(a.get('reservation',{}).get('risk_rejected') for a in x['decisions']))
        self.assertLessEqual(max(a['modeled_equity_loss'] for a in x['risk_audit']),.02+1e-12)
if __name__=='__main__':unittest.main()
