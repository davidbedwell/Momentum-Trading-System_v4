#!/usr/bin/env python3
"""V3 calibration Phase 1: outcome-only planting integrity, not GA-search power.
Writes a fail-closed INCOMPLETE_SEARCH_POWER state until Phase 2 evolves.
"""
import sys,json,time,hashlib,traceback,random
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.layered_ga.stage2_data_v3 import load_path_cache,sha256_file
from Core.layered_ga.stage2_compiler_v3 import VectorSignalCompiler,stage2_search_spaces,random_genome
from Core.layered_ga.stage2_evaluator_v3 import cluster_ids_from_frame
RUN=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/calibration'
CACHE=RUN.parent/'cache';PY=ROOT/'Research/Design/MTS_STAGE2_V3_PROVENANCE_20261007.json'
SHAPES={'FAST':(1,3,7,12),'MEDIUM':(3,10,20,30),'SLOW':(8,25,45,60)}
EFFECTS=(0.,.0025,.005,.01,.02)
SEED=20261007

def write(name,obj):
 p=RUN/name;temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(obj,indent=2,allow_nan=False));temp.replace(p)
def state(s,**more):write('status.json',{'state':s,'timestamp':time.time(),**more})
def shape(n):
 a,b,c,d=SHAPES[n];h=np.arange(1,64);return np.interp(h,[1,a,b,c,d,63],[0,0,1,1,0,0]).astype(np.float32)
def main():
 RUN.mkdir(parents=True,exist_ok=True);state('PREFLIGHT')
 freeze=json.loads(PY.read_text());partition=ROOT/freeze['partition']['path'];cost=ROOT/freeze['cost_freeze']['path']
 assert sha256_file(partition)==freeze['partition']['sha256']
 assert sha256_file(cost)==freeze['cost_freeze']['sha256']
 part=json.loads(partition.read_text());assert (len(part['DISCOVERY_UNTOUCHED']),len(part['VERIFICATION_A']),len(part['VERIFICATION_B']),len(part['audit']['touched_tickers']))==(136,100,100,167)
 psets=[set(x['ticker'] for x in part[k]) for k in ('DISCOVERY_UNTOUCHED','VERIFICATION_A','VERIFICATION_B')]+[set(part['audit']['touched_tickers'])]
 assert len(set.union(*psets))==503 and all(not (psets[i]&psets[j]) for i in range(4) for j in range(i+1,4))
 manifest=json.loads((CACHE/'path_cache_manifest.json').read_text());assert manifest['rows']==594182 and manifest['max_horizon']==63
 for name,info in manifest['files'].items():assert sha256_file(CACHE/info['file'])==info['sha256'],name
 features=pd.read_parquet(CACHE/'dev117_predictors_v3.parquet');assert len(features)==594182 and features.security_id.nunique()==117
 assert not (set(features.security_id.unique()) & set.union(*psets[:3])),'PROTECTED BANK LEAK'
 paths,costs=load_path_cache(CACHE);assert paths.endpoint_return.shape==(594182,63)
 compiler=VectorSignalCompiler(features);cid=cluster_ids_from_frame(features); rng=random.Random(SEED)
 spaces=stage2_search_spaces();targets={}
 for family in ('MOMENTUM','MEAN_REVERSION','BREAKOUT'):
  found=None
  for attempt in range(24):
   g=random_genome(spaces[family],rng)
   m=compiler.compile(family,g);n=int(np.sum(m & np.isfinite(paths.endpoint_return[:,19]) & np.isfinite(costs.long_roundtrip[:,19])))
   if n>=5000:found=(g,m,n);break
  if found is None:raise RuntimeError(f'Could not preselect supported calibration target for {family}')
  targets[family]=found
 write('target_manifest.json',{'seed':SEED,'targets':{k:{'genome':v[0],'valid20_n':v[2]} for k,v in targets.items()},'shapes':SHAPES,'effects':EFFECTS,'calibration_only':True})
 state('RUNNING_ENGINEERING_PLANT_AND_NULL_CHECK',completed=0,total=len(targets)*len(SHAPES)*len(EFFECTS))
 records=[];total=len(targets)*len(SHAPES)*len(EFFECTS)
 # Measure the *incremental planted-vs-null net EV curve* on the exact same rows;
 # absent any plant, the difference must be identically zero at every horizon.
 for family,(genome,mask,n20) in targets.items():
  ix=np.flatnonzero(mask);base=paths.endpoint_return[ix];co=costs.long_roundtrip[ix];valid=np.isfinite(base)&np.isfinite(co)
  for sn in SHAPES:
   profile=shape(sn)
   for effect in EFFECTS:
    # Only the selected target row population receives a planted outcome addition.
    uplift=np.where(valid,profile[None,:]*effect,np.nan)
    incremental=np.nanmean(uplift.astype(np.float64),axis=0)
    expected=effect*profile
    error=float(np.nanmax(np.abs(incremental-expected)))
    if error>1e-7:raise AssertionError(f'injection-alignment error {family} {sn} {effect}: {error}')
    peak=np.flatnonzero(incremental>=.95*max(float(incremental.max()),1e-12))+1 if effect>0 else []
    overlap=(max(SHAPES[sn][1],int(min(peak)))<=min(SHAPES[sn][2],int(max(peak)))) if len(peak) else False
    records.append({'family':family,'shape':sn,'effect':effect,'support_n_h20':n20,'max_injection_error':error,'peak_window':list(map(int,peak)),'true_high_window':list(SHAPES[sn][1:3]),'overlap':bool(overlap),'null_exact_zero':bool(effect==0 and np.allclose(incremental,0))})
    if len(records)%5==0:state('RUNNING_ENGINEERING_PLANT_AND_NULL_CHECK',completed=len(records),total=total)
 write('plant_integrity_results.json',{'records':records,'test_count':len(records),'passed':all(r['max_injection_error']<1e-7 and (r['null_exact_zero'] if r['effect']==0 else r['overlap']) for r in records)})
 # Scientific calibration cannot pass here: the full search-power and null-recovery GA is not implemented.
 state('STOPPED_ENGINEERING_SEARCH_POWER_NOT_IMPLEMENTED',plant_integrity_pass=True,plant_tests=len(records),next_action='Implement faithful matched evolutionary recovery and null comparison before Stage2')
 print('PLANT_INTEGRITY_PASS',len(records),'SEARCH_POWER_PENDING',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:
  RUN.mkdir(parents=True,exist_ok=True);write('failure.json',{'error':repr(e),'traceback':traceback.format_exc()});state('ERROR',reason=repr(e));raise
