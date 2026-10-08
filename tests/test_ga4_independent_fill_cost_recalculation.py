[Reading 34 lines from start (total: 34 lines, 0 remaining)]

"""Independent arithmetic oracle for GA4 execution cost estimates."""
import unittest
import math
from datetime import date
import pandas as pd
from Core.layered_ga.ga4_stop_fill_costs import estimate_fill_cost
from Core.layered_ga.stage2_path_v3 import _frozen_costs

class TestIndependentCostRecalculation(unittest.TestCase):
    def test_manual_two_leg_recalculation(self):
        dates=pd.bdate_range('2026-01-02',periods=100)
        bars=pd.DataFrame({'date':dates,'open':[100.]*100,'high':[101.]*100,'low':[99.]*100,'close':[100.]*100,'volume':[1000000.]*100})
        bars.loc[33,'high']=100.5
        decision,entry,exit_=30,31,34
        actual=estimate_fill_cost(bars,decision,entry,exit_,100.,97.)
        def independently_calculated_leg(day):
            history=bars.iloc[day-19:day+1]
            adv=sum(float(row.close)*float(row.volume) for row in history.itertuples())/20
            b=bars.iloc[day]
            spread=max(2.,min(50.,10000*(float(b.high)-float(b.low))/float(b.close)/2))
            impact=10.*math.sqrt(100000./adv)
            return (spread+impact)/10000
        sell_date=dates[exit_].date()
        sell_fee=_frozen_costs.regulatory_sell_fee(sell_date,100000.,100000./97.,97.)/100000.
        independent=independently_calculated_leg(decision)+independently_calculated_leg(exit_-1)+sell_fee
        self.assertAlmostEqual(actual,independent,places=12)
    def test_entry_leg_unchanged_by_future_price_shock(self):
        dates=pd.bdate_range('2026-01-02',periods=100)
        bars=pd.DataFrame({'date':dates,'open':100.,'high':101.,'low':99.,'close':100.,'volume':1000000.})
        first=estimate_fill_cost(bars,30,31,31,100.,97.)
        bars.loc[32:,'close']=10000.
        second=estimate_fill_cost(bars,30,31,31,100.,97.)
        self.assertEqual(first,second)
if __name__=='__main__':unittest.main()
