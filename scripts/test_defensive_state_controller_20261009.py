import unittest
from Core.layered_ga.defensive_state_controller import DefensiveStateController

ENTRY=dict(direction='LONG',planned_horizon=2,max_defensive_horizon=3,validated_defensive_strategy=True,independent_signal_pass=True,risk_pass=True)
class StateTests(unittest.TestCase):
 def test_cash_first_then_eligible(self):
  c=DefensiveStateController();self.assertEqual(len(c.update(abc_crash_detected=True,r1_confirmed=False)),2)
  self.assertEqual(c.assess(**ENTRY).reason,'cash_transition_unconfirmed')
  c.acknowledge_cash_transition(cancellations_confirmed=True,liquidations_confirmed=False);self.assertFalse(c.assess(**ENTRY).permitted)
  c.acknowledge_cash_transition(cancellations_confirmed=True,liquidations_confirmed=True);self.assertTrue(c.assess(**ENTRY).permitted)
 def test_crash_priority_and_r1(self):
  c=DefensiveStateController();c.update(abc_crash_detected=True,r1_confirmed=True);self.assertTrue(c.defensive)
  c.update(abc_crash_detected=False,r1_confirmed=True);self.assertFalse(c.defensive)
 def test_repeat_does_not_reliquidate(self):
  c=DefensiveStateController();c.update(abc_crash_detected=True,r1_confirmed=False);self.assertEqual(c.update(abc_crash_detected=True,r1_confirmed=False),())
 def test_unfrozen_horizon_still_blocks(self):
  c=DefensiveStateController();c.update(abc_crash_detected=True,r1_confirmed=False);c.acknowledge_cash_transition(cancellations_confirmed=True,liquidations_confirmed=True)
  self.assertEqual(c.assess(**{**ENTRY,'max_defensive_horizon':None}).reason,'unfrozen_defensive_horizon')
if __name__=='__main__':unittest.main()

class ExclusiveBoundaryTests(unittest.TestCase):
 def test_no_timeout_until_r1(self):
  c=DefensiveStateController();c.update(abc_crash_detected=True,r1_confirmed=False)
  for _ in range(1000):c.update(abc_crash_detected=False,r1_confirmed=False)
  self.assertTrue(c.defensive)
  c.update(abc_crash_detected=False,r1_confirmed=True)
  self.assertFalse(c.defensive)
 def test_repeated_abc_does_not_end_crash(self):
  c=DefensiveStateController();c.update(abc_crash_detected=True,r1_confirmed=False)
  for _ in range(30):c.update(abc_crash_detected=True,r1_confirmed=True)
  self.assertTrue(c.defensive)
