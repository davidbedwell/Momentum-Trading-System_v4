import unittest
from .horizons_causal_rank import evaluate
class TestRank(unittest.TestCase):
 def test_qualification(self):
  g={'ids':[0],'w':[1.],'qual':.7,'short':False,'safe_margin':0.}
  r=evaluate(g,{'A':{'ret5':.1},'B':{'ret5':.5},'C':{'ret5':.9}})
  self.assertEqual([t for t,x in r.items() if x['qualified']],['C'])
 def test_cross_section_required(self):
  with self.assertRaises(ValueError):evaluate({'ids':[0],'w':[1.]},{'A':{'ret5':.2}})
if __name__=='__main__':unittest.main()
