import unittest
from engines.portfolio_replay.kernel import Replay,Bar
from .horizons_long_execution_bridge import signals_from_decisions
class TestLongBridge(unittest.TestCase):
 def test_next_open_and_exit(self):
  r=Replay()
  entry={'AAA':{'action':'ENTER_LONG','previous_weight':0,'target_weight':.10}}
  r.day('D1',{'AAA':Bar(100,100)},signals_from_decisions(entry,'h1'))
  self.assertEqual(len(r.ledger),0)
  r.day('D2',{'AAA':Bar(110,110)},signals_from_decisions({'AAA':{'action':'EXIT_LONG','previous_weight':.10,'target_weight':0}},'h1'))
  self.assertEqual(r.ledger[0][0],'D2');self.assertEqual(r.ledger[0][4],110)
  r.day('D3',{'AAA':Bar(105,105)})
  self.assertEqual([row[2] for row in r.ledger],['BUY','SELL'])
  self.assertEqual(r.ledger[-1][4],105)
 def test_shorts_blocked(self):
  with self.assertRaises(ValueError):signals_from_decisions({'AAA':{'action':'ENTER_SHORT','previous_weight':0,'target_weight':-.1}},'h')
 def test_overcap_blocked(self):
  with self.assertRaises(ValueError):signals_from_decisions({'AAA':{'action':'ENTER_LONG','previous_weight':0,'target_weight':.2}},'h')
if __name__=='__main__':unittest.main()
