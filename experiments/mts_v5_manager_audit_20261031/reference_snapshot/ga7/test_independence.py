import unittest
from ga7.independence import assert_nonoverlapping_forward,unique_training_epochs
from ga7.ga7_folds import expanding_walk_forward
class IndependenceTests(unittest.TestCase):
 def test_forward_nonoverlap(self):
  windows=expanding_walk_forward()
  self.assertTrue(assert_nonoverlapping_forward(windows))
  epochs=unique_training_epochs(windows)
  self.assertEqual(len(epochs),len(windows))
  self.assertTrue(all(a[1]<=b[0] for a,b in zip(epochs,epochs[1:])))
 def test_reject_overlap(self):
  w=expanding_walk_forward()[:2]
  w[1]['test_start']=w[0]['test_start']
  with self.assertRaises(ValueError):assert_nonoverlapping_forward(w)
if __name__=='__main__':unittest.main()
