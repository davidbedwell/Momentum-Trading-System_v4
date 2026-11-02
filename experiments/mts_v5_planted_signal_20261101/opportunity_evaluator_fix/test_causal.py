import unittest
import experiment as e

class Causal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.days,cls.f,cls.p,_=e.generate(2101,'reversal')
        cls.states,cls.ledger,cls.alarms=e.causal_predictions(cls.days,cls.f,cls.p)
    def test_maturation_and_all_eligible(self):
        self.assertEqual(len(self.ledger),250*24)
        for z in self.ledger:
            if z['available_index'] is not None:self.assertGreater(z['available_index'],z['maturity_index'])
        self.assertEqual(sum(z['missingness']=='PENDING' for z in self.ledger),24)
    def test_future_outcomes_and_holdout_isolation(self):
        changed=list(self.days);changed[126:]=[(d,{}) for d,b in changed[126:]]
        states,ledger,alarms=e.causal_predictions(changed,self.f,self.p)
        self.assertEqual(states[:127],self.states[:127])
        self.assertTrue(any(z['missingness']=='MISSING_BARS' for z in ledger))
    def test_future_features(self):
        f=[list(v) for v in self.f];p=[list(v) for v in self.p]
        f[127:]=[[0]*24 for _ in f[127:]];p[127:]=[[99]*24 for _ in p[127:]]
        states,_,_=e.causal_predictions(self.days,f,p)
        self.assertEqual(states[:128],self.states[:128])
    def test_reversal_detector_quarantines_after_observable_lag(self):
        hits=[z for z in self.alarms if z['index']>=126]
        self.assertTrue(hits)
        first=hits[0]['index'];self.assertGreaterEqual(first,129)
        self.assertTrue(all(z['label']=='UNKNOWN' for z in self.states[first]))
    def test_calibration_is_absolute_and_unknown_distinct(self):
        self.assertEqual(e.infer(0,.001,40,20),'AVERAGE')
        self.assertEqual(e.infer(0,.003,40,20),'UNKNOWN')
        self.assertTrue(all(z['label']=='UNKNOWN' for z in self.states[20]))
        self.assertTrue(all(z['radius']>=0 for row in self.states for z in row))
    def test_cost_accounting_in_ledger(self):
        z=self.ledger[0]
        self.assertAlmostEqual(z['realized_net'],e.observed(self.days,0,0))
        self.assertEqual(z['costs'],e.s.COSTS)

if __name__=='__main__':unittest.main(verbosity=2)
