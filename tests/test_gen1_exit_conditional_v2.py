import unittest,numpy as np
from scripts.run_gen1_exit_conditional_v2_20261009 import simulate
class TestExitV2(unittest.TestCase):
 def test_future_open_cannot_trigger_same_open_exit(self):
  r=np.array([[0.0,-0.2,0.1,0.2]],float);c=np.zeros_like(r)
  z=np.array([1,-.05,.5,.5,0]);net,ix,last=simulate(r,c,z)
  self.assertEqual(int(ix[0]),2);self.assertAlmostEqual(float(net[0]),.1)
 def test_truncated_path_uses_last_valid_exit(self):
  r=np.array([[0.0,.01,.02,np.nan,np.nan]],float);c=np.zeros_like(r)
  net,ix,last=simulate(r,c,np.array([40,-.2,.5,.5,0]));self.assertEqual(int(ix[0]),2);self.assertEqual(int(last[0]),2)
 def test_invalid_first_exit_rejected(self):
  r=np.array([[np.nan,.01,.02]],float)
  with self.assertRaises(ValueError):simulate(r,np.zeros_like(r),np.array([1,-.2,.5,.5,0]))
if __name__=='__main__':unittest.main()
