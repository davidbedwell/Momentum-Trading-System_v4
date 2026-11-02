import unittest
from .horizons_daily_adapter import decide
class TestDaily(unittest.TestCase):
 def test_entry_exit(self):
  g={'ids':[0],'w':[1.],'qual':.7,'short':False,'safe_margin':0.,'alloc':'strength','replace_margin':0.}
  x=decide(g,{'A':{'ret5':.1},'B':{'ret5':.5},'C':{'ret5':.9}}, {'A':.1})
  self.assertEqual(x['A']['action'],'EXIT')
  self.assertEqual(x['C']['action'],'ENTER')
  self.assertEqual(x['C']['target_weight'],.1)
 def test_no_signal(self):
  g={'ids':[0],'w':[1.],'qual':1.,'short':False,'alloc':'strength','replace_margin':0.}
  self.assertEqual(decide(g,{'A':{'ret5':.1},'B':{'ret5':.9}}),{})
if __name__=='__main__':unittest.main()
