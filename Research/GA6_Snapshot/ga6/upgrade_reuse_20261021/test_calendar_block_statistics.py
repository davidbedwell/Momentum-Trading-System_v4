import unittest
import numpy as np
from ga6.upgrade_reuse_20261021.calendar_block_statistics import bootstrap_indices,spa_global,stepdown_max_t

class CalendarBlockTests(unittest.TestCase):
 def test_contiguous_wrapped_blocks(self):
  idx=bootstrap_indices(17,4,200,7)
  self.assertEqual(idx.shape,(200,17))
  for row in idx:
   for i in (0,4,8,12):
    self.assertTrue(all(row[j]==(row[i]+j-i)%17 for j in range(i+1,min(i+4,17))))
 def test_deterministic_global(self):
  x=np.random.default_rng(8).normal(size=(300,5))
  self.assertEqual(spa_global(x,10,199,42),spa_global(x,10,199,42))
 def test_stepdown_monotonic(self):
  x=np.random.default_rng(5).normal(size=(300,6))
  result=stepdown_max_t(x,12,199,3)
  ordered=[result['adjusted_p_values'][i] for i in result['order']]
  self.assertTrue(all(a<=b for a,b in zip(ordered,ordered[1:])))
 def test_invalid(self):
  with self.assertRaises(ValueError):spa_global(np.ones((50,3)),5,199)
  with self.assertRaises(ValueError):spa_global(np.ones((50,3)),5,20)
if __name__=='__main__':unittest.main()
