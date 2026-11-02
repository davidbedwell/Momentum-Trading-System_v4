import unittest
from ga7.engine import Genome
from ga7.request_replay import replay_requests
class CashReconciliationTests(unittest.TestCase):
 def test_dividends_fees_yield_and_scale_in(self):
  g=Genome('momentum','a','b','AND',0,0,.1,2,'signal_decay',.02)
  sessions=[]
  for i,v in enumerate([100,100,104,104,104,104]):
   bars={t:{'open':float(v),'close':float(v),'low':float(v),'dividend':.25 if i==3 else 0.,'eligible':True,'features':{'a':1.,'b':1.},'sector':t} for t in ('A','B')}
   sessions.append((str(i),bars,False))
  m,_=replay_requests(g,sessions,lambda g,b:True,fee=.001,cash_yield=.0297)
  self.assertAlmostEqual(m['cash_reconciliation_error'],0.,places=6)
  self.assertGreater(m['trades'],0)
if __name__=='__main__':unittest.main()
