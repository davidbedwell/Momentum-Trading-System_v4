import unittest,pandas as pd
from Core.layered_ga.gen1_path_episode_audit import paired_brier_by_episode,quarter_labels
class EpisodeAuditTests(unittest.TestCase):
 def test_paired_score(self):
  p=pd.DataFrame({'failure_probability':[.9,.1,.8,.2],'baseline_probability':[.5]*4,
    'failure_outcome':[1,0,1,0],'episode':['a','a','b','b']})
  r=paired_brier_by_episode(p)
  self.assertEqual(r['episodes'],2)
  self.assertEqual(r['positive_episodes'],2)
  self.assertGreater(r['row_weighted_gain'],0)
  self.assertIn('UNVERIFIED',r['certification'])
 def test_invalid_probability(self):
  p=pd.DataFrame({'failure_probability':[1.1],'baseline_probability':[.5],'failure_outcome':[1],'episode':['a']})
  with self.assertRaises(ValueError):paired_brier_by_episode(p)
 def test_quarters(self):
  self.assertEqual(list(quarter_labels(['2020-01-01','2020-04-01'])),['2020Q1','2020Q2'])
if __name__=='__main__':unittest.main()
