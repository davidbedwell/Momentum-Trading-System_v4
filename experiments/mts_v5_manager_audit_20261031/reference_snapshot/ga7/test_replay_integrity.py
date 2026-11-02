import unittest
from ga7.engine import Genome
from ga7.request_replay import replay_requests
class ReplayIntegrityTests(unittest.TestCase):
 def test_fill_uses_signal_chromosome_stop(self):
  g=Genome('momentum','a','b','AND',0,0,.05,2,'reversal',.01)
  sessions=[]
  for i in range(5):
   bars={t:{'open':100.,'close':100.,'low':100.,'eligible':True,'features':{'a':1.,'b':1.},'controlling_niche':'N'} for t in ('AAA','BBB')}
   sessions.append((f'2020-01-{i+1:02d}',bars,False))
  metrics,ledger=replay_requests(g,sessions,lambda genome,bar:True)
  self.assertGreater(metrics['trades'],0)
  self.assertEqual(metrics['mae_stop_ratio'],0)
 def test_no_fixed_max_hold(self):
  g=Genome('momentum','a','b','AND',0,0,.05,1,'signal_decay',.02)
  sessions=[]
  for i in range(65):
   sessions.append((f'{i:04d}',{'AAA':{'open':100.,'close':100.,'low':100.,'eligible':True,'features':{'a':1.,'b':1.},'controlling_niche':'N'}},False))
  metrics,_=replay_requests(g,sessions,lambda genome,bar:True)
  self.assertEqual(metrics['trades'],1)
  self.assertGreater(metrics['avg_hold'],40)
if __name__=='__main__':unittest.main()
