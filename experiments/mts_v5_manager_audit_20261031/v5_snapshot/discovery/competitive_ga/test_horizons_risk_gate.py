import unittest
from .horizons_next_open_execution import Book
from .horizons_risk_gate import validate
class TestRiskGate(unittest.TestCase):
 def test_sector_cap(self):
  d={t:{'target_weight':.1} for t in 'ABCD'}
  with self.assertRaisesRegex(ValueError,'sector concentration'):validate(Book(),d,{},dict.fromkeys('ABCD','tech'))
 def test_missing_sector(self):
  with self.assertRaisesRegex(ValueError,'classification'):validate(Book(),{'A':{'target_weight':.1}},{},{})
 def test_diversified(self):
  d={t:{'target_weight':.1} for t in 'ABCD'}
  self.assertTrue(validate(Book(),d,{},dict(zip('ABCD',['tech','tech','health','energy']))))
 def test_held_positions_count(self):
  b=Book(cash=3000.,shares={'A':10.,'B':10.})
  with self.assertRaisesRegex(ValueError,'sector concentration'):validate(b,{'C':{'target_weight':.1}},{'A':100.,'B':100.},{'A':'tech','B':'tech','C':'tech'})
if __name__=='__main__':unittest.main()
