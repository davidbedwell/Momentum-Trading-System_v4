import unittest
from .native_manager_bridge import proposal_from_native,orders_from_native
from .manager_policy_v2 import Genes
class TestNativeWeights(unittest.TestCase):
 def test_scale_in_is_increment(self):
  p=proposal_from_native('A','c','GA6','SCALE_IN',.025,held_weight=.05)
  self.assertAlmostEqual(p.target,.075)
 def test_scale_out_is_fraction(self):
  p=proposal_from_native('A','c','GA6','SCALE_OUT',.25,held_weight=.08)
  self.assertAlmostEqual(p.target,.06)
 def test_invalid_scale_out(self):
  with self.assertRaises(ValueError):proposal_from_native('A','c','GA6','SCALE_OUT',1.2,held_weight=.08)
 def test_learning_cap(self):
  with self.assertRaises(ValueError):orders_from_native([],{},.2,Genes(max_total=.30))
 def test_no_unearned_capital(self):
  self.assertEqual(orders_from_native([('A','c','GA6','ENTER',.1,None)],{},.5,Genes(max_total=.1)),{})
if __name__=='__main__':unittest.main()
