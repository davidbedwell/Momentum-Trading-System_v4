import unittest
from ga7.trade_accounting import TradeAccount
class TradeAccountingTests(unittest.TestCase):
 def test_scale_in_and_partial_exit(self):
  a=TradeAccount();a.buy(1000,.02);a.buy(500,.02)
  a.sell(600,.5)
  ret,r=a.finish(1000)
  self.assertAlmostEqual(ret,100/1500)
  self.assertAlmostEqual(r,100/30)
 def test_loss_in_r(self):
  a=TradeAccount();a.buy(1000,.02)
  self.assertEqual(a.finish(980)[1],-1.)
 def test_invalid_fraction(self):
  a=TradeAccount();a.buy(1000,.02)
  with self.assertRaises(ValueError):a.sell(100,1.1)
if __name__=='__main__':unittest.main()
