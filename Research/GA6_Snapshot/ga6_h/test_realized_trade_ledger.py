import unittest
from realized_trade_ledger import realized_trades
class LedgerTests(unittest.TestCase):
 def test_costs(self):
  rows,open_=realized_trades([('2026-01-01','A','buy',10,100),('2026-01-02','A','sell',10,110)])
  self.assertAlmostEqual(rows[0]['net_pnl'],97.9)
  self.assertFalse(open_)
 def test_split_and_dividend(self):
  rows,_=realized_trades([('2026-01-01','A','buy',10,100),('2026-01-04','A','sell',20,55)],[('2026-01-02','A','split',2),('2026-01-03','A','dividend',1)])
  self.assertAlmostEqual(rows[0]['net_pnl'],117.9)
 def test_open_lot_not_realized(self):
  rows,open_=realized_trades([('2026-01-01','A','buy',10,100)])
  self.assertFalse(rows);self.assertEqual(open_['A'],10)
 def test_unmatched_sell_rejected(self):
  with self.assertRaises(ValueError):realized_trades([('2026-01-01','A','sell',1,100)])
