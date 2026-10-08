"""Isolated DEV80 parallel GA4; explicit frozen JSON budget."""
import argparse,hashlib,json,os
from pathlib import Path
import numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces
from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
from Core.layered_ga.ga4_conditional_runner import evaluate_conditional_candidate
from Core.layered_ga.stage2_evaluator_v3 import CurveEvaluation
from Core.layered_ga.ga4_catalog_store import append_record
from Core.layered_ga.ga4_optional_human_context import load_optional_context
from Core.layered_ga.ga4_resumable_parallel import run
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint'
STATE=None
STAGE1=ROOT/'Research/Runs/layered/stage1-context-map-20261007'
STAGE1_HASHES={'galaxy_context.parquet':'97f013734def96dcbc03b020d43f515490a375a76a6d529b06d53c7e747b8947','sector_context.parquet':'71c79ceb543a18ee9c706c8058589ae11447e3d62a6ba6ba3608ff7447e3ff4c'}

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
 # Human-semantic metadata is optional and cannot gate machine discovery.
 # The optional loader independently verifies the Stage 1 gate and hashes.
 linked,reference=load_optional_context(pred,STAGE1,STAGE1_HASHES,sha)
 # Missing or invalid human-semantic context is recorded, not a GA eligibility filter.
 STATE=(CausalSignalCompiler(pred),np.asarray(pred.eligible,dtype=bool),paths,costs,a['cluster_ids'],manifest['predictor_scope'],linked,reference)
 return STATE

def evaluate_side(chromosomes,side):
 if side not in ('LONG','SHORT'):raise ValueError('Invalid side')
 compiler,mask,paths,costs,clusters,provenance,linked,reference=initialize()
 r=evaluate_conditional_candidate(compiler=compiler,chromosomes=chromosomes,context_mask=mask,context={'scope':'DEV80_ELIGIBLE'},paths=paths,costs=costs,cluster_ids=clusters,fold='DEV80',data_provenance=provenance,side=side,stage1_context_frame=linked,stage1_reference=reference) if linked is not None else evaluate_conditional_candidate(compiler=compiler,chromosomes=chromosomes,context_mask=mask,context={'scope':'DEV80_ELIGIBLE'},paths=paths,costs=costs,cluster_ids=clusters,fold='DEV80',data_provenance=provenance,side=side)
 points=tuple({k:(float('nan') if v is None and k in ('ev_net','lcb95','mae_mean','mae_tail5') else v) for k,v in p.items()} for p in r['daily_horizon_evidence'])
 return CurveEvaluation(r['side'],points,tuple(r['pareto_horizons']),tuple(tuple(x) for x in r['pareto_ranges'])),r

def evaluate_long(chromosomes):
 return evaluate_side(chromosomes,'LONG')

def evaluate_short(chromosomes):
 return evaluate_side(chromosomes,'SHORT')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--budget',required=True);args=ap.parse_args()
 budget=json.loads(Path(args.budget).read_text())
 required={'seed','population_size','generations','workers','run_id','side'}
 if 'max_runtime_seconds' in budget:required.add('max_runtime_seconds')
 if set(budget)!=required:raise ValueError('Budget fields mismatch')
 if not str(budget['run_id']).replace('-','').replace('_','').isalnum():raise ValueError('Invalid run ID')
 side=budget['side']
 if side not in ('LONG','SHORT'):raise ValueError('Explicit LONG or SHORT side required')
 destination=SOURCE.parent/('ga4_parallel_'+budget['run_id']+'_'+side.lower());destination.mkdir(exist_ok=True)
 frozen=destination/'budget.json'
 if frozen.exists() and json.loads(frozen.read_text())!=budget:raise ValueError('Frozen budget changed')
 if not frozen.exists():
  with frozen.open('x') as f:json.dump(budget,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 source_files=['Core/layered_ga/ga4_resumable_parallel.py','Core/layered_ga/ga4_combination_genetics.py','Core/layered_ga/ga4_conditional_runner.py','Core/layered_ga/ga4_relationship_catalog.py','Core/layered_ga/ga4_candidate_context_evidence.py','Core/layered_ga/ga4_stage1_context_join.py','Core/layered_ga/ga4_optional_human_context.py','Core/layered_ga/ga4_discovery_evidence_policy.py','Core/layered_ga/ga4_causal_compiler.py','Core/layered_ga/stage2_evaluator_v3.py','Core/layered_ga/stage2_nsga2_engine_v3.py','Core/layered_ga/stage2_multiobjective_v3.py','Core/layered_ga/stage2_compiler_v3.py','scripts/run_ga4_parallel_dev80.py']
 identity={'fold':'DEV80','predictors_sha256':sha(SOURCE/'dev80_predictors.parquet'),'paths_sha256':sha(SOURCE/'dev80_execution_arrays.npz'),'stage1_metadata_status':initialize()[7],'budget':budget,'source_sha256':{p:sha(ROOT/p) for p in source_files}}
 provenance=destination/'frozen_provenance.json'
 if (destination/'generation_state.pkl').exists() and not provenance.exists():raise ValueError('Legacy checkpoint lacks frozen source provenance; do not resume')
 if provenance.exists():
  if json.loads(provenance.read_text())!=identity:raise ValueError('Source or data provenance changed')
 else:
  with provenance.open('x') as f:json.dump(identity,f,sort_keys=True,indent=2);f.flush();os.fsync(f.fileno())
 initialize()
 result=run(stage2_search_spaces(),evaluate_long if side=='LONG' else evaluate_short,seed=budget['seed'],population_size=budget['population_size'],generations=budget['generations'],workers=budget['workers'],checkpoint_dir=destination,identity=identity,persist=lambda record:append_record(destination/'candidate_catalog',record),max_runtime_seconds=budget.get('max_runtime_seconds'))
 print(json.dumps(result,default=str),flush=True)
if __name__=='__main__':main()
