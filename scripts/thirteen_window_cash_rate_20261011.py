"""Historical 3-month Treasury yield alignment to execution-session cash accrual.
FRED DGS3MO is an annualized percentage yield, not a daily total return.
No lookahead: prior published observation only, strictly earlier than session.
"""
import pathlib
import numpy as np
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'Research/Data/RiskFree/FRED_DGS3MO_20261005.csv'
def session_cash_returns(calendar,path=DEFAULT,annual_days=252):
    dates=pd.DatetimeIndex(pd.to_datetime(calendar)).normalize()
    if len(dates)<2 or dates.has_duplicates or not dates.is_monotonic_increasing:
        raise ValueError('invalid session calendar')
    raw=pd.read_csv(path,usecols=['observation_date','DGS3MO'])
    raw['observation_date']=pd.to_datetime(raw['observation_date']).dt.normalize()
    if raw.observation_date.duplicated().any():raise ValueError('duplicate Treasury observations')
    raw['DGS3MO']=pd.to_numeric(raw.DGS3MO,errors='coerce')
    yields=raw.set_index('observation_date')['DGS3MO'].sort_index().dropna()
    if yields.empty or not np.isfinite(yields.to_numpy()).all():raise ValueError('missing yields')
    # Use only yield observations dated BEFORE the current trading session.
    prior=yields.reindex(yields.index.union(dates)).sort_index().ffill().shift(1).reindex(dates)
    # Shift on the union calendar to exclude same-day observations while
    # retaining a valid yield from the preceding publication day.
    if prior.isna().any():raise ValueError('Treasury history insufficient for calendar')
    if ((prior < -10)|(prior > 100)).any():raise ValueError('implausible Treasury yields')
    daily=(1+prior.to_numpy(dtype=float)/100)**(1/annual_days)-1
    return daily
