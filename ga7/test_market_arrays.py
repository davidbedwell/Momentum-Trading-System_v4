import unittest
import numpy as np
import pandas as pd
from ga7.market_arrays import prepare

class ArrayTests(unittest.TestCase):
    def test_contiguous_and_no_lookahead_signal(self):
        df = pd.DataFrame([
            dict(date=d, ticker="AAA", open=100, close=101, low=99,
                 dividends=0, stock_splits=0, sector_name="Tech",
                 security_id="id", signal=s)
            for d, s in [("2020-01-02", 1.), ("2020-01-03", 2.),
                         ("2020-01-06", 3.)]
        ])
        policy = dict(membership=[[d, "AAA", True] for d in df.date],
                      blocked={"AAA": []}, risk_veto={d: True for d in df.date})
        market = prepare(df, ["signal"], policy, {d: False for d in df.date},
                         start="2020-01-01", end="2020-12-31")
        self.assertTrue(market.features.flags.c_contiguous)
        self.assertTrue(market.opens.flags.c_contiguous)
        self.assertEqual(market.features.shape, (3, 1, 1))
        try:
            from ga7.compiled_signals import scan_signals
            import numba
        except ImportError:
            self.skipTest("Numba unavailable")
        result = scan_signals(market.features, market.present, market.eligible,
                              market.defense, 0, 0, .5, .5, True)
        self.assertFalse(result[0, 0])
        self.assertTrue(result[1, 0])
        self.assertTrue(result[2, 0])

    def test_missing_membership_fails_closed(self):
        df = pd.DataFrame([dict(date="2020-01-02", ticker="AAA", open=1,
            close=1, low=1, dividends=0, stock_splits=0, sector_name="Tech",
            security_id="id", signal=1)])
        with self.assertRaises(ValueError):
            prepare(df, ["signal"], {"membership": [], "blocked": {},
                 "risk_veto": {"2020-01-02": True}},
                 {"2020-01-02": False}, start="2020-01-01", end="2020-12-31")

if __name__ == "__main__":
    unittest.main()
