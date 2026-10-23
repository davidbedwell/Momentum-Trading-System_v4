import unittest
from performance_metrics import equity_metrics,trade_net_ev
class MetricsTests(unittest.TestCase):
 def test_flat(self):
  m=equity_metrics([100000]*253)
  self.assertEqual(m['cagr'],0)
  self.assertEqual(m['max_drawdown'],0)
 def test_drawdown(self):
  m=equity_metrics([100000,120000,90000,110000])
  self.assertAlmostEqual(m['max_drawdown'],-.25)
 def test_ev(self):self.assertEqual(trade_net_ev([100,-50,25]),25)
 def test_empty_ev(self):
  with self.assertRaises(ValueError):trade_net_ev([])
