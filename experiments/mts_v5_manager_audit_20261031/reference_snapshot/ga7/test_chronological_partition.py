import unittest
from ga7.ga7_folds import expanding_walk_forward
from ga7.chronological_partition import partition
class ChronologicalPartitionTests(unittest.TestCase):
 def test_no_training_forward_overlap(self):
  training,forward=partition(expanding_walk_forward())
  self.assertTrue(training and forward)
  self.assertLessEqual(max(end for _,end in training),min(w['test_start'] for w in forward))
  self.assertEqual(min(w['test_start'] for w in forward),'2019-01-01')
 def test_reject_missing_forward(self):
  with self.assertRaises(ValueError):partition(expanding_walk_forward(last_year=2017))
if __name__=='__main__':unittest.main()
