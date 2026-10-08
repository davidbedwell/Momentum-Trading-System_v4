#!/usr/bin/env python3
"""Read-only independent structural audit of DEV117 cached sample counts/cost identities."""
import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007'
C=BASE/'cache'; OUT=BASE/'calibration/ga4_cached_independent_audit_20261008.json'
def main():
 df=pd.read_parquet(C/'dev117_predictors_v3.parquet',columns=['effective_date','security_id'])
 raw=pd.read_parquet(C/'dev117_raw_aligned_v3.parquet',columns=['date','security_id'])
 assert len(df)==len(raw)==594182
 assert np.array_equal(df.security_id.to_numpy(),raw.security_id.to_numpy())
 assert np.array_equal(pd.to_datetime(df.effective_date).to_numpy(),pd.to_datetime(raw.date).to_numpy())
 ids=(df.security_id.astype(str)+'|'+pd.to_datetime(df.effective_date).dt.year.astype(str)).to_numpy()
 clusters,_=pd.factorize(ids,sort=True)
 manifest=json.loads((C/'path_cache_manifest.json').read_text())
 arrays={n:np.load(C/(n+'.npy'),mmap_mode='r',allow_pickle=False) for n in ('endpoint_return','long_roundtrip','short_roundtrip','calendar_days','spread_bps','impact_bps','regulatory_sell_fraction')}
 checks=[]
 for h in (1,3,7,12,20,30,45,63):
  j=h-1; valid=np.isfinite(arrays['endpoint_return'][:,j]);row={'horizon':h}
  for side in ('long','short'):
   cost=arrays[side+'_roundtrip'][:,j];ok=valid&np.isfinite(cost)
   row[side+'_valid_rows']=int(ok.sum());row[side+'_security_year_clusters']=int(np.unique(clusters[ok]).size)
   if side=='long':
    model=2*(arrays['spread_bps'][ok]+arrays['impact_bps'][ok])/10000+arrays['regulatory_sell_fraction'][ok]
    row['long_cost_max_abs_identity_error']=float(np.max(np.abs(cost[ok].astype(float)-model))) if ok.any() else None
   else:
    long=arrays['long_roundtrip'][ok,j].astype(float);days=arrays['calendar_days'][ok,j].astype(float)
    model=long+.003*days/365
    row['short_borrow_max_abs_identity_error']=float(np.max(np.abs(cost[ok].astype(float)-model))) if ok.any() else None
  checks.append(row)
 report={'decision':'STRUCTURAL_CHECK_ONLY','certified':False,'independent_effective_n_verified':False,'causal_costs_verified':False,'note':'Recomputes raw security-year cluster counts and cached algebraic cost identities, not candidate-specific effective N or independently sourced executable fills','aligned_rows':len(df),'horizons':checks}
 OUT.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
