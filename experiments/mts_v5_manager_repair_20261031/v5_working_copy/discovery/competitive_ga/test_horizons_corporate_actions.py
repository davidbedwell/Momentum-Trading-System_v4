import unittest
from .horizons_next_open_execution import Book,equity,apply_split,apply_dividend
class TestCorporateActions(unittest.TestCase):
 def test_split_preserves_equity(self):
  b=Book(cash=1000.,shares={'A':10.})
  before=equity(b,{'A':100.})
  apply_split(b,'A',2.)
  self.assertEqual(b.shares['A'],20.)
  self.assertAlmostEqual(equity(b,{'A':50.}),before)
 def test_dividend_cash(self):
  b=Book(cash=100.,shares={'A':10.})
  self.assertEqual(apply_dividend(b,'A',1.5),15.)
  self.assertEqual(b.cash,115.)
 def test_invalid_actions(self):
  with self.assertRaises(ValueError):apply_split(Book(),'A',0.)
  with self.assertRaises(ValueError):apply_dividend(Book(),'A',-1.)
if __name__=='__main__':unittest.main()
