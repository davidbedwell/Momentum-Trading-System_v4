import unittest
from portfolio_execution import Portfolio,Order,quantity_for_weight,entry_permitted

class ExecutionTests(unittest.TestCase):
    def test_cash_and_costs(self):
        p=Portfolio(1000,{},{});self.assertTrue(p.fill(Order('ABC',5,'buy'),100))
        self.assertAlmostEqual(p.cash,499.5)
        self.assertAlmostEqual(p.equity({'ABC':100}),999.5)
        self.assertTrue(p.fill(Order('ABC',5,'sell'),110))
        self.assertAlmostEqual(p.cash,1048.95)
    def test_insufficient_cash(self):
        p=Portfolio(100,{},{});self.assertFalse(p.fill(Order('ABC',2,'buy'),100))
        self.assertEqual(p.shares,{})
    def test_weight_cap(self):
        self.assertEqual(quantity_for_weight(10000,10000,100,0.03),2)
        with self.assertRaises(ValueError):quantity_for_weight(10000,10000,100,0.11)
    def test_unknown_earnings_fail_closed(self):
        self.assertFalse(entry_permitted('ABC','2026-10-22',{},['2026-10-22'],'2026-10-21T20:00:00+00:00',set()))

if __name__=='__main__':unittest.main()
