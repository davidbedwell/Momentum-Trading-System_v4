#!/usr/bin/env python3
"""Reevaluate top Gen2 genomes across all 13 windows, DEV80 only."""
import argparse,concurrent.futures,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from reevaluate_horizon_parents_20261010 import init,evaluate,OUT
def main():
 p=argparse.ArgumentParser();p.add_argument("--top",type=int,default=30);p.add_argument("--workers",type=int,default=4);a=p.parse_args()
 records=[json.loads(s) for s in (OUT/"gen2_reconciled_ranked_candidates.jsonl").open()]
 tasks=[]
 for r in records[:a.top]:
  for start,end in [(2,5)]+[(i,i+4) for i in range(6,62,5)]:
   tasks.append({"window":[start,end],"source_file":"gen2-200-parent-20261010/offspring.jsonl",
    "source_index":r["offspring_id"],"generation":2,"side":r["side"],"genome_hash":r["genome_hash"],
    "chromosomes":r["chromosomes"],"original_priority":r["overall_priority"]})
 result=OUT/"gen2_window_reevaluations.jsonl"
 done=set()
 if result.exists():
  for s in result.open():
   r=json.loads(s);done.add((r["source_index"],tuple(r["window"])))
 todo=[t for t in tasks if (t["source_index"],tuple(t["window"])) not in done]
 print("TOP",a.top,"TASKS",len(tasks),"TODO",len(todo),flush=True)
 if not todo:return
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers,initializer=init) as pool,result.open("a") as f:
  for i,r in enumerate(pool.map(evaluate,todo,chunksize=1),1):
   f.write(json.dumps(r,allow_nan=True)+"\n");f.flush()
   if i%20==0:print("DONE",i,flush=True)
if __name__=="__main__":main()