import unittest
from ga6.structural_evolution_v3_20261022.family_logic import evaluate,validate
A={'family':'trend','threshold':0,'comparison':'>='}
B={'family':'momentum','threshold':0,'comparison':'>='}
C={'family':'volatility','threshold':0.2,'comparison':'<='}
class TestLogic(unittest.TestCase):
 def test_flat(self):
  assert evaluate({'op':'AND','children':[A,B]},dict(trend=1,momentum=-1)) is False
  assert evaluate({'op':'OR','children':[A,B]},dict(trend=1,momentum=-1)) is True
 def test_grouped(self):
  x={'op':'AND','children':[{'op':'OR','children':[A,B]},C]}
  assert len(validate(x))==3
  assert evaluate(x,dict(trend=-1,momentum=1,volatility=.1)) is True
  assert evaluate(x,dict(trend=-1,momentum=1,volatility=.3)) is False
 def test_missing(self):
  assert evaluate({'op':'OR','children':[A,B]},dict(trend=1)) is None
 def test_duplicate_rejected(self):
  with self.assertRaises(ValueError):validate({'op':'OR','children':[A,A]})
if __name__=='__main__':unittest.main()
