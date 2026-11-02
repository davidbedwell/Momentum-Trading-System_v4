import unittest
from ga7.engine import Genome
from ga7.request_replay import replay_requests
class IntegratedRTests(unittest.TestCase):
 def test_one_trade_exact_r_with_final_liquidation(self):
  g=Genome('momentum','a','b','AND',0,0,.1,1,'signal_decay',.02)
  prices=[100,100,100,102]
  sessions=[(str(i),{'T':{'open':float(v),'close':float(v),'low':float(v),'eligible':True,'features':{'a':1.,'b':1.},'sector':'X'}},False) for i,v in enumerate(prices)]
  m,_=replay_requests(g,sessions,lambda g,b:True,fee=0,cash_yield=0)
  self.assertEqual(m['trades'],1)
  self.assertAlmostEqual(m['ev_r'],1.,places=8)
  self.assertAlmostEqual(m['final_nav'],100200.,places=8)
  self.assertAlmostEqual(m['mdd'],0.,places=8)
 def test_fee_reduces_r_and_final_nav(self):
  g=Genome('momentum','a','b','AND',0,0,.1,1,'signal_decay',.02)
  sessions=[(str(i),{'T':{'open':100.,'close':100.,'low':100.,'eligible':True,'features':{'a':1.,'b':1.},'sector':'X'}},False) for i in range(4)]
  m,_=replay_requests(g,sessions,lambda g,b:True,fee=.001,cash_yield=0)
  self.assertLess(m['ev_r'],0)
  self.assertLess(m['final_nav'],100000.)
  self.assertGreater(m['mdd'],0.)
if __name__=='__main__':unittest.main()
