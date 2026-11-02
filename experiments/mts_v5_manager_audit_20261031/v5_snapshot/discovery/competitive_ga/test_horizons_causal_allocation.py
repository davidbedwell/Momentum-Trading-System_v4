import unittest
from .horizons_causal_allocation import allocate
class TestAllocation(unittest.TestCase):
 def test_cap_and_cash(self):
  r=allocate({'short':False,'alloc':'strength','replace_margin':.1},{'A':.8,'B':.2})
  self.assertEqual(r,{'A':.1,'B':.1})
 def test_unsupported_transform_fails(self):
  with self.assertRaises(ValueError):allocate({'short':False,'alloc':'downside','replace_margin':.1},{'A':1.})
 def test_no_opportunity(self):
  self.assertEqual(allocate({'short':False,'alloc':'strength','replace_margin':.1},{'A':0.}),{})
if __name__=='__main__':unittest.main()
