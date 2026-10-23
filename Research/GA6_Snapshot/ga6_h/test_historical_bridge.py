import unittest
import pandas as pd
from context_free_genome import Genome
from historical_bridge import evaluate_chromosome
class BridgeTests(unittest.TestCase):
 def test_end_to_end_with_realized_prices(self):
  dates=pd.bdate_range('2026-09-01',periods=12)
  bars=pd.DataFrame([{'date':d,'symbol':'ABC','Open':100+i,'Close':100+i,'tradable_bar':True,'eligible_signal':True,'return_20':.1,'volume_ratio_20':1.1,'Stock Splits':0.,'Dividends':0.} for i,d in enumerate(dates)])
  g=Genome({'op':'AND','children':[{'feature':'momentum','window':20,'threshold':0,'direction':'>=','transform':'raw'},{'feature':'volume','window':20,'threshold':0,'direction':'>=','transform':'raw'}]},hold_sessions=3)
  out=evaluate_chromosome(g,bars,{'ABC':[]},{'ABC'},'2026-09-30')
  self.assertGreater(out['executed_buys'],0)
  self.assertIsNotNone(out['stats'])
 def test_fail_closed_earnings(self):
  dates=pd.bdate_range('2026-09-01',periods=8)
  bars=pd.DataFrame([{'date':d,'symbol':'ABC','Open':100.,'Close':100.,'tradable_bar':True,'return_20':.1,'volume_ratio_20':1.1,'Stock Splits':0.,'Dividends':0.} for d in dates])
  g=Genome({'op':'AND','children':[{'feature':'momentum','window':20,'threshold':0,'direction':'>=','transform':'raw'},{'feature':'volume','window':20,'threshold':0,'direction':'>=','transform':'raw'}]})
  out=evaluate_chromosome(g,bars,{},set(),'2026-09-30')
  self.assertEqual(out['executed_buys'],0)

class MeasuredEVTests(unittest.TestCase):
 def test_bridge_realized_ev_and_cagr(self):
  dates=pd.bdate_range('2026-09-01',periods=12)
  bars=pd.DataFrame([{'date':d,'symbol':'ABC','Open':100.+i,'Close':100.+i,'tradable_bar':True,'eligible_signal':True,'return_20':.1,'volume_ratio_20':1.1,'Stock Splits':0.,'Dividends':0.} for i,d in enumerate(dates)])
  g=Genome({'op':'AND','children':[{'feature':'momentum','window':20,'threshold':0,'direction':'>=','transform':'raw'},{'feature':'volume','window':20,'threshold':0,'direction':'>=','transform':'raw'}]},hold_sessions=3)
  out=evaluate_chromosome(g,bars,{'ABC':[]},{'ABC'},'2026-09-30')
  self.assertGreater(len(out['completed_trades']),0)
  self.assertIsInstance(out['net_ev_dollars_per_completed_trade'],float)
  self.assertIn('cagr',out['stats'])
  self.assertIn('max_drawdown',out['stats'])
 def test_zero_trades_has_no_ev(self):
  dates=pd.bdate_range('2026-09-01',periods=5)
  bars=pd.DataFrame([{'date':d,'symbol':'ABC','Open':100.,'Close':100.,'tradable_bar':True,'return_20':.1,'volume_ratio_20':1.1,'Stock Splits':0.,'Dividends':0.} for d in dates])
  g=Genome({'op':'AND','children':[{'feature':'momentum','window':20,'threshold':0,'direction':'>=','transform':'raw'},{'feature':'volume','window':20,'threshold':0,'direction':'>=','transform':'raw'}]})
  out=evaluate_chromosome(g,bars,{},set(),'2026-09-30')
  self.assertIsNone(out['net_ev_dollars_per_completed_trade'])
