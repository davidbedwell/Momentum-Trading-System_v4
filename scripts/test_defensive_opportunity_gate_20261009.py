import unittest
from Core.layered_ga.defensive_opportunity_gate import crash_transition_actions,evaluate_entry

BASE=dict(defensive=True,direction='LONG',planned_horizon=3,max_defensive_horizon=5,validated_defensive_strategy=True,independent_signal_pass=True,risk_pass=True)
class GateTests(unittest.TestCase):
 def check(self,expected,**kw):
  args={**BASE,**kw};self.assertEqual(evaluate_entry(**args).permitted,expected)
 def test_cash_first(self):self.assertEqual(crash_transition_actions(True),('cancel_conflicting_entries','liquidate_equity_to_cash'))
 def test_no_crash(self):self.assertEqual(crash_transition_actions(False),())
 def test_both_directions(self):self.check(True);self.check(True,direction='SHORT',borrow_available=True,quoted_borrow_rate=.06)
 def test_no_arbitrary_cutoff(self):self.check(False,max_defensive_horizon=None)
 def test_horizon_bound(self):self.check(False,planned_horizon=6)
 def test_not_validated(self):self.check(False,validated_defensive_strategy=False)
 def test_no_signal(self):self.check(False,independent_signal_pass=False)
 def test_no_risk(self):self.check(False,risk_pass=False)
 def test_short_fee_cap(self):self.check(False,direction='SHORT',borrow_available=True,quoted_borrow_rate=.061)
 def test_short_unavailable(self):self.check(False,direction='SHORT',borrow_available=False,quoted_borrow_rate=.03)
 def test_repeat_allowed_after_new_signal(self):
  for _ in range(3):self.check(True,planned_horizon=2)
 def test_normal_not_subject_to_defensive_horizon(self):self.check(True,defensive=False,max_defensive_horizon=None,planned_horizon=63)
 def test_invalid_horizon(self):self.check(False,planned_horizon=0)
if __name__=='__main__':unittest.main()
