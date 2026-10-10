#!/usr/bin/env python3
"""Independent calendar-episode diagnostics on DEV80, not validation certification."""
import argparse,json,pathlib,sys,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from reevaluate_horizon_parents_20261010 import init,evaluate,OUT
EPISODES={"GFC_2007_2009":("2007-07-01","2009-06-30"),"COVID_2020":("2020-02-01","2020-06-30"),"BEAR_2022":("2022-01-01","2022-12-31")}
def worker(task):
 import numpy as np,pandas as pd
 import reevaluate_horizon_parents_20261010 as base
 compiler,paths,costs,clusters,curve=base.CTX
 from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
 start,end=EPISODES[task["episode"]]
 dates=pd.to_datetime(compiler.frame["effective_date"]) if hasattr(compiler,"frame") else None
 if dates is None:raise ValueError("compiler.frame missing; check attribute")
 epoch=((dates>=start)&(dates<=end)).to_numpy()
 try:
  signal=np.logical_and.reduce([compiler.compile(f,g) for f,g in task["chromosomes"]]) & epoch
  points=curve(signal,paths,costs,task["side"],clusters,min_effective_n=20,horizons=(task["horizon"],)).points
  return {k:v for k,v in task.items() if k!="chromosomes"}|{"points":points,"status":"DIAGNOSTIC_NOT_CERTIFIED"}
 except Exception as exc:return {k:v for k,v in task.items() if k!="chromosomes"}|{"status":"ERROR","error":repr(exc)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--top-per-window",type=int,default=5);ap.add_argument("--workers",type=int,default=4);args=ap.parse_args()
 selected=[json.loads(s) for s in (OUT/"cross_generation_window_rankings.jsonl").open()]
 originals={r["gen1_index"]:r for r in (json.loads(s) for s in (OUT/"gen1_parent_definitions.jsonl").open())}
 offspring={r["offspring_id"]:r for r in (json.loads(s) for s in (OUT/"gen2_reconciled_ranked_candidates.jsonl").open())}
 tasks=[]
 for r in selected:
  if r["provisional_rank"]>args.top_per_window:continue
  genes=(originals if r["generation"]==1 else offspring)[r["id"]]["chromosomes"]
  for ep in EPISODES:
   tasks.append({"episode":ep,"window":r["window"],"generation":r["generation"],"id":r["id"],"side":r["side"],"horizon":r["window"][1],"chromosomes":genes})
 output=OUT/"market_episode_diagnostics.jsonl"
 print("TASKS",len(tasks),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers,initializer=init) as pool,output.open("w") as f:
  for result in pool.map(worker,tasks,chunksize=1):f.write(json.dumps(result,allow_nan=True)+"\n")
 print("DONE",len(tasks),flush=True)
if __name__=="__main__":main()