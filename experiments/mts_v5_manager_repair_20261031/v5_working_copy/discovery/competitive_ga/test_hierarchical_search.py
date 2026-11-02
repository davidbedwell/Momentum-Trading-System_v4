import unittest
from discovery.competitive_ga.hierarchical_search import RoutedCandidate,screen_all
class TestRouting(unittest.TestCase):
 def test_all_tiers_and_late_winner(self):
  bank=[RoutedCandidate('a','GA6','NICHE-0001'),RoutedCandidate('b','GA6',None),RoutedCandidate('c','GA4'),RoutedCandidate('d','HORIZONS'),RoutedCandidate('e','GA6','NICHE-0013')]
  rows={'AAA':{'close':10},'BBB':{'close':20}}
  matches,counts=screen_all(rows,bank,lambda t,r,day:'NICHE-0001' if t=='AAA' else None,lambda *args:True,lambda c,r,h,d:('ENTER',.1),'2020-06-01')
  self.assertEqual(len(matches),7)
  self.assertEqual(counts['matched_NICHE'],1)
  self.assertEqual(counts['matched_NO_NICHE'],2)
  self.assertEqual(counts['matched_GA4_HORIZONS'],4)
  self.assertEqual([x[0] for x in matches if x[1]=='AAA'],['NICHE','NO_NICHE','GA4_HORIZONS','GA4_HORIZONS'])
  self.assertTrue(any(x[2]=='d' for x in matches))
 def test_no_niche_fallback(self):
  matches,_=screen_all({'A':{}},[RoutedCandidate('a','GA6','NICHE-0001'),RoutedCandidate('b','GA4')],lambda *a:None,lambda *a:True,lambda *a:('ENTER',.1),0)
  self.assertEqual([x[2] for x in matches],['b'])
if __name__=='__main__':unittest.main()
