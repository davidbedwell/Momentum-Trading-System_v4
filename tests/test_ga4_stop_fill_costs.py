[Reading 24 lines from start (total: 24 lines, 0 remaining)]

import unittest
import pandas as pd
import numpy as np
from Core.layered_ga.ga4_stop_fill_costs import estimate_fill_cost

class TestStopFillCosts(unittest.TestCase):
    def setUp(self):
        dates=pd.bdate_range('2026-01-02',periods=100)
        self.bars=pd.DataFrame({'date':dates,'open':100.,'high':101.,'low':99.,'close':100.,'volume':1000000.})
    def test_costs_finite_and_positive_for_observed_fill(self):
        c=estimate_fill_cost(self.bars,30,31,34,100,97)
        self.assertTrue(np.isfinite(c))
        self.assertGreater(c,0)
    def test_cannot_use_future_for_entry_cost(self):
        a=estimate_fill_cost(self.bars,30,31,34,100,97)
        self.bars.loc[33,'high']=99.5
        b=estimate_fill_cost(self.bars,30,31,34,100,97)
        self.assertNotEqual(a,b)
        self.assertEqual(estimate_fill_cost(self.bars,30,31,31,100,97),estimate_fill_cost(self.bars,30,31,31,100,97))
    def test_insufficient_history_is_ineligible(self):
        self.assertTrue(np.isnan(estimate_fill_cost(self.bars,10,11,12,100,97)))
    def test_invalid_timeline_rejected(self):
        with self.assertRaises(ValueError):estimate_fill_cost(self.bars,32,31,34,100,97)
if __name__=='__main__':unittest.main()

[executed on device: instance-e298gycb-main (a21f8a9b-b225-483b-b45f-ba34708f98ee)]