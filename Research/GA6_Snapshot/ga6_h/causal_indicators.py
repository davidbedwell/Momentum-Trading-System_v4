"""Close-t-only stock indicators; no forward labels or future normalization."""
import numpy as np
import pandas as pd

WINDOWS=(5,10,20,40,60,120,252)

def enrich(bars, windows=WINDOWS):
    """Input contains historical raw bars; returns causal features sorted by symbol/date.
    Sector and breadth are computed from contemporaneous eligible rows.
    Missing sector labels remain NaN (not fabricated).
    """
    required={'date','symbol','Close','Volume'}
    if not required.issubset(bars.columns): raise ValueError('missing causal inputs')
    d=bars.copy()
    d['date']=pd.to_datetime(d.date)
    if d.duplicated(['symbol','date']).any():raise ValueError('duplicate stock/date')
    d=d.sort_values(['symbol','date']).reset_index(drop=True)
    close=pd.to_numeric(d.Close,errors='coerce')
    vol=pd.to_numeric(d.Volume,errors='coerce')
    if close.isna().any() or (close<=0).any() or vol.isna().any() or (vol<0).any():
        raise ValueError('invalid OHLCV')
    d['_ret1']=close.groupby(d.symbol).pct_change(fill_method=None)
    for w in windows:
        if not isinstance(w,int) or w<2:raise ValueError('window >=2 required')
        group=d.groupby('symbol',sort=False)
        past=group.Close.shift(w)
        r=close/past-1
        d[f'return_{w}']=r
        d[f'acceleration_{w}']=r-(past/group.Close.shift(2*w)-1)
        mean=group.Close.transform(lambda s:s.rolling(w,min_periods=w).mean())
        d[f'trend_{w}']=close/mean-1
        avgvol=group.Volume.transform(lambda s:s.rolling(w,min_periods=w).mean())
        d[f'liquidity_{w}']=close*avgvol
        d[f'volatility_{w}']=group['_ret1'].transform(lambda s:s.rolling(w,min_periods=w).std())
        d[f'volume_ratio_{w}']=vol/avgvol.replace(0,np.nan)
        # Same-session cross-sectional benchmark; no future dates.
        market=d.groupby('date')[f'return_{w}'].transform('mean')
        d[f'relative_strength_{w}']=r-market
        # Contemporaneous breadth is fraction of eligible securities above their own MA.
        eligible=d.eligible_signal.fillna(False).astype(bool) if 'eligible_signal' in d else pd.Series(True,index=d.index)
        above=(close>mean).where(eligible & mean.notna())
        d[f'breadth_{w}']=above.groupby(d.date).transform('mean')
        if 'sector' in d:
            sector_avg=d[f'return_{w}'].groupby([d.date,d.sector],dropna=True).transform('mean')
            d[f'sector_strength_{w}']=sector_avg-market
        else:
            d[f'sector_strength_{w}']=np.nan
        d[f'volume_{w}']=d[f'volume_ratio_{w}']
    return d.drop(columns=['_ret1'])
