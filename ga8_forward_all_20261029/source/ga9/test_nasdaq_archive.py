"""Adversarial adapter checks: diagnostic data cannot become replay evidence."""
import json
from pathlib import Path
import tempfile
import unittest
import pandas as pd
from ga9.nasdaq_archive import normalize, snapshot_projection, require_replay_inputs, bar_issues
from ga9.screening import membership_mask


class ArchiveTests(unittest.TestCase):
    def test_eodhd_unknown_actions_and_lineage(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/'OLD.json'
            path.write_text(json.dumps([dict(date='2022-01-03', open=2, high=3,
                                            low=1, close=2, adjusted_close=2, volume=10)]))
            d = normalize(path)
            self.assertTrue(d.dividends.isna().all())
            self.assertTrue(d.stock_splits.isna().all())
            self.assertEqual(d.ticker.tolist(), ['OLD'])
            self.assertEqual(len(d.source_sha256.iloc[0]), 64)
            self.assertEqual(bar_issues(d)['unknown_action_rows'], 1)

    def test_local_dates_and_explicit_actions_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/'X.parquet'
            pd.DataFrame({'Open':[2], 'High':[3], 'Low':[1], 'Close':[2],
                          'Adj Close':[1.9], 'Volume':[10], 'Dividends':[0.1],
                          'Stock Splits':[0]}, index=pd.DatetimeIndex(
                              ['2022-01-03'], tz='America/New_York', name='Date')).to_parquet(path)
            d = normalize(path)
            self.assertEqual(str(d.date.iloc[0]), '2022-01-03 00:00:00')
            self.assertEqual(d.dividends.iloc[0], 0.1)

    def test_removal_reentry_and_no_terminal_extension(self):
        snapshots = [dict(effective_date=date, eligible_tickers=tickers) for date,tickers in
                     [('2021-12-20',['A']), ('2022-02-01',['B']),
                      ('2022-03-01',['A']), ('2022-04-01',['A'])]]
        d = snapshot_projection(snapshots)
        self.assertEqual(d.ticker.tolist(), ['A','B','A'])
        self.assertEqual(d.effective_to.max(), '2022-04-01')
        self.assertTrue(d.known_at.isna().all())
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/'membership.csv'
            d.to_csv(path,index=False)
            with self.assertRaisesRegex(ValueError, 'known by'):
                membership_mask(pd.date_range('2022-01-01', periods=3), ['A','B'], path)

    def test_duplicate_snapshots_rejected(self):
        with self.assertRaises(ValueError):
            snapshot_projection([dict(effective_date='2022-01-01', eligible_tickers=[])]*2)

    def test_forged_gate_never_authorizes_replay(self):
        with self.assertRaisesRegex(ValueError, 'blocked'):
            require_replay_inputs({'status':'CERTIFIED', 'blockers':[], 'passed':True})

    def test_bad_and_duplicate_bars_reported(self):
        d = pd.DataFrame(dict(ticker=['A','A'], date=['2022-01-03']*2,
                              open=[2,2], high=[1,3], low=[1,1], close=[2,2],
                              adj_close=[2,2],volume=[10,10],dividends=[0,0],stock_splits=[0,0]))
        self.assertEqual(bar_issues(d)['invalid_rows'],1)
        self.assertEqual(bar_issues(d)['duplicates'],1)

if __name__ == '__main__':
    unittest.main()
