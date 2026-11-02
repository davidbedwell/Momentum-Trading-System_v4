import unittest
from ga7.ga7_folds import sector_balanced_folds,expanding_walk_forward
class GA7FoldTests(unittest.TestCase):
 def test_disjoint(self):
  stocks={f'T{i}':f'S{i%4}' for i in range(79)}
  folds=sector_balanced_folds(stocks)
  self.assertEqual(len(folds),3)
  self.assertEqual(len(set(sum(folds.values(),[]))),79)
  self.assertEqual(folds,sector_balanced_folds(stocks))
 def test_chronology(self):
  rows=expanding_walk_forward()
  self.assertEqual(rows[0]['test_start'],'2014-01-01')
  self.assertEqual(rows[-1]['test_start'],'2024-01-01')
  self.assertTrue(all(x['train_end_exclusive']==x['test_start'] for x in rows))
if __name__=='__main__':unittest.main()
