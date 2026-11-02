import unittest
from datetime import date,timedelta
from discovery.competitive_ga.functional_niche_manager import Candidate,NicheObservation,run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

class ResidualShareTests(unittest.TestCase):
    def test_repeated_native_reductions_preserve_funded_ownership(self):
        def native(c,t,d,held):
            return NativeProposal(d,t,'GA7','a','REDUCE' if held else 'ENTER',held['weight']/2 if held else .1,0.,'net_return_fraction','source','snapshot','2026-10-28')
        days=[((date(2027,1,4)+timedelta(days=i)).isoformat(),{'AAA':Bar(100,100)}) for i in range(45)]
        r=run_slice(days,[Candidate('a','GA7',None,.02)],classify=lambda t,d:NicheObservation(d,'2026-10-28','test',()),eligible=lambda *a:True,native=native,max_sessions=45)
        # Below the former fill-book cutoff, this remains a real bank holding.
        self.assertGreater(r['nav'][-1][3]['AAA'],1e-10)
        self.assertLess(r['nav'][-1][3]['AAA'],1e-8)
        self.assertEqual(r['owners']['AAA'],('GA7','a'))
if __name__=='__main__':unittest.main()
