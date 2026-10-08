import unittest
import numpy as np
import pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler

class TestCausalQuantiles(unittest.TestCase):
    def test_future_changes_do_not_affect_past(self):
        frame=pd.DataFrame({'effective_date':['2025-01-01','2025-01-02','2025-01-03'],'feature':[2.,4.,6.]})
        a=CausalSignalCompiler(frame).qthreshold('feature',.5)
        changed=frame.copy();changed.loc[2,'feature']=1000000.
        b=CausalSignalCompiler(changed).qthreshold('feature',.5)
        np.testing.assert_array_equal(a[:3],b[:3])
        self.assertTrue(np.isnan(a[0]))
        self.assertEqual(a[1],2.)
        self.assertEqual(a[2],3.)
    def test_same_day_values_not_in_threshold(self):
        frame=pd.DataFrame({'effective_date':['2025-01-01','2025-01-02','2025-01-02','2025-01-03'],'feature':[1.,10.,100.,3.]})
        a=CausalSignalCompiler(frame).qthreshold('feature',.5)
        self.assertEqual(a[1],1.)
        self.assertEqual(a[2],1.)
        self.assertEqual(a[3],10.)
    def test_quantile_compile(self):
        frame=pd.DataFrame({'effective_date':['2025-01-01','2025-01-02','2025-01-03'],'feature':[1.,2.,3.]})
        compiler=CausalSignalCompiler(frame)
        signal=compiler.compile('MOMENTUM',{'momentum_feature':'feature','threshold_quantile':.5,'direction':'ABOVE','context_feature':'NONE'})
        self.assertEqual(list(signal),[False,True,True])
if __name__=='__main__':unittest.main()
