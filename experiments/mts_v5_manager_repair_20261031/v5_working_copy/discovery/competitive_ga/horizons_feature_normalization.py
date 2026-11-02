"""Original Horizons stock cross-section and prior-history market normalization."""
import numpy as np
import pandas as pd
from .horizons_native_score import STOCK,MARKET

def normalize(raw):
 required={'date','ticker',*STOCK,*MARKET}
 if not required<=set(raw.columns):raise ValueError('incomplete Horizons native features')
 if raw.duplicated(['date','ticker']).any():raise ValueError('duplicate date-ticker')
 p=raw.sort_values(['date','ticker']).copy()
 for name in STOCK:
  # Match original argsort(argsort) and valid-count denominator exactly.
  def ranks(s):
   a=s.to_numpy(dtype=np.float32)
   order=np.argsort(np.argsort(np.nan_to_num(a,nan=-1e30))).astype(float)
   valid=np.isfinite(a);den=max(int(valid.sum())-1,1)
   out=order/den;out[~valid]=np.nan
   return pd.Series(out,index=s.index)
  p[name]=p.groupby('date',sort=False)[name].transform(ranks)
 market=p.groupby('date',sort=True)[list(MARKET)].first()
 for name in MARKET:
  hist=[];vals=[]
  for value in market[name].to_numpy(dtype=np.float32):
   if np.isfinite(value):
    prior=np.asarray(hist[-1260:],dtype=float)
    vals.append(float((prior<=value).mean()) if len(prior)>=60 else .5)
    hist.append(float(value))
   else:vals.append(.5)
  market[name]=vals
 p=p.drop(columns=list(MARKET)).merge(market.reset_index(),on='date',validate='many_to_one')
 return p.sort_values(['date','ticker']).reset_index(drop=True)
