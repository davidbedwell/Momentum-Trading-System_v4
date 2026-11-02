import unittest
from .horizons_stress_governance import require_certified,status
class TestStressGate(unittest.TestCase):
 def test_research_allowed(self):self.assertTrue(require_certified('research'))
 def test_trading_blocked(self):
  with self.assertRaisesRegex(RuntimeError,'availability timestamps'):require_certified('trading')
 def test_pit_blocked(self):
  with self.assertRaises(RuntimeError):require_certified('pit_validation')
 def test_uncertified(self):self.assertFalse(status().live_or_pit_certified)
if __name__=='__main__':unittest.main()
