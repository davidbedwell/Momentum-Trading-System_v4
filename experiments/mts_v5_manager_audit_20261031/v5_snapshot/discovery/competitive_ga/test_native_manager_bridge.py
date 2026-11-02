import unittest
from .native_manager_bridge import NATIVE_TO_MANAGER,proposal_from_native
class TestNativeBridge(unittest.TestCase):
 def test_all_native_actions_are_preserved(self):
  for action,expected in [('ENTER','ENTER'),('HOLD','HOLD'),('EXIT','EXIT'),('SCALE_IN','INCREASE'),('SCALE_OUT','REDUCE'),('REPLACE_CANDIDATE','PASS')]:
   self.assertEqual(NATIVE_TO_MANAGER[action],expected)
 def test_replacement_candidate_is_not_forced_exit(self):
  p=proposal_from_native('SYN','chrom','GA6','REPLACE_CANDIDATE',0.1)
  self.assertEqual(p.action,'PASS')
  self.assertFalse(p.calibrated)
 def test_no_fabricated_calibration(self):
  p=proposal_from_native('SYN','chrom','GA6','ENTER',0.1)
  self.assertFalse(p.calibrated)
  self.assertEqual(p.matured_samples,0)
if __name__=='__main__':unittest.main()
