import unittest
from discovery.competitive_ga.adaptive_search import search_session,SearchPolicy
from discovery.competitive_ga.hierarchical_search import RoutedCandidate
class TestAdaptive(unittest.TestCase):
 def setUp(self):
  self.bank=[RoutedCandidate('n','GA6','NICHE-0001'),RoutedCandidate('g','GA4'),RoutedCandidate('h','HORIZONS'),RoutedCandidate('u','GA6',None)]
  self.rows={str(i):{} for i in range(6)}
  self.calls=[]
 def decision(self,c,row,held,date):
  self.calls.append(c.chromosome_id)
  return 'ENTER',.1
 def search(self,idx,threshold):
  return search_session(self.rows,self.bank,lambda *a:'NICHE-0001',lambda *a:True,self.decision,'2020-06-01',idx,SearchPolicy(threshold,5))
 def test_sufficient_skips_fallback(self):
  x=self.search(1,5)
  self.assertFalse(x['counts']['expanded'])
  self.assertFalse(x['shadow'])
  self.assertEqual(set(self.calls),{'n'})
 def test_insufficient_expands(self):
  x=self.search(1,7)
  self.assertTrue(x['counts']['expanded'])
  self.assertEqual({m[2] for m in x['active']},{'n','g','h','u'})
 def test_weekly_shadow_without_live_fallback(self):
  x=self.search(5,5)
  self.assertFalse(x['counts']['expanded'])
  self.assertEqual({m[2] for m in x['active']},{'n'})
  self.assertEqual({m[2] for m in x['shadow']},{'n','g','h','u'})
if __name__=='__main__':unittest.main()
