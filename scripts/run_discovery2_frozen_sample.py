#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,subprocess,sys
from pathlib import Path
from MTS_V4.universe_membership import load_membership_csv
from MTS_V4.universe_scientific_partition import ScientificCohort,load_frozen_partition

ORIGINAL={"AAPL","AMD","AMZN","BA","GOOGL","JPM","META","MSFT","NVDA","TSLA","XOM"}
SEED="MTS_DISCOVERY_2_20260930_V1"
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--derived-market-root",required=True);p.add_argument("--universe-id",required=True)
 p.add_argument("--membership-csv",required=True);p.add_argument("--scientific-partition-manifest",required=True)
 p.add_argument("--output-dir",required=True);p.add_argument("--count",type=int,default=50)
 p.add_argument("--budget-per-family",type=int,default=500);p.add_argument("--seed",type=int,default=20260930)
 p.add_argument("--workers",type=int,default=8);a=p.parse_args()
 part=load_frozen_partition(a.scientific_partition_manifest)
 if part.universe_id!=a.universe_id: raise RuntimeError("partition universe mismatch")
 mem=load_membership_csv(a.membership_csv)
 sid_to_ticker={}
 for x in mem.intervals(): sid_to_ticker.setdefault(x.security_id,x.ticker.upper())
 pool=[]
 for sid in part.members(ScientificCohort.DISCOVERY):
  t=sid_to_ticker.get(sid)
  if t and t not in ORIGINAL:
   score=hashlib.sha256(f"{SEED}|{part.partition_id}|{sid}".encode()).hexdigest()
   pool.append((score,t,sid))
 pool.sort()
 chosen=pool[:a.count]
 if len(chosen)!=a.count: raise RuntimeError(f"only {len(chosen)} eligible Discovery-2 names")
 out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 manifest={"format":"MTS_V4_DISCOVERY_2_FROZEN_SAMPLE_V1","selection_method":"deterministic SHA256 sample from frozen Discovery cohort; excludes original 11","selection_seed":SEED,
 "partition_id":part.partition_id,"universe_id":a.universe_id,"count":a.count,"original_11":sorted(ORIGINAL),
 "tickers":[{"ticker":t,"security_id":sid,"selection_hash":score} for score,t,sid in chosen],
 "search_contract":{"families":8,"budget_per_family_per_optimizer":a.budget_per_family,"seed":a.seed,"workers":a.workers},
 "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
 mp=out/"MTS_DISCOVERY_2_FROZEN_50_SAMPLE_20260930.json";mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
 print(f"SAMPLE_MANIFEST={mp}");print("TICKERS="+",".join(t for _,t,_ in chosen));print(f"COUNT={len(chosen)}")
 completed=0
 for i,(_,t,_) in enumerate(chosen,1):
  target=out/f"{t}_COMPUTATIONAL_SEARCH_20260930.json"
  if target.exists():
   print(f"[{i}/{len(chosen)}] SKIP_COMPLETE={t}",flush=True);completed+=1;continue
  print(f"[{i}/{len(chosen)}] START={t}",flush=True)
  cmd=[sys.executable,"scripts/run_one_ticker_computational_search.py","--ticker",t,
   "--derived-market-root",a.derived_market_root,"--universe-id",a.universe_id,
   "--membership-csv",a.membership_csv,"--scientific-partition-manifest",a.scientific_partition_manifest,
   "--budget-per-family",str(a.budget_per_family),"--seed",str(a.seed),"--workers",str(a.workers),
   "--output",str(target)]
  subprocess.run(cmd,check=True);completed+=1
  print(f"[{i}/{len(chosen)}] COMPLETE={t}",flush=True)
 print(f"DISCOVERY_2_SEARCH_COMPLETE={completed}/{len(chosen)}")
 print("CANDIDATE_SELECTION_MUTATED=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__": main()
