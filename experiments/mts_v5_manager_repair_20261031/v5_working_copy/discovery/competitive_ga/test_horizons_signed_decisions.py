import unittest
from .horizons_signed_decisions import decide
class TestSigned(unittest.TestCase):
 def setUp(self):
  self.g={'ids':[0],'w':[1.],'qual':.8,'short':True,'short_qual':.8,'safe_margin':0.,'alloc':'strength','replace_margin':0.}
  self.p={'A':{'ret5':.1},'B':{'ret5':.5},'C':{'ret5':.9}}
 def test_short_blocked(self):
  with self.assertRaises(ValueError):decide(self.g,self.p)
 def test_signed_entries(self):
  a=decide(self.g,self.p,allow_shorts=True)
  self.assertEqual(a['A']['action'],'ENTER_SHORT')
  self.assertEqual(a['C']['action'],'ENTER_LONG')
 def test_short_cover(self):
  g=dict(self.g,short=False,qual=1.)
  a=decide(g,self.p,previous={'A':-.1},allow_shorts=True)
  self.assertEqual(a['A']['action'],'COVER_SHORT')
if __name__=='__main__':unittest.main()
