"""Independent array-formula replay of archived Horizons normalization.
Tests the normalization formulas, not provenance or publication timestamps.
"""
import numpy as np
import pandas as pd
from .horizons_native_score import STOCK,MARKET,FEATURES
from .horizons_feature_normalization import normalize

def compare(raw):
 dates=pd.DatetimeIndex(sorted(raw.date.unique()))
 tickers=sorted(raw.ticker.unique())
 if len(raw)!=len(dates)*len(tickers):raise ValueError('rectangular input required')
 ordered=raw.sort_values(['date','ticker']).reset_index(drop=True)
 x=ordered[list(FEATURES)].to_numpy(dtype=np.float32,copy=True).reshape(len(dates),len(tickers),len(FEATURES))
 for k in range(len(STOCK)):
  a=x[:,:,k]
  order=np.argsort(np.argsort(np.nan_to_num(a,nan=-1e30),axis=1),axis=1).astype(np.float32)
  valid=np.isfinite(a);den=np.maximum(valid.sum(1,keepdims=True)-1,1)
  r=order/den;r[~valid]=np.nan;x[:,:,k]=r
 for k in range(len(STOCK),len(FEATURES)):
  vals=[];hist=[]
  for value in x[:,0,k]:
   if np.isfinite(value):
    prior=np.asarray(hist[-1260:],float)
    vals.append(float((prior<=value).mean()) if len(prior)>=60 else .5)
    hist.append(float(value))
   else:vals.append(.5)
  x[:,:,k]=np.asarray(vals,np.float32)[:,None]
 actual=normalize(ordered)[list(FEATURES)].to_numpy(dtype=float).reshape(x.shape)
 difference=np.abs(actual-x.astype(float))
 per_feature={name:{'count':int(np.sum(difference[:,:,k]>1e-6)),'max':float(np.nanmax(difference[:,:,k]))} for k,name in enumerate(FEATURES) if np.any(difference[:,:,k]>1e-6)}
 return {'dates':len(dates),'stocks':len(tickers),'cells':int(np.prod(x.shape)),'max_abs_diff':float(np.nanmax(difference)),'nonmatching_gt_1e_6':int(np.sum(difference>1e-6)),'by_feature':per_feature}
