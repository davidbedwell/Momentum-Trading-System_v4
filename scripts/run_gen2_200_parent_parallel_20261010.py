#!/usr/bin/env python3
"""Gen2 entry-genome breeding: frozen 200 parents, nine original horizons, DEV80 only.
Deterministic offspring generation; six-process causal evaluation; no protected banks.
"""
import argparse, concurrent.futures, hashlib, json, pathlib, random, copy, os, sys
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
PARENTS=ROOT/'Research/Governance/GEN2_200_PARENT_FREEZE_20261009/frozen_200_parent_genomes.jsonl'
HORIZONS=(1,2,3,5,7,10,15,20,63)
PRED=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet'
ARRAY=ROOT/'Research/Runs/gen1-merit-screen-20261008/phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz'
WORKER=None
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def offspring(parents,count,seed):
 rng=random.Random(seed);known={digest((p['side'],p['chromosomes'])) for p in parents};result=[]
 for attempt in range(count*200):
  if len(result)>=count:break
  a,b=rng.sample(parents,2);side=a['side']
  # Cross family blocks only; do not blend incompatible gene schemas.
  genes={fam:copy.deepcopy(g) for fam,g in a['chromosomes']}
  donor={fam:g for fam,g in b['chromosomes']}
  shared=list(set(genes)&set(donor))
  if shared:
   fam=rng.choice(shared);genes[fam]=copy.deepcopy(donor[fam])
  elif rng.random()<.5:
   fam=rng.choice(list(donor));genes[fam]=copy.deepcopy(donor[fam])
  if rng.random()<.35 and len(genes)>1:del genes[rng.choice(list(genes))]
  if rng.random()<.35:
   fam=rng.choice(list(genes));g=genes[fam]
   nums=[k for k,v in g.items() if isinstance(v,(int,float)) and not isinstance(v,bool) and ('quantile' in k or 'threshold' in k)]
   if nums:
    k=rng.choice(nums);v=g[k]
    if isinstance(v,float):g[k]=round(max(0,min(1,v+rng.choice((-1,1))*.05)),6)
    # Integer and categorical domains are kept unchanged until their schema is audited.
  child=sorted(genes.items())
  key=digest((side,child))
  if key in known:continue
  known.add(key)
  result.append({'offspring_id':len(result)+1,'side':side,'chromosomes':child,'parent_indices':[a['index'],b['index']],'genome_hash':key,'seed':seed})
 if len(result)!=count:raise RuntimeError(f'Only {len(result)} unique offspring after {attempt+1} attempts; no silent shortfall')
 return result
def init_worker():
 global WORKER
 import pandas as pd
 from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
 from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
 from Core.layered_ga.stage2_evaluator_v3 import evaluate_curve
 frame=pd.read_parquet(PRED);data=np.load(ARRAY)
 paths=ExecutionPaths(*(data[k] for k in ('endpoint_return','low_excursion','high_excursion','calendar_days')))
 costs=ProspectiveCosts(*(data[k] for k in ('long_roundtrip','short_roundtrip','spread_bps','impact_bps','adv_dollars','regulatory_sell_fraction')))
 WORKER=(CausalSignalCompiler(frame),paths,costs,data['cluster_ids'],evaluate_curve)
def evaluate(child):
 compiler,paths,costs,clusters,curve=WORKER
 try:
  mask=np.logical_and.reduce([compiler.compile(fam,gene) for fam,gene in child['chromosomes']])
  points=curve(mask,paths,costs,child['side'],clusters,horizons=HORIZONS).points
  return {'offspring_id':child['offspring_id'],'genome_hash':child['genome_hash'],'status':'EVALUATED_UNCERTIFIED','points':points}
 except Exception as e:
  return {'offspring_id':child['offspring_id'],'genome_hash':child['genome_hash'],'status':'REJECTED_COMPILER_OR_EVALUATION','error':repr(e)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--count',type=int,default=1200);ap.add_argument('--workers',type=int,default=6);ap.add_argument('--seed',type=int,default=20261010);ap.add_argument('--generate-only',action='store_true');args=ap.parse_args()
 if args.workers!=6:raise ValueError('Frozen 6-CPU execution request')
 parents=[json.loads(line) for line in PARENTS.open()]
 assert len(parents)==200 and len({p['index'] for p in parents})==200
 out=ROOT/'Research/Runs/gen2-200-parent-20261010';out.mkdir(parents=True,exist_ok=True)
 manifest={'status':'GEN2_OFFSPRING_GENERATED_EVALUATION_PENDING','parents':200,'offspring_requested':args.count,'seed':args.seed,'workers':6,'horizons':HORIZONS,'scope':'DEV80_ONLY','protected_banks_accessed':False,'source_sha256':hashlib.sha256(PARENTS.read_bytes()).hexdigest(),'design_status':'EXPLORATORY_NOT_CERTIFIED','genome_mutation':'shared-family crossover; optional family add/remove; bounded float threshold mutation; compiler rejection recorded'}
 mp=out/'manifest.json'
 if (out/'offspring.jsonl').exists():
  old=json.loads(mp.read_text())
  assert old['seed']==args.seed and old['offspring_requested']==args.count and old['source_sha256']==manifest['source_sha256']
  children=[json.loads(x) for x in (out/'offspring.jsonl').open()]
 else:
  children=offspring(parents,args.count,args.seed)
  with (out/'offspring.jsonl').open('w') as f:
   for c in children:f.write(json.dumps(c)+'\n')
  mp.write_text(json.dumps(manifest,indent=2))
 print('GENERATED',len(children),'PARENTS',len(parents),flush=True)
 if args.generate_only:return
 missing=[str(p) for p in (PRED,ARRAY) if not p.exists()]
 if missing:raise FileNotFoundError('DEV80 evaluation cache missing: '+', '.join(missing))
 result_file=out/'evaluations.jsonl'
 done={json.loads(x)['offspring_id'] for x in result_file.open()} if result_file.exists() else set()
 todo=[x for x in children if x['offspring_id'] not in done]
 with concurrent.futures.ProcessPoolExecutor(max_workers=6,initializer=init_worker) as pool,result_file.open('a') as f:
  for i,r in enumerate(pool.map(evaluate,todo,chunksize=1),1):
   f.write(json.dumps(r,allow_nan=True)+'\n');f.flush()
   if i%25==0:print('EVALUATED',len(done)+i,'/',len(children),flush=True)
 manifest['status']='GEN2_EVALUATION_COMPLETE_UNCERTIFIED';mp.write_text(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
