import unittest
from .horizons_full_math import targets
class TestFull(unittest.TestCase):
 def test_short(self):
  g={'ids':[0],'w':[1.],'qual':.8,'short':True,'short_qual':.8,'safe_margin':0.,'alloc':'strength','replace_margin':0.}
  x=targets(g,{'A':{'ret5':.1},'B':{'ret5':.5},'C':{'ret5':.9}})
  self.assertLess(x['A'],0)
  self.assertGreater(x['C'],0)
 def test_downside_needs_history(self):
  g={'ids':[0],'w':[1.],'qual':.5,'short':False,'safe_margin':0.,'alloc':'downside','replace_margin':0.}
  with self.assertRaises(ValueError):targets(g,{'A':{'ret5':.1},'B':{'ret5':.9}})
if __name__=='__main__':unittest.main()
