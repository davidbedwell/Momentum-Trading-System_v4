import unittest
import numpy as np
import pandas as pd
from dataclasses import replace
from .risk import risk_budget, stop_risk, risk_feasible
from .execution import Gene, Manager, replay
from .test_objective import fixture
from .exploratory import build

class RiskAndScreenTests(unittest.TestCase):
    def test_loss_risk_is_not_capital_exposure(self):
        self.assertAlmostEqual(risk_budget(100000,.02,0,.05),40000)
        self.assertAlmostEqual(risk_budget(100000,.02,1000,.10),10000)
        self.assertAlmostEqual(stop_risk(40000,100,95),2000)
        with self.assertRaises(ValueError): risk_budget(100000,.0201,0,.05)
        self.assertTrue(risk_feasible(.25))
    def test_realistic_deployment_and_separate_cash_risk(self):
        p=fixture(); p.close[:]=100; p.open[:]=100
        g=Gene('trend',threshold=-3,weight=.6,stop_distance=.02,add=100,hold_sessions=500,exit_threshold=-100)
        r=replay(p,[g],Manager(position_cap=.6,slots=2,reserve=.1,correlation=1.1),'2022','2023',True)
        row=r['equity'][1]
        self.assertGreater(row['exposure'],.5)
        self.assertLessEqual(row['defined_stop_risk'],.02)
        self.assertAlmostEqual(row['cash_reserve']+row['exposure'],1)
    def test_ratcheting_stop_bounds_planned_risk_after_gains(self):
        p=fixture()
        g=Gene('trend',threshold=-3,weight=.6,stop_distance=.02,add=100,hold_sessions=500,exit_threshold=-100,trailing=1)
        r=replay(p,[g],Manager(position_cap=.6,slots=2,reserve=.1,correlation=1.1),'2022','2023',True)
        self.assertLessEqual(r['audit']['max_total_risk'],.02+1e-9)
    def test_screen_prefix_and_late_listing(self):
        dates=pd.bdate_range('2022-01-03',periods=620)
        frames=[]
        for j in range(25):
            c=100*(1.0002+j*.0001)**np.arange(620)
            d=pd.DataFrame(dict(date=dates,ticker=str(j).zfill(2),close=c,open=c,volume=1000))
            frames.append(d.iloc[200:] if j==24 else d)
        p,_=build(frames); q,_=build([d[d.date<=dates[550]] for d in frames])
        np.testing.assert_array_equal(p.screen_mask[:551],q.screen_mask)
        self.assertFalse(p.eligible[:200,-1].any())
        self.assertLessEqual(p.screen_mask.sum(axis=1).max(),20)
        self.assertTrue(p.screen_mask[550,-1])
