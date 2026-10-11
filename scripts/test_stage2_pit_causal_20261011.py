#!/usr/bin/env python3
"""Causal compiler prefix invariance, executable forward-path indexing."""
import numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
from Core.layered_ga.stage2_path_v3 import build_execution_paths
from scripts.preflight_horizon_evolution_20261010 import PRED
frame=pd.read_parquet(PRED,columns=['effective_date','security_id'])
assert not frame[['effective_date','security_id']].isna().any().any()
assert not frame.duplicated(['effective_date','security_id']).any()
# Exact historical cutoff: adding future observations must not change past quantiles.
rng=np.random.default_rng(42)
dates=pd.date_range('2020-01-01',periods=40,freq='B')
f=pd.DataFrame({'effective_date':np.repeat(dates,3),'security_id':np.tile(['A','B','C'],40),'close_to_sma_200__v1':rng.normal(size=120)})
a=CausalSignalCompiler(f.iloc[:60].copy()).qthreshold('close_to_sma_200__v1',.8)
b=CausalSignalCompiler(f.copy()).qthreshold('close_to_sma_200__v1',.8)
assert np.allclose(a,b[:60],equal_nan=True)
# Outcome builder must enter next open and exit h trading sessions later.
d=pd.bdate_range('2020-01-01',periods=75)
raw=pd.DataFrame({'security_id':['X']*75,'date':d,'open':np.arange(100.,175.),'high':np.arange(101.,176.),'low':np.arange(99.,174.),'close':np.arange(100.,175.),'adj_close':np.arange(100.,175.)})
paths=build_execution_paths(raw,max_horizon=65)
for h in range(2,66):
 assert np.isclose(paths.endpoint_return[0,h-1],(101+h)/101-1,atol=1e-6),(h,paths.endpoint_return[0,h-1])
 assert np.isnan(paths.endpoint_return[75-h-1,h-1]) if 75-h-1>=0 else True
# Feature factory must be prefix-invariant for every computed predictor column.
from MTS_V4.derived_feature_factory import build_predictor_rows
rawrows=[{'security_id':'X','date':str(t.date()),'open':100+i,'high':101+i,'low':99+i,'close':100+i,'volume':10000+i,'eligible':True} for i,t in enumerate(pd.bdate_range('2019-01-01',periods=300))]
short=build_predictor_rows(rawrows[:275]);full=build_predictor_rows(rawrows)
assert len(short)==275 and len(full)==300
for i,(a,b) in enumerate(zip(short,full)):
 for key,val in a.items():
  other=b[key]
  if isinstance(val,(int,float)) and not isinstance(val,bool) and val is not None:
   assert other is not None and np.isclose(val,other,equal_nan=True), (i,key,val,other)
  else:assert val==other,(i,key)
print('PASS_STAGE2_PIT_PREFIX_AND_FORWARD_PATH_INDEXING')
