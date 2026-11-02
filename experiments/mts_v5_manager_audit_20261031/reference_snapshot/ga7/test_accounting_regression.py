import unittest
from ga7.engine import Genome
from ga7.request_replay import replay_requests

class AccountingRegressionTests(unittest.TestCase):
 def genome(self):
  return Genome('momentum','a','b','AND',0,0,.1,1,'signal_decay',.02)
 def sessions(self,prices,features=None):
  result=[]
  for i,price in enumerate(prices):
   value=features[i] if features else 1.
   result.append((f'D{i:03d}',{'AAA':{'open':float(price),'close':float(price),'low':float(price),'eligible':True,'features':{'a':value,'b':value},'controlling_niche':'N'}},False))
  return result
 def test_zero_fees_flat_price_is_flat(self):
  m,_=replay_requests(self.genome(),self.sessions([100]*6),lambda g,b:True,fee=0,cash_yield=0)
  self.assertAlmostEqual(m['final_nav'],100000.,places=6)
 def test_scale_in_then_exit_conserves_cash(self):
  prices=[100,100,104,104,104,104,104]
  m,_=replay_requests(self.genome(),self.sessions(prices),lambda g,b:b['features']['a']>.5,fee=0,cash_yield=0)
  self.assertGreater(m['final_nav'],100000.)
 def test_no_trade_without_signal(self):
  m,_=replay_requests(self.genome(),self.sessions([100]*5),lambda g,b:False,fee=0,cash_yield=0)
  self.assertEqual(m['trades'],0)
  self.assertEqual(m['final_nav'],100000.)
if __name__=='__main__':unittest.main()
