import unittest
from ga7.engine import Genome
from ga7.request_replay import replay_requests
class SharedBankTests(unittest.TestCase):
 def test_two_niches_share_one_account(self):
  a=Genome('momentum','x','y','AND',0,0,.10,10,'signal_decay',.02)
  b=Genome('trend','x','y','AND',0,0,.10,10,'signal_decay',.02)
  sessions=[]
  for i in range(5):
   bars={t:{'open':100.,'close':100.,'low':100.,'eligible':True,'sector':'S'+str(j),'features':{'x':1.,'y':1.},'controlling_niche':('N1' if j%2==0 else 'N2')} for j,t in enumerate('ABCDE')}
   sessions.append((f'D{i}',bars,False))
  m,ledger=replay_requests({'N1':a,'N2':b,'NON_NICHE':a},sessions,lambda g,bar:True,fee=0,cash_yield=0)
  self.assertEqual(m['trades'],5)
  self.assertEqual(m['final_nav'],100000.)
  self.assertEqual(sum(m['niche_entry_counts'].values()),5)
 def test_shared_cash_prevents_overfunding(self):
  g=Genome('momentum','x','y','AND',0,0,.10,10,'signal_decay',.02)
  sessions=[]
  for i in range(4):
   bars={str(j):{'open':100.,'close':100.,'low':100.,'eligible':True,'sector':'S'+str(j),'features':{'x':1.,'y':1.},'controlling_niche':'N'} for j in range(15)}
   sessions.append((f'D{i}',bars,False))
  m,_=replay_requests({'N':g,'NON_NICHE':g},sessions,lambda g,b:True,fee=0,cash_yield=0)
  self.assertLessEqual(m['trades'],10)
  self.assertAlmostEqual(m['final_nav'],100000.)
if __name__=='__main__':unittest.main()
