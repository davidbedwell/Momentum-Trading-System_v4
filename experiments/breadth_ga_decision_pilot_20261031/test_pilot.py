import unittest
import numpy as np
import pandas as pd
import pilot

class PilotTests(unittest.TestCase):
    def sample(self):
        return pd.DataFrame(dict(pnl=[100.,-30.,20.], acquisition_cost=[1000.]*3,
            entry_date=pd.to_datetime(['2020-01-01','2020-01-01','2021-01-01']),
            exit_date=pd.to_datetime(['2020-01-10','2020-01-10','2021-01-10'])))

    def test_economic_opportunity_cost(self):
        s=pilot.summarize(self.sample(),[False,False,True])
        self.assertEqual(s['uplift_pnl'],-70.)
        self.assertEqual(s['uplift_pnl'],s['avoided_loss_pnl']-s['skipped_winner_pnl'])
        self.assertEqual(s['skipped_net_pnl'],70.)
        self.assertTrue(np.isnan(s['mdd']))

    def test_whole_episode_baseline(self):
        g=self.sample()
        s=pilot.summarize(g,[True]*3)
        self.assertEqual(s['retained_pnl'],g.pnl.sum())
        self.assertEqual(s['capital_days_retention'],1.)
        self.assertEqual(s['uplift_pnl'],0.)

    def test_duplicate_and_overlapping_events(self):
        g=self.sample()
        self.assertEqual(pilot.separated_events(g),2)
        self.assertEqual(pilot.separated_events(pd.concat([g,g])),2)

    def test_no_portfolio_cannot_launch_even_with_future_success(self):
        checks,launch=pilot.eligibility(False,1000,1000,1000,True)
        self.assertFalse(launch)
        self.assertFalse(checks['cash_constrained_counterfactual_valid'])
        self.assertFalse(pilot.eligibility(True,19,3,3,True)[1])
        self.assertFalse(pilot.eligibility(True,20,1,1,True)[1])

    def test_real_ledger_timing_and_folds(self):
        t=pd.read_csv(pilot.SOURCE/'trades.csv.gz',parse_dates=['entry_date','exit_date','feature_date'])
        self.assertTrue((t.feature_date<t.entry_date).all())
        for f,start,end in [('F1','2012-01-01','2014-01-01'),('F2','2014-01-01','2016-01-01'),('F3','2016-01-01','2018-01-01')]:
            g=t[t.fold==f]
            self.assertTrue((g.entry_date>=pd.Timestamp(start)).all())
            self.assertTrue((g.exit_date<pd.Timestamp(end)).all())
        np.testing.assert_allclose(t.net_return,t.pnl/t.acquisition_cost)

if __name__=='__main__':
    unittest.main()
