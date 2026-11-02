"""Read archived Horizons stress observations with original lag conventions.
Returns only dates with actual source coverage; no extrapolation beyond source end.
"""
from pathlib import Path
import pandas as pd
ROOT=Path('/opt/mts/thunder-migration/Momentum-Trading-System_v4/Research/Data')

RECOVERED_ROOT=Path('/opt/mts/thunder-migration/mts-v4-recovery-integration-20261004/Research/Data')

def load(dates, *, root=ROOT):
 dates=pd.DatetimeIndex(pd.to_datetime(dates)).sort_values().unique()
 v=pd.read_csv(Path(root)/'CrashMultiMarketV1/VIX_History.csv')
 vv=pd.read_csv(Path(root)/'CrashMultiMarketV1/VVIX_History.csv')
 ofr=pd.read_csv(Path(root)/'CrashCausalPackV1/ofr_fsi_raw_20261004.csv')
 v['date']=pd.to_datetime(v.DATE,format='%m/%d/%Y')
 vv['date']=pd.to_datetime(vv.DATE,format='%m/%d/%Y')
 ofr['date']=pd.to_datetime(ofr.Date)
 a=pd.to_numeric(v.set_index('date').CLOSE,errors='coerce').sort_index()
 b=pd.to_numeric(vv.set_index('date').VVIX,errors='coerce').sort_index()
 c=ofr.set_index('date')[['Funding','Credit']].apply(pd.to_numeric,errors='coerce').sort_index().shift(2)
 # Do not extrapolate beyond the last observed source date.
 last=min(a.index.max(),b.index.max(),c.index.max())
 eligible=dates[dates<=last]
 result=pd.DataFrame(index=eligible)
 result['vix']=a.reindex(a.index.union(eligible)).sort_index().ffill().reindex(eligible)
 result['vvix']=b.reindex(b.index.union(eligible)).sort_index().ffill().reindex(eligible)
 lagged=c.reindex(c.index.union(eligible)).sort_index().ffill().reindex(eligible)
 result['funding']=lagged.Funding;result['credit']=lagged.Credit
 if result.isna().any().any():raise ValueError('historical stress inputs incomplete')
 return result.rename_axis('date').reset_index(),{'source_end':str(last.date()),'excluded_dates':len(dates)-len(eligible),'first':str(eligible.min().date()) if len(eligible) else None}
