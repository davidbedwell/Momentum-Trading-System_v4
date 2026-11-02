"""Bounded causal GA4 feature generation using the original research factory.

No simulator regime labels, surrogate predictors, or writes to research inputs.
Cross-sectional features require the complete intended universe. Small ticker
subsets are allowed only for explicit smoke/parity checks.
"""
from pathlib import Path
import importlib.util
import sys
import numpy as np
import pandas as pd

SOURCE=Path('/opt/mts/thunder-migration/mts-layered-run-20261007/Core/layered_ga/stage2_features_v3.py')
RAW=Path('/opt/mts/synthetic-market-lab/runs/five_iteration_inputs/universe_1/stock_prices.parquet')
COLUMNS=['Date','Ticker','Open','High','Low','Close','Volume','Sector']


def build(raw_path=RAW, *, as_of, smoke_tickers=None):
    """Rebuild a <=504-session prefix, including any required warmup.

    All rolling inputs stop at as_of before calling external code. The source
    factory is loaded from its real path; it is never copied or replaced.
    """
    cutoff=pd.Timestamp(as_of)
    frame=pd.read_parquet(raw_path,columns=COLUMNS,
                          filters=[('Date','<=',cutoff)])
    frame=frame.loc[pd.to_datetime(frame.Date)<=cutoff].copy()
    if smoke_tickers is not None:
        frame=frame.loc[frame.Ticker.isin(smoke_tickers)].copy()
    if frame.empty or frame.Date.nunique()>504 or frame.Ticker.nunique()>500:
        raise ValueError('feature build requires 1..504 sessions and 1..500 tickers')
    if frame.duplicated(['Date','Ticker']).any():raise ValueError('duplicate raw bars')
    expected = set(smoke_tickers) if smoke_tickers is not None else set(frame.Ticker)
    if smoke_tickers is None and len(expected) != 500:
        raise ValueError('full-universe build requires exactly 500 tickers')
    if not expected or any(set(g.Ticker) != expected for _, g in frame.groupby('Date')):
        raise ValueError('incomplete daily cross section')
    numeric=frame[['Open','High','Low','Close','Volume']].to_numpy(dtype=float)
    if not np.isfinite(numeric).all() or (numeric[:,:4]<=0).any() or (numeric[:,4]<0).any():
        raise ValueError('invalid OHLCV')
    if ((frame.High<frame[['Open','Close','Low']].max(axis=1)) |
        (frame.Low>frame[['Open','Close','High']].min(axis=1))).any():
        raise ValueError('inconsistent OHLC')
    sectors=frame[['Ticker','Sector']].drop_duplicates()
    if sectors.Ticker.duplicated().any():raise ValueError('dated sector adapter required')
    spec=importlib.util.spec_from_file_location('mts_authentic_stage2_features',SOURCE)
    module=importlib.util.module_from_spec(spec)
    # External imports must not write pycache into the read-only research tree.
    prior=sys.dont_write_bytecode
    sys.dont_write_bytecode=True
    try:
        spec.loader.exec_module(module)
        frame=frame.rename(columns={c:c.lower() for c in COLUMNS})
        pieces=[module.build_stock_local_frame(g,t,str(g.sector.iloc[0]),None)
                for t,g in frame.groupby('ticker',sort=True)]
        full=module.recompute_cross_sectional(pd.concat(pieces,ignore_index=True))
    finally:
        sys.dont_write_bytecode=prior
    aliases={f'ga4_{c}':np.tanh(pd.to_numeric(full[c],errors='coerce').astype(float).clip(-1e8,1e8))
             for c in full if c.endswith('__v1')}
    full=pd.concat([full,pd.DataFrame(aliases,index=full.index)],axis=1)
    full=full.rename(columns={'effective_date':'date'})
    full['date']=pd.to_datetime(full.date)
    if full.date.max()>cutoff:raise ValueError('external factory returned future rows')
    return full.sort_values(['date','ticker']).reset_index(drop=True)
