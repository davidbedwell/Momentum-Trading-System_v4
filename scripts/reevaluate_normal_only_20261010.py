#!/usr/bin/env python3
"""Normal-only DEV80 reranking: fixed calendar exclusions, immutable original files."""
import argparse,concurrent.futures,hashlib,json,pathlib,sys
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import reevaluate_horizon_parents_20261010 as base
INTERVALS=(("2007-07-01","2009-06-30"),("2020-02-01","2020-06-30"),("2022-01-01","2022-12-31"))
OUT=ROOT/"Research/Preparation/horizon_generational_20261010/normal_only"
MASK=None
def init():
 global MASK
 base.init()
 import pandas as pd
 dates=pd.to_datetime(base.CTX[0].frame["effective_date"])
 bad=np.zeros(len(dates),dtype=bool)
 for start,end in INTERVALS:bad|=((dates>=start)&(dates<=end)).to_numpy()
 MASK=~bad
def evaluate(task):
 compiler,paths,costs,clusters,curve=base.CTX
 a,b=task["window"]
 try:
  signal=np.logical_and.reduce([compiler.compile(f,g) for f,g in task["chromosomes"]])
  signal &= MASK
  pts=curve(signal,paths,costs,task["side"],clusters,min_effective_n=30,horizons=tuple(range(a,b+1))).points
  return {k:v for k,v in task.items() if k!="chromosomes"}|{"status":"NORMAL_ONLY_EXPLORATORY","points":pts,"eligible_entry_rows":int(MASK.sum()),"exclusion_policy":"ENTRY_DATE_ONLY_BOUNDARY_EXPOSURES_UNRESOLVED"}
 except Exception as exc:return {k:v for k,v in task.items() if k!="chromosomes"}|{"status":"ERROR","error":repr(exc)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--workers",type=int,default=2);p.add_argument("--limit",type=int,default=0);a=p.parse_args()
 if not 1<=a.workers<=8:raise ValueError("workers")
 OUT.mkdir(parents=True,exist_ok=True)
 g1={r["gen1_index"]:r for r in (json.loads(s) for s in (base.OUT/"gen1_parent_definitions.jsonl").open())}
 g2={r["offspring_id"]:r for r in (json.loads(s) for s in (base.OUT/"gen2_reconciled_ranked_candidates.jsonl").open())}
 tasks=[]
 for gen,file,bank in ((1,"window_reevaluations.jsonl",g1),(2,"gen2_window_reevaluations.jsonl",g2)):
  for s in (base.OUT/file).open():
   r=json.loads(s)
   if r["status"]!="EVALUATED_UNCERTIFIED":continue
   tasks.append({"generation":gen,"source_index":r["source_index"],"window":r["window"],"side":r["side"],"genome_hash":r["genome_hash"],"chromosomes":bank[r["source_index"]]["chromosomes"]})
 result=OUT/"normal_only_reevaluations.jsonl"
 done=set()
 if result.exists():
  for s in result.open():
   r=json.loads(s);done.add((r["generation"],r["source_index"],tuple(r["window"])))
 tasks=[t for t in tasks if (t["generation"],t["source_index"],tuple(t["window"])) not in done]
 if a.limit:tasks=tasks[:a.limit]
 print("TASKS",len(tasks),"PREVIOUS",len(done),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers,initializer=init) as pool,result.open("a") as f:
  for i,r in enumerate(pool.map(evaluate,tasks,chunksize=1),1):
   f.write(json.dumps(r,allow_nan=True)+"\n");f.flush()
   if i%100==0:print("DONE",i,flush=True)
 print("COMPLETE",len(tasks),flush=True)
if __name__=="__main__":main()