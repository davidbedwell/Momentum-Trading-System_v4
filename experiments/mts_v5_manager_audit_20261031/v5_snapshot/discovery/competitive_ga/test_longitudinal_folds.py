import unittest
from .longitudinal_folds import Fold,expanding_folds,validate_folds
class TestLongitudinalFolds(unittest.TestCase):
 def test_expanding(self):
  f=expanding_folds(2017)
  self.assertEqual([(x.train_end,x.evaluation_year) for x in f],[(2017,2018),(2018,2019),(2019,2020),(2020,2021)])
  self.assertTrue(validate_folds(f))
 def test_reject_leakage(self):
  f=list(expanding_folds(2017))
  f[1]=Fold(2,2017,2020,2019)
  with self.assertRaises(ValueError):validate_folds(f)
if __name__=='__main__':unittest.main()
