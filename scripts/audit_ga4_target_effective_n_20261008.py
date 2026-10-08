#!/usr/bin/env python3
"""Independent target-specific cluster counts, never a heldout or GA certification."""
import json
from pathlib import Path
import numpy as np,pandas as pd
from Core.layered_ga.stage2_compiler_v3 import VectorSignalCompiler
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007'
C=BASE/'cache'; CAL=BASE/'calibration'
def main():
 df=pd.read_parquet(C/'dev117_predictors_v3.parquet')
 compiler=VectorSignalCompiler(df)
 targets=json.loads((CAL/'target_manifest.json').read_text())['targets']
 ids=(df.security_id.astype(str)+'|'+pd.to_datetime(df.effective_date).dt.year.astype(str)).to_numpy()
 returns=np.load(C/'endpoint_return.npy',mmap_mode='r')
 costs={s:np.load(C/(s+'_roundtrip.npy'),mmap_mode='r') for s in ('long','short')}
 rows=[]
 for family,target in targets.items():
  mask=np.asarray(compiler.compile(family,target['genome']),bool)
  for side in ('long','short'):
   for h in range(1,64):
    valid=mask&np.isfinite(returns[:,h-1])&np.isfinite(costs[side][:,h-1])
    n=int(valid.sum());g=int(len(set(ids[valid])))
    rows.append({'family':family,'side':side.upper(),'horizon':h,'raw_n':n,'security_year_clusters':g,'evaluator_eligible':n>=200 and g>=20})
 out={'certified':False,'scope':'independent target-mask raw N and security-year cluster counts, all 63 horizons both sides','candidate_specific_ga_n_verified':False,'market_shock_dependence_verified':False,'rows':rows}
 (CAL/'ga4_target_effective_n_audit_20261008.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'rows':len(rows),'families':len(targets),'min_raw_n':min(r['raw_n'] for r in rows),'min_clusters':min(r['security_year_clusters'] for r in rows),'all_eligible':all(r['evaluator_eligible'] for r in rows)}))
if __name__=='__main__':main()
