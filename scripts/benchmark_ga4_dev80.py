"""DEV80-only executable path preparation and repeatable candidate evaluation benchmark.
Checkpoint arrays and timing are persisted atomically; no DEV37 price reads.
"""
import json,hashlib,time,os
from pathlib import Path
import numpy as np,pandas as pd
from Core.layered_ga.stage2_path_v3 import build_execution_paths,build_prospective_costs
from Core.layered_ga.stage2_evaluator_v3 import evaluate_curve,cluster_ids_from_frame
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def main():
 manifest=json.loads((DIR/'checkpoint_manifest.json').read_text())
 for file,key in [('dev80_raw.parquet','raw_sha256'),('dev80_predictors.parquet','predictors_sha256')]:
  if sha(DIR/file)!=manifest[key]:raise ValueError('checkpoint checksum mismatch '+file)
 raw=pd.read_parquet(DIR/'dev80_raw.parquet');pred=pd.read_parquet(DIR/'dev80_predictors.parquet')
 if raw.security_id.nunique()!=80 or pred.security_id.nunique()!=80:raise ValueError('DEV80 isolation')
 key=pd.MultiIndex.from_arrays([raw.security_id.astype(str),pd.to_datetime(raw.date)])
 ids=pd.MultiIndex.from_arrays([pred.security_id.astype(str),pd.to_datetime(pred.effective_date)])
 if not key.is_unique or not ids.is_unique:raise ValueError('duplicate identity')
 idx=key.get_indexer(ids)
 if (idx<0).any():raise ValueError('missing decision identity')
 t0=time.perf_counter();paths=build_execution_paths(raw);t1=time.perf_counter();costs=build_prospective_costs(raw,paths);t2=time.perf_counter()
 arrays={}
 for name in ('endpoint_return','low_excursion','high_excursion','calendar_days'):
  arrays[name]=getattr(paths,name)[idx]
 for name in ('long_roundtrip','short_roundtrip','spread_bps','impact_bps','adv_dollars','regulatory_sell_fraction'):
  arrays[name]=getattr(costs,name)[idx]
 arrays['cluster_ids']=cluster_ids_from_frame(pred)
 arrfile=DIR/'dev80_execution_arrays.npz'
 if arrfile.exists():
  with np.load(arrfile) as saved:
   if set(saved.files)!=set(arrays) or any(not np.array_equal(saved[k],arrays[k],equal_nan=True) for k in arrays):
    raise ValueError('existing execution checkpoint differs; refusing overwrite')
 else:
  with arrfile.open('wb') as f:
   np.savez(f,**arrays);f.flush();os.fsync(f.fileno())
 from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
 from Core.layered_ga.stage2_evaluator_v3 import CurveEvaluation
 from dataclasses import fields
 projected_paths=ExecutionPaths(**{k:arrays[k] for k in ('endpoint_return','low_excursion','high_excursion','calendar_days')})
 projected_costs=ProspectiveCosts(**{k:arrays[k] for k in ('long_roundtrip','short_roundtrip','spread_bps','impact_bps','adv_dollars','regulatory_sell_fraction')})
 mask=np.array(pred.eligible,dtype=bool,copy=True) if 'eligible' in pred else np.ones(len(pred),dtype=bool)
 mask &= np.asarray(pred['return_20__v1'],dtype=float)>0
 samples=[]
 for j in range(3):
  start=time.perf_counter();curve=evaluate_curve(mask,projected_paths,projected_costs,'LONG',arrays['cluster_ids'],min_raw_n=200,min_effective_n=20)
  samples.append(time.perf_counter()-start)
 if len(curve.points)!=63:raise ValueError('not 63 horizons')
 report={'input_manifest_sha256':sha(DIR/'checkpoint_manifest.json'),'execution_checkpoint_sha256':sha(arrfile),
 'decision_rows':len(pred),'securities':80,'path_seconds':round(t1-t0,4),'cost_seconds':round(t2-t1,4),
 'candidate_seconds_samples':[round(x,4) for x in samples], 'candidate_seconds_median':float(np.median(samples)),
 'benchmark_kind':'63-horizon real DEV80 evaluation of deterministic mask; NOT evolutionary GA throughput',
 'cpu_count_visible':os.cpu_count(),'dev37_accessed':False,'candidate_selection_frozen':False}
 (DIR/'benchmark_checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
