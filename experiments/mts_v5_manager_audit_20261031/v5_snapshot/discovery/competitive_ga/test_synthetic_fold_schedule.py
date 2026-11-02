import unittest
from .synthetic_fold_schedule import make_folds
class TestSchedule(unittest.TestCase):
 def test_boundaries(self):
  folds=make_folds(1,range(1260))
  self.assertEqual([(f.train_stop,f.test_start,f.test_stop) for f in folds],[(252,252,504),(504,504,756),(756,756,1008),(1008,1008,1260)])
 def test_reject_duplicates(self):
  with self.assertRaises(ValueError):make_folds(1,[1,1,2,3,4,5,6,7,8,9])
 def test_scenario_identity(self):
  self.assertEqual(make_folds(5,range(100))[0].scenario,5)
if __name__=='__main__':unittest.main()
