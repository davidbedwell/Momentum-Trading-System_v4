"""Bounded real-source regression for the missing raw-close integration bug."""
import sys
import pandas as pd
from discovery.competitive_ga.first_year_features import build,RAW,COLUMNS
from discovery.competitive_ga.first_year_parity import ga6_features
from discovery.competitive_ga.archived_genomes import ga7_bars


def test_actual_predictors_join_raw_close_before_native_ga7_rank(monkeypatch):
    monkeypatch.setattr(sys,'path',['/opt/mts/ga7-deploy/ga7_unbounded',*sys.path])
    from ga7.runner import COLUMNS as native_columns
    cutoff='2022-01-05'
    tickers=('STK_0000','STK_0001')
    raw=pd.read_parquet(RAW,columns=COLUMNS,filters=[('Date','<=',pd.Timestamp(cutoff)),('Ticker','in',list(tickers))])
    raw=raw.rename(columns={c:c.lower() for c in COLUMNS})
    raw['date']=pd.to_datetime(raw.date)
    predictors=build(as_of=cutoff,smoke_tickers=tickers)
    assert 'close' not in predictors
    panel=ga6_features(raw,predictors)
    pd.testing.assert_series_equal(panel.set_index(['date','ticker']).close.sort_index(),raw.set_index(['date','ticker']).close.sort_index())
    bars=ga7_bars(panel.loc[panel.date==cutoff],decision_date=cutoff,eligibility=dict.fromkeys(tickers,True),columns=native_columns)
    assert set(bars)==set(tickers)
    assert all(bars[t]['close']>0 for t in tickers)
