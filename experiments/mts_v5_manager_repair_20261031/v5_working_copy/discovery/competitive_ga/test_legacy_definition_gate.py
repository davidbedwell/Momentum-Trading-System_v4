import unittest
from .legacy_definition_gate import parse
from .legacy_archive_index import LegacyStrategy
class TestLegacy(unittest.TestCase):
 def test_ga4(self):
  x=LegacyStrategy('a','GA4','[["RULE",{}]]','x','63')
  self.assertEqual(parse(x).horizon,63)
 def test_horizons(self):
  x=LegacyStrategy('b','HORIZONS','{"ids":[1],"w":[0.5],"qual":0.7}','x','')
  self.assertEqual(parse(x).payload['ids'],[1])
 def test_reject_mismatch(self):
  x=LegacyStrategy('b','HORIZONS','{"ids":[1,2],"w":[0.5],"qual":0.7}','x','')
  with self.assertRaises(ValueError):parse(x)
if __name__=='__main__':unittest.main()
