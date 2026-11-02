"""Regression checks for independently managed, fill-derived native shadows."""
import unittest
from types import SimpleNamespace
from discovery.competitive_ga.functional_niche_manager import Candidate,NicheObservation,run_slice
from discovery.competitive_ga.native_shadow_trade_book import ShadowBook
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

class NativeShadowStateTests(unittest.TestCase):
    def test_native_hysteresis_controller_preserves_true_distances(self):
        obs=NicheObservation('2027-01-04','2026-10-28','native',
          (('A',.50),('B',.48)),'A')
        self.assertEqual(obs.controlling('2027-01-04'),'A')
        self.assertEqual(dict(obs.matches)['B'],.48)
        with self.assertRaises(ValueError):
            NicheObservation('2027-01-04','2026-10-28','native',(('B',.48),),'A').controlling('2027-01-04')

    def test_funded_owner_shadow_receives_independent_full_held_state(self):
        observed=[]
        def native(c,t,d,held):
            if held is not None:observed.append((d,held.copy()))
            action='ENTER' if held is None else ('EXIT' if d=='2027-01-06' else 'HOLD')
            return NativeProposal(d,t,'GA6','frozen',action,0. if action=='EXIT' else .1,
              0.,'entry_equity_fraction','source','snapshot','2026-10-28')
        result=run_slice([(d,{'AAA':Bar(p,p)}) for d,p in
          [('2027-01-04',100),('2027-01-05',110),('2027-01-06',120),('2027-01-07',115)]],
          [Candidate('frozen','GA6',None,.02)],
          classify=lambda t,d:NicheObservation(d,'2026-10-28','test',()),
          eligible=lambda *a:True,native=native,native_shadow=True)
        funded=[h for d,h in observed if d=='2027-01-06' and not h.get('shadow')]
        shadow=[h for d,h in observed if d=='2027-01-06' and h.get('shadow')]
        self.assertEqual(len(funded),1);self.assertEqual(len(shadow),1)
        self.assertGreater(funded[0]['shares'],shadow[0]['shares']*1000)
        self.assertEqual(shadow[0]['peak'],120)
        self.assertEqual(shadow[0]['entry'],110)
        self.assertEqual(shadow[0]['entry_session'],1)
        self.assertEqual(result['native_shadow_outcomes'][0].maturity_session,3)
        self.assertEqual(result['shadow_method'],'NATIVE_POSITION_EXIT_REPLAY')
        # Exit decided at Jan 6 close fills at Jan 7 open, never same close.
        self.assertEqual([x[0] for x in result['ledger']],['2027-01-05','2027-01-07'])

    def test_shadow_add_updates_native_entry_price_from_own_fills(self):
        b=ShadowBook(fee=0.)
        def signal(action,w):
            return SimpleNamespace(family='GA6',chromosome_id='x',ticker='AAA',action=action,target_weight=w)
        b.close_session(0,[signal('ENTER',.1)])
        b.open_session(1,{'AAA':Bar(100,100)})
        old=b.positions['GA6','x','AAA']['units']
        b.close_session(1,[signal('ADD',.2)])
        b.open_session(2,{'AAA':Bar(120,120)})
        pos=b.positions['GA6','x','AAA']
        expected=(old*100+(pos['units']-old)*120)/pos['units']
        self.assertAlmostEqual(pos['entry_price'],expected)
        self.assertEqual(pos['entry_session'],1)

if __name__=='__main__':unittest.main()
