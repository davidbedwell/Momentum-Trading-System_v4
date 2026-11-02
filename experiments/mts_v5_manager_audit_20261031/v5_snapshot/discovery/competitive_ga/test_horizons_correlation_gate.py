import unittest
import numpy as np
from .horizons_correlation_gate import validate
class TestCorrelationGate(unittest.TestCase):
 def test_cluster_veto(self):
  x=np.sin(np.arange(70)*.37)/100
  r=np.column_stack((x,x*1.01,x*.99))
  with self.assertRaisesRegex(ValueError,'cluster'):validate({'A':.1,'B':.1,'C':.1},r,['A','B','C'])
 def test_missing_history(self):
  with self.assertRaisesRegex(ValueError,'history'):validate({'A':.1,'B':.1},np.ones((10,2)),['A','B'])
 def test_uncorrelated(self):
  x=np.sin(np.arange(70)*.37)/100;y=np.cos(np.arange(70)*.83)/100
  self.assertTrue(validate({'A':.1,'B':.1},np.column_stack((x,y)),['A','B']))
if __name__=='__main__':unittest.main()
