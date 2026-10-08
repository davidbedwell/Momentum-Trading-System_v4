"""Isolated DEV80 parallel GA4; explicit frozen JSON budget."""
import argparse,hashlib,json,os
from pathlib import Path
import numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces
from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
from Core.layered_ga.ga4_conditional_runner import evaluate_conditional_candidate
from Core.layered_ga.stage2_evaluator_v3 import CurveEvaluation
from Core.layered_ga.ga4_resumable_parallel import run
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint'
STATE=None

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()

def initialize():
 global STATE
 if STATE is not None:return STATE
 manifest=json.loads((SOURCE/'checkpoint_manifest.json').read_text())
 for file,key in [('dev80_predictors.parquet','predictors_sha256'),('dev80_raw.parquet','raw_sha256')]:
  if sha(SOURCE/file)!=manifest[key]:raise ValueError('Source hash mismatch: '+file)
 if manifest['dev37_opened'] is not False:raise ValueError('DEV37 isolation violated')
 pred=pd.read_parquet(SOURCE/'dev80_predictors.parquet')
 if pred.security_id.astype(str).nunique()!=80:raise ValueError('DEV80 scope mismatch')
 with np.load(SOURCE/'dev80_execution_arrays.npz') as z:a={k:z[k] for k in z.files}
 paths=ExecutionPaths(**{k:a[k] for k in ('endpoint_return','low_excursion','high_excursion','calendar_days')})
 costs=ProspectiveCosts(**{k:a[k] for k in ('long_roundtrip','short_roundtrip','spread_bps','impact_bps','adv_dollars','regulatory_sell_fraction')})
 if len(pred)!=len(paths.endpoint_return) or len(pred)!=len(a['cluster_ids']):raise ValueError('Array alignment mismatch')
 STATE=(CausalSignalCompiler(pred),np.asarray(pred.eligible,dtype=bool),paths,costs,a['cluster_ids'],manifest['predictor_scope'])
 return STATE

def evaluate(chromosomes):
 compiler,mask,paths,costs,clusters,provenance=initialize()
 r=evaluate_conditional_candidate(compiler=compiler,chromosomes=chromosomes,context_mask=mask,context={'scope':'DEV80_ELIGIBLE'},paths=paths,costs=costs,cluster_ids=clusters,fold='DEV80',data_provenance=provenance)
 points=tuple({k:(float('nan') if v is None and k in ('ev_net','lcb95','mae_mean','mae_tail5') else v) for k,v in p.items()} for p in r['daily_horizon_evidence'])
 return CurveEvaluation(r['side'],points,tuple(r['pareto_horizons']),tuple(tuple(x) for x in r['pareto_ranges']))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--budget',required=True);args=ap.parse_args()
 budget=json.loads(Path(args.budget).read_text())
 required={'seed','population_size','generations','workers','run_id'}
 if set(budget)!=required:raise ValueError('Budget fields mismatch')
 if not str(budget['run_id']).replace('-','').replace('_','').isalnum():raise ValueError('Invalid run ID')
 destination=SOURCE.parent/('ga4_parallel_'+budget['run_id']);destination.mkdir(exist_ok=True)
 frozen=destination/'budget.json'
 if frozen.exists() and json.loads(frozen.read_text())!=budget:raise ValueError('Frozen budget changed')
 if not frozen.exists():
  with frozen.open('x') as f:json.dump(budget,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 identity={'fold':'DEV80','predictors_sha256':sha(SOURCE/'dev80_predictors.parquet'),'paths_sha256':sha(SOURCE/'dev80_execution_arrays.npz'),'budget':budget}
 initialize()
 result=run(stage2_search_spaces(),evaluate,seed=budget['seed'],population_size=budget['population_size'],generations=budget['generations'],workers=budget['workers'],checkpoint_dir=destination,identity=identity)
 print(json.dumps(result,default=str),flush=True)
if __name__=='__main__':main()