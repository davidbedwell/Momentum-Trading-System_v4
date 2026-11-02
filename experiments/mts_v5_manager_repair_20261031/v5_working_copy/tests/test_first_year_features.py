"""Bounded parity check on actual external synthetic data and original code."""
import pandas as pd
import pyarrow.parquet as pq
import pytest
from discovery.competitive_ga.first_year_features import SOURCE,RAW,build


def test_authentic_factory_prefix_is_unchanged_by_later_bars():
    try:
        with SOURCE.open('rb') as stream:stream.read(1)
    except PermissionError:
        pytest.skip('authentic feature source requires read-only elevated access')
    raw=pq.read_table(RAW,columns=['Date','Ticker']).to_pandas()
    dates=sorted(raw.Date.unique())
    tickers=sorted(raw.Ticker.unique())[:2]
    prefix=build(as_of=str(dates[5])[:10],smoke_tickers=tickers)
    longer=build(as_of=str(dates[7])[:10],smoke_tickers=tickers)
    pd.testing.assert_frame_equal(prefix,longer.loc[longer.date<=prefix.date.max()].reset_index(drop=True))
    assert prefix.ticker.nunique()==2
    assert len(prefix)==12
    assert 'Regime' not in prefix and 'regime' not in prefix
    assert any(c.startswith('ga4_') for c in prefix)
