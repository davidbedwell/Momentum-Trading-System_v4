import unittest
from .horizons_next_open_execution import Book,queue,execute_next_open,equity
class TestNextOpen(unittest.TestCase):
 def test_next_open_not_signal_close(self):
  b=Book();queue(b,{'A':{'target_weight':.1}})
  self.assertEqual(b.cash,100000);self.assertEqual(b.shares,{})
  o=execute_next_open(b,{'A':110},fee_bps=10)
  self.assertEqual(o[0]['side'],'BUY');self.assertAlmostEqual(b.shares['A'],10000/110)
  self.assertAlmostEqual(b.fees_paid,10);self.assertAlmostEqual(equity(b,{'A':110}),99990)
 def test_exit_and_missing_price(self):
  b=Book();queue(b,{'A':{'target_weight':.1}})
  with self.assertRaises(ValueError):execute_next_open(b,{})
  execute_next_open(b,{'A':100});queue(b,{'A':{'target_weight':0}})
  o=execute_next_open(b,{'A':105});self.assertEqual(o[0]['side'],'SELL');self.assertAlmostEqual(b.shares['A'],0)
 def test_sale_proceeds_not_reused_until_settled(self):
  from .horizons_next_open_execution import settle
  b=Book(cash=0.,shares={'A':100.})
  queue(b,{'A':{'target_weight':0.},'B':{'target_weight':.1}})
  orders=execute_next_open(b,{'A':100.,'B':100.})
  self.assertEqual([o['side'] for o in orders],['SELL'])
  self.assertEqual(b.cash,0.)
  self.assertEqual(b.unsettled_cash,10000.)
  self.assertAlmostEqual(equity(b,{'A':100.,'B':100.}),10000.)
  settle(b)
  self.assertEqual(b.cash,10000.)
  self.assertEqual(b.unsettled_cash,0.)
 def test_missing_held_price_rejected(self):
  with self.assertRaises(ValueError):equity(Book(shares={'A':1.}),{'B':100.})
 def test_short_blocked(self):
  with self.assertRaises(ValueError):queue(Book(),{'A':{'target_weight':-.05}})
if __name__=='__main__':unittest.main()
