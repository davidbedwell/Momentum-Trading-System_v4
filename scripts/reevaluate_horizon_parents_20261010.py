#!/usr/bin/env python3
"""Causal DEV80 re-evaluation of archived genome-window assignments.

No GA evolution, protected banks, or parent promotion here. Outputs are
uncertified descriptive evidence until multiplicity and episode tests pass.
"""
import argparse,hashlib,json,pathlib,concurrent.futures
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
ARCH=ROOT/"Research/Preparation/horizon_generational_20261010/Research/Runs/gen1-merit-screen-20261008/holding_window_chromosome_archive_20261009"
PRED=ROOT/"Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet"
ARRAY=ROOT/"Research/Runs/gen1-merit-screen-20261008/phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz"
OUT=ROOT/"Research/Preparation/horizon_generational_20261010/parent_study"
CTX=None
def init():
 global CTX
 import pandas as pd
 from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
 from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
 from Core.layered_ga.stage2_evaluator_v3 import evaluate_curve
 frame=pd.read_parquet(PRED);d=np.load(ARRAY)
 paths=ExecutionPaths(*(d[k] for k in ('endpoint_return','low_excursion','high_excursion','calendar_days')))
 costs=ProspectiveCosts(*(d[k] for k in ('long_roundtrip','short_roundtrip','spread_bps','impact_bps','adv_dollars','regulatory_sell_fraction')))
 CTX=(CausalSignalCompiler(frame),paths,costs,d['cluster_ids'],evaluate_curve)
def evaluate(task):
 compiler,paths,costs,clusters,curve=CTX
 a,b=task["window"]
 try:
  mask=np.logical_and.reduce([compiler.compile(f,g) for f,g in task["chromosomes"]])
  pts=curve(mask,paths,costs,task["side"],clusters,min_effective_n=30,horizons=tuple(range(a,b+1))).points
  return {k:v for k,v in task.items() if k!="chromosomes"}|{"status":"EVALUATED_UNCERTIFIED","points":pts}
 except Exception as e:
  return {k:v for k,v in task.items() if k!="chromosomes"}|{"status":"REJECTED","error":repr(e)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--workers",type=int,default=4);ap.add_argument("--limit",type=int,default=0);args=ap.parse_args()
 if not 1<=args.workers<=16:raise ValueError("worker bound")
 OUT.mkdir(parents=True,exist_ok=True)
 tasks=[]
 for f in sorted(ARCH.glob("window_*_chromosomes.json")):
  d=json.loads(f.read_text())
  for g in d["genomes"]:
   h=hashlib.sha256(json.dumps([g["side"],g["chromosomes"]],sort_keys=True,separators=(",",":")).encode()).hexdigest()
   tasks.append({"window":d["window"],"source_file":f.name,"source_index":g["index"],"side":g["side"],"genome_hash":h,"chromosomes":g["chromosomes"]})
 result=OUT/"window_reevaluations.jsonl"
 done=set()
 if result.exists():
  for line in result.open():
   r=json.loads(line);done.add((tuple(r["window"]),r["genome_hash"]))
 todo=[t for t in tasks if (tuple(t["window"]),t["genome_hash"]) not in done]
 if args.limit:todo=todo[:args.limit]
 print("TASKS",len(tasks),"ALREADY_DONE",len(done),"TO_RUN",len(todo),flush=True)
 if not todo:return
 with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers,initializer=init) as pool,result.open("a") as f:
  for i,r in enumerate(pool.map(evaluate,todo,chunksize=1),1):
   f.write(json.dumps(r,allow_nan=True)+"\n");f.flush()
   if i%10==0:print("COMPLETED",i,flush=True)
 print("REEVALUATION_BATCH_COMPLETE",len(todo),flush=True)
if __name__=="__main__":main()
