"""Strict causal-panel loader for five synthetic 500-ticker years.
No chromosome selection, future outcome scoring or portfolio performance claims.
"""
from pathlib import Path
import pandas as pd
ROOT=Path('/opt/mts/synthetic-market-lab/runs/causal_native_features')

def load_year(year,columns=None):
    if year not in range(1,6):raise ValueError('year index must be 1..5')
    a=pd.read_parquet(ROOT/f'universe_{year}_ga4_native.parquet')
    b=pd.read_parquet(ROOT/f'universe_{year}_eight_family.parquet')
    keys=['date','ticker']
    for frame in (a,b):
        if not set(keys+['close']).intersection(frame.columns)>=set(keys):raise ValueError('missing keys')
        frame['date']=pd.to_datetime(frame['date'])
        if frame.duplicated(keys).any():raise ValueError('duplicate ticker-date')
    extra=keys+[c for c in b if c not in a and c not in keys]
    joined=a.merge(b[extra],on=keys,how='inner',validate='one_to_one')
    if len(joined)!=len(a) or len(joined)!=len(b):raise ValueError('feature-panel mismatch')
    if joined.ticker.nunique()!=500:raise ValueError('not 500 tickers')
    if columns is not None:joined=joined[keys+list(columns)]
    return joined.sort_values(keys).reset_index(drop=True)

def audit_five_years():
    summary=[]
    for i in range(1,6):
        p=load_year(i,columns=['open','close'])
        first,last=p.date.min(),p.date.max()
        # These are parallel five-year scenarios, NOT sequential years.
        if p[['open','close']].isna().any().any() or (p[['open','close']]<=0).any().any():raise ValueError('invalid prices')
        summary.append({'year':i,'first':str(first.date()),'last':str(last.date()),'sessions':int(p.date.nunique()),'tickers':int(p.ticker.nunique()),'rows':len(p)})
        # Keep scenario identity separate in every fold and result.
    return summary
