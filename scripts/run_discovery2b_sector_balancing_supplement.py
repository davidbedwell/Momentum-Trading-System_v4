#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
from MTS_V4.universe_membership import load_membership_csv
from MTS_V4.universe_scientific_partition import ScientificCohort,load_frozen_partition

SEED="MTS_DISCOVERY_2B_SECTOR_BALANCE_20260930_V1"
BANDS=("LOWER_CURRENT_SP500_CAP_TERCILE","MIDDLE_CURRENT_SP500_CAP_TERCILE","UPPER_CURRENT_SP500_CAP_TERCILE")
ORIGINAL={"AAPL","AMD","AMZN","BA","GOOGL","JPM","META","MSFT","NVDA","TSLA","XOM"}

def read_csv_map(path,key,value,cast=str):
 with open(path,newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
 return {str(r[key]).strip():cast(r[value]) for r in rows}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--existing-classification",required=True);p.add_argument("--membership-csv",required=True)
 p.add_argument("--sector-csv",required=True);p.add_argument("--market-cap-csv",required=True)
 p.add_argument("--scientific-partition-manifest",required=True);p.add_argument("--derived-market-root",required=True)
 p.add_argument("--universe-id",required=True);p.add_argument("--output-dir",required=True)
 p.add_argument("--target-per-sector",type=int,default=5);p.add_argument("--budget-per-family",type=int,default=500)
 p.add_argument("--seed",type=int,default=20260930);p.add_argument("--workers",type=int,default=8);a=p.parse_args()
 existing=json.loads(Path(a.existing_classification).read_text()); part=load_frozen_partition(a.scientific_partition_manifest)
 mem=load_membership_csv(a.membership_csv); byid={x.security_id:x for x in mem.intervals()}
 sectors=read_csv_map(a.sector_csv,"security_id","sector"); caps=read_csv_map(a.market_cap_csv,"security_id","market_cap",float)
 ordered=sorted(byid,key=lambda sid:(caps[sid],sid)); band={}
 for i,sid in enumerate(ordered): band[sid]=BANDS[min(2,i*3//len(ordered))]
 used={x["ticker"] for x in existing["tickers"]}|ORIGINAL
 current=Counter(x["sector"] for x in existing["tickers"]); current_cell=Counter((x["sector"],x["size_band"]) for x in existing["tickers"])
 pools=defaultdict(list)
 for sid in part.members(ScientificCohort.DISCOVERY):
  x=byid.get(sid)
  if not x or x.ticker.upper() in used: continue
  sec=sectors.get(sid)
  if not sec: raise RuntimeError(f"missing sector {sid}")
  score=hashlib.sha256(f"{SEED}|{part.partition_id}|{sec}|{band[sid]}|{sid}".encode()).hexdigest()
  pools[sec].append((score,x.ticker.upper(),sid,band[sid],caps[sid]))
 for sec in pools: pools[sec].sort()
 chosen=[]
 for sec in sorted(set(sectors.values())):
  need=max(0,a.target_per_sector-current.get(sec,0))
  local=list(pools.get(sec,[]))
  for _ in range(need):
   if not local: raise RuntimeError(f"insufficient Discovery names for {sec}")
   # Prefer the currently least represented cap tercile within this sector; deterministic hash breaks ties.
   minc=min(current_cell[(sec,b)] for b in BANDS)
   eligible=[x for x in local if current_cell[(sec,x[3])]==minc] or local
   pick=min(eligible,key=lambda x:x[0]); local.remove(pick); chosen.append((sec,*pick)); current_cell[(sec,pick[3])]+=1; current[sec]+=1
 out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 manifest={"format":"MTS_V4_DISCOVERY_2B_SECTOR_BALANCING_SUPPLEMENT_V1","selection_seed":SEED,
  "selection_method":"minimum untouched Discovery supplement to reach sector floor; within each sector prefer least represented cap tercile, deterministic SHA256 tie-break",
  "target_per_sector":a.target_per_sector,"count":len(chosen),"partition_id":part.partition_id,
  "tickers":[{"sector":sec,"ticker":t,"security_id":sid,"size_band":b,"current_market_cap":cap,"selection_hash":score}
             for sec,score,t,sid,b,cap in chosen],
  "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
 mp=out/"MTS_DISCOVERY_2B_SECTOR_BALANCING_SUPPLEMENT_20260930.json";mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
 print(f"MANIFEST={mp}");print(f"COUNT={len(chosen)}");print("TICKERS="+",".join(x[2] for x in chosen))
 for i,(sec,score,t,sid,b,cap) in enumerate(chosen,1):
  target=out/f"{t}_COMPUTATIONAL_SEARCH_20260930.json"
  if target.exists(): print(f"[{i}/{len(chosen)}] SKIP_COMPLETE={t}");continue
  cmd=[sys.executable,"scripts/run_one_ticker_computational_search.py","--ticker",t,
   "--derived-market-root",a.derived_market_root,"--universe-id",a.universe_id,
   "--membership-csv",a.membership_csv,"--scientific-partition-manifest",a.scientific_partition_manifest,
   "--budget-per-family",str(a.budget_per_family),"--seed",str(a.seed),"--workers",str(a.workers),"--output",str(target)]
  subprocess.run(cmd,check=True);print(f"[{i}/{len(chosen)}] COMPLETE={t}",flush=True)
 print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
