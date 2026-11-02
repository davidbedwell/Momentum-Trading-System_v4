import unittest
from .horizons_next_open_accounting import Account,execute
class TestNextOpen(unittest.TestCase):
 def test_buy_sell_and_fees(self):
  a=Account();first=execute(a,{'A':.1},{'A':100.})
  self.assertAlmostEqual(a.shares['A'],100.)
  self.assertAlmostEqual(first['equity_after_fees'],99990.)
  second=execute(a,{}, {'A':110.})
  self.assertFalse(a.shares)
  self.assertAlmostEqual(a.cash,100979.)
 def test_no_borrow(self):
  a=Account(cash=100.);execute(a,{'A':.1,'B':.1},{'A':10.,'B':10.})
  self.assertGreaterEqual(a.cash,0)
 def test_short_block(self):
  with self.assertRaisesRegex(ValueError,'long-only'):execute(Account(),{'A':-.1},{'A':100.})
 def test_missing_next_open(self):
  with self.assertRaisesRegex(ValueError,'missing'):execute(Account(),{'A':.1},{})
if __name__=='__main__':unittest.main()
