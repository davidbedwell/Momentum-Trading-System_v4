import unittest
from ga7.fold_features import rank_filtered_sessions
class RankTests(unittest.TestCase):
 def test_filter_before_rank_and_ties(self):
  s=[('2020-01-01',{'A':{'features':{'x':1.}},'B':{'features':{'x':2.}},'C':{'features':{'x':3.}}},False)]
  x=rank_filtered_sessions(s,['A','C'],['x'])
  self.assertEqual(x[0][1]['A']['features']['x'],.5)
  self.assertEqual(x[0][1]['C']['features']['x'],1.)
  self.assertEqual(s[0][1]['A']['features']['x'],1.)
 def test_tie_average_rank(self):
  s=[('2020-01-01',{'A':{'features':{'x':1.}},'B':{'features':{'x':1.}}},False)]
  x=rank_filtered_sessions(s,['A','B'],['x'])
  self.assertEqual(x[0][1]['A']['features']['x'],.75)
if __name__=='__main__':unittest.main()
