import unittest
from ga7.engine import Genome
from ga7.request_replay import replay_requests
class MultilegTests(unittest.TestCase):
 def test_scale_in_and_reduce_reconciles_final_nav(self):
  g=Genome('momentum','a','b','AND',0,0,.1,1,'signal_decay',.02)
  prices=[100,100,104,104,99,99,99,99]
  sessions=[]
  for i,v in enumerate(prices):
   signal=1. if i<4 else .4
   sessions.append((str(i),{'T':{'open':float(v),'close':float(v),'low':float(v),'eligible':True,'features':{'a':signal,'b':signal},'sector':'X'}},False))
  m,_=replay_requests(g,sessions,lambda g,b:b['features']['a']>.5,fee=.001,cash_yield=0)
  self.assertEqual(m['trades'],1)
  self.assertLess(m['ev_r'],0)
  self.assertLess(m['final_nav'],100000.)
 def test_dividend_cashflow_reconciles(self):
  g=Genome('momentum','a','b','AND',0,0,.1,1,'signal_decay',.02)
  sessions=[]
  for i in range(5):
   sessions.append((str(i),{'T':{'open':100.,'close':100.,'low':100.,'dividend':1. if i==2 else 0.,'eligible':True,'features':{'a':1.,'b':1.},'sector':'X'}},False))
  m,_=replay_requests(g,sessions,lambda g,b:True,fee=0,cash_yield=0)
  self.assertAlmostEqual(m['final_nav'],100100.)
  self.assertAlmostEqual(m['ev_r'],.5)
if __name__=='__main__':unittest.main()
