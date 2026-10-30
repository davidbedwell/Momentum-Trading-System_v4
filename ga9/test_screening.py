"""Daily variation, membership, prefix causality and screen-to-open integration."""
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
import numpy as np
import pandas as pd
from .screening import ScreenPolicy
from .execution import load_panel, replay, Gene, Manager
from .test_benchmarks import frame

class DailyScreenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dates = pd.bdate_range('2022-01-03', periods=260)
        a = frame('A', self.dates, 1.001)
        b = frame('B', self.dates, 1.0001)
        for f, late in [(a, 1.0001), (b, 1.004)]:
            f.loc[150:, 'close'] = f.close.iloc[149] * late**np.arange(1,111)
            f['open'] = np.r_[f.close.iloc[0], f.close.to_numpy()[:-1]]
            f['high'] = f[['open','close']].max(axis=1)*1.001
            f['low'] = f[['open','close']].min(axis=1)*.999
            f['adj_close'] = f.close
        self.data = pd.concat([a,b])
        self.path = self.root/'stocks.parquet'
        self.data.to_parquet(self.path)
    def panel(self, **kw):
        return load_panel(self.path, screen_policy=ScreenPolicy(1), **kw)[0]
    def test_daily_variation_prefix_and_future_mutation(self):
        p = self.panel()
        self.assertEqual(np.flatnonzero(p.screen_mask[140]).tolist(), [0])
        self.assertEqual(np.flatnonzero(p.screen_mask[240]).tolist(), [1])
        prefix = self.panel(end=str(self.dates[200].date()))
        np.testing.assert_array_equal(p.screen_mask[:200], prefix.screen_mask)
        self.data.loc[self.data.date >= self.dates[200], 'close'] *= 3
        self.data.loc[self.data.date >= self.dates[200], 'high'] *= 3
        self.data.to_parquet(self.path)
        changed = self.panel()
        np.testing.assert_allclose(p.screen_score[:200], changed.screen_score[:200], equal_nan=True)
    def test_historical_peers_and_next_open(self):
        history = self.root/'membership.csv'
        pd.DataFrame(dict(ticker=['A','B'],effective_from=['2022-01-01',str(self.dates[180].date())],
                          effective_to=[str(self.dates[220].date()),None],known_at=['2021-12-01']*2)).to_csv(history,index=False)
        p = self.panel(membership=history)
        self.assertFalse(p.eligible[:180,1].any())
        self.assertTrue(np.isnan(p.features['relative_strength'][:180,1]).all())
        self.assertFalse(p.screen_mask[220:,0].any())
        signal = np.ones((1,*p.close.shape))*.01
        result = replay(p,[Gene('momentum',threshold=0.,hold_sessions=1000,add=100,weight=.001,trailing=1.,exit_threshold=-100)],Manager(correlation=1.),
                        '2022','2023',True,signal=signal,edge_mode=True)
        entries = [f for f in result['fills'] if f['action']=='ENTRY']
        self.assertTrue(entries)
        for fill in entries:
            t=p.dates.get_loc(pd.Timestamp(fill['date'])); j=p.symbols.index(fill['ticker'])
            self.assertTrue(p.screen_mask[t-1,j])
            self.assertTrue(p.eligible[t,j])
            self.assertAlmostEqual(fill['price'],p.open[t,j]*1.0005)
        self.assertTrue(any(f['reason']=='membership_exit' for f in result['fills']))
        history.write_text('ticker,effective_from,effective_to,known_at\nA,2022-01-01,,2023-01-01\n')
        with self.assertRaisesRegex(ValueError,'known'):
            self.panel(membership=history)
