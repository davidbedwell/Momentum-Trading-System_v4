import unittest
import numpy as np
from Core.layered_ga.gen1_horizon_path_labels import labels,valid_checkpoints
class HorizonPathLabelsTest(unittest.TestCase):
 def test_horizon_one_has_no_checkpoint(self):
  self.assertEqual(valid_checkpoints(1),())
  with self.assertRaises(ValueError):labels(np.zeros((1,63)),np.zeros((1,63)),'LONG',1,1)
 def test_recovery_and_adverse_side(self):
  e=np.zeros((2,63));e[0,5]=-.04;e[0,6]=-.02;e[0,7]=.01
  e[1,5]=.04;e[1,6]=.02;e[1,7]=-.01
  c=np.zeros_like(e)
  self.assertEqual(labels(e,c,'LONG',10,5)['event'][0],-1)
  self.assertEqual(labels(e,c,'SHORT',10,5)['event'][1],-1)
 def test_terminal_specific_and_cost(self):
  e=np.zeros((1,63));e[0,9]=.03;e[0,19]=-.05
  c=np.zeros_like(e);c[0,9]=.01
  x=labels(e,c,'LONG',10,5)
  self.assertAlmostEqual(x['terminal_net'][0],.02)
  self.assertEqual(x['event'][0],1)
  self.assertNotEqual(x['terminal_net'][0],e[0,19])
 def test_missing_future_is_unavailable(self):
  e=np.zeros((1,63));e[0,6]=np.nan
  self.assertEqual(labels(e,np.zeros_like(e),'LONG',10,5)['event'][0],-2)
 def test_reject_nonoriginal_horizon(self):
  with self.assertRaises(ValueError):valid_checkpoints(6)
if __name__=='__main__':unittest.main()
