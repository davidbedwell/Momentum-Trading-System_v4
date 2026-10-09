import unittest,numpy as np
from Core.layered_ga.gen1_path_matching import matched_failure_scores,select_threshold
class MatchTests(unittest.TestCase):
 def test_training_only(self):
  x=np.array([[0.],[.1],[10.],[10.1]])
  r=matched_failure_scores(x,[0,0,1,1],[[0.05],[10.05]],neighbors=2)
  np.testing.assert_allclose(r['failure_probability'],[0,1])
 def test_no_single_class(self):
  with self.assertRaises(ValueError):matched_failure_scores([[0.],[1.]],[0,0],[[0.]],neighbors=1)
 def test_calibration_abstention(self):
  self.assertIsNone(select_threshold([.9,.9],[0,1],min_support=3))
 def test_calibration_lift(self):
  self.assertIsNotNone(select_threshold([.9]*30+[.1]*30,[1]*30+[0]*30))
if __name__=='__main__':unittest.main()
