#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,math,subprocess,sys
from collections import defaultdict
from pathlib import Path
from MTS_V4.universe_membership import load_membership_csv
from MTS_V4.universe_scientific_partition import ScientificCohort,load_frozen_partition

ORIGINAL={"AAPL","AMD","AMZN","BA","GOOGL","JPM","META","MSFT","NVDA","TSLA","XOM"}
SEED="MTS_DISCOVERY_2_SECTOR_CAP_STRATIFIED_20260930_V1"
BANDS=("LOWER_CURRENT_SP500_CAP_TERCILE","MIDDLE_CURRENT_SP500_CAP_TERCILE","UPPER_CURRENT_SP500_CAP_TERCILE")

def read_caps(path):
 with open(path,newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
 caps={str(r["security_id"]):float(r["market_cap"]) for r in rows}
 if len(caps)!=len(rows) or any(v<=0 for v in caps.values()): raise RuntimeError("invalid market-cap CSV")
 return caps

def allocate(strata,count):
 # Proportional Hamilton allocation over eligible Discovery-2 pool, then deterministic fill.
 total=sum(len(v) for v in strata.values()); q={k:count*len(v)/total for k,v in strata.items()}
 n={k:min(len(strata[k]),math.floor(q[k])) for k in strata}
 while sum(n.values())<count:
  eligible=[k for k in strata if n[k]<len(strata[k])]
  if not eligible: raise RuntimeError("cannot allocate requested sample")
  k=max(eligible,key=lambda z:(q[z]-n[z],len(strata[z]),str(z)))
  n[k]+=1
 return n

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--derived-market-root",required=True);p.add_argument("--universe-id",required=True)
 p.add_argument("--membership-csv",required=True);p.add_argument("--market-cap-csv",required=True)
 p.add_argument("--scientific-partition-manifest",required=True);p.add_argument("--output-dir",required=True)
 p.add_argument("--count",type=int,default=50);p.add_argument("--budget-per-family",type=int,default=500)
 p.add_argument("--seed",type=int,default=20260930);p.add_argument("--workers",type=int,default=8);a=p.parse_args()
 part=load_frozen_partition(a.scientific_partition_manifest)
 if part.universe_id!=a.universe_id: raise RuntimeError("partition universe mismatch")
 mem=load_membership_csv(a.membership_csv); intervals=mem.intervals()
 byid={x.security_id:x for x in intervals}
 if len(byid)!=len(intervals): raise RuntimeError("requires one current membership interval per security")
 caps=read_caps(a.market_cap_csv)
 missing=set(byid)-set(caps)
 if missing: raise RuntimeError(f"market caps missing {len(missing)} current members")
 ordered=sorted(byid,key=lambda sid:(caps[sid],sid)); size={}
 for i,sid in enumerate(ordered): size[sid]=BANDS[min(2,i*3//len(ordered))]
 strata=defaultdict(list)
 for sid in part.members(ScientificCohort.DISCOVERY):
  x=byid.get(sid)
  if not x or x.ticker.upper() in ORIGINAL: continue
  sector=str(x.sector_id or "UNCLASSIFIED")
  score=hashlib.sha256(f"{SEED}|{part.partition_id}|{sector}|{size[sid]}|{sid}".encode()).hexdigest()
  strata[(sector,size[sid])].append((score,x.ticker.upper(),sid))
 for v in strata.values(): v.sort()
 alloc=allocate(strata,a.count); chosen=[]
 for k in sorted(strata):
  for score,t,sid in strata[k][:alloc[k]]: chosen.append((k,score,t,sid))
 chosen.sort(key=lambda x:(x[0],x[1]))
 out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 counts=defaultdict(int)
 for (sector,band),_,_,_ in chosen: counts[(sector,band)]+=1
 manifest={"format":"MTS_V4_DISCOVERY_2_SECTOR_CAP_STRATIFIED_SAMPLE_V1",
  "selection_method":"proportional sector x relative-current-market-cap-tercile stratification within frozen Discovery cohort; deterministic SHA256 selection within strata; original 11 excluded",
  "selection_seed":SEED,"partition_id":part.partition_id,"universe_id":a.universe_id,"count":len(chosen),
  "size_definition":"terciles of current market cap within the 503-member current-S&P-500 calibration universe; NOT genuine small/mid/large-cap classifications",
  "market_cap_csv":str(Path(a.market_cap_csv).resolve()),"original_11":sorted(ORIGINAL),
  "stratum_allocation":[{"sector":k[0],"size_band":k[1],"eligible":len(strata[k]),"selected":alloc[k]} for k in sorted(strata)],
  "tickers":[{"ticker":t,"security_id":sid,"sector":k[0],"size_band":k[1],"current_market_cap":caps[sid],"selection_hash":score} for k,score,t,sid in chosen],
  "search_contract":{"families":8,"budget_per_family_per_optimizer":a.budget_per_family,"seed":a.seed,"workers":a.workers},
  "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
 mp=out/"MTS_DISCOVERY_2_STRATIFIED_50_SAMPLE_20260930.json"
 if mp.exists():
  prior=json.loads(mp.read_text())
  if prior!=manifest: raise RuntimeError("frozen Discovery-2 sample manifest mismatch")
 else: mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
 print(f"SAMPLE_MANIFEST={mp}");print(f"COUNT={len(chosen)}")
 print("SECTOR_COUNTS="+json.dumps({s:sum(v for (ss,_),v in counts.items() if ss==s) for s in sorted({k[0] for k in counts})},sort_keys=True))
 print("SIZE_COUNTS="+json.dumps({b:sum(v for (_,bb),v in counts.items() if bb==b) for b in BANDS},sort_keys=True))
 completed=0
 for i,(_,_,t,_) in enumerate(chosen,1):
  target=out/f"{t}_COMPUTATIONAL_SEARCH_20260930.json"
  if target.exists(): print(f"[{i}/{len(chosen)}] SKIP_COMPLETE={t}",flush=True);completed+=1;continue
  print(f"[{i}/{len(chosen)}] START={t}",flush=True)
  cmd=[sys.executable,"scripts/run_one_ticker_computational_search.py","--ticker",t,
   "--derived-market-root",a.derived_market_root,"--universe-id",a.universe_id,
   "--membership-csv",a.membership_csv,"--scientific-partition-manifest",a.scientific_partition_manifest,
   "--budget-per-family",str(a.budget_per_family),"--seed",str(a.seed),"--workers",str(a.workers),"--output",str(target)]
  subprocess.run(cmd,check=True);completed+=1;print(f"[{i}/{len(chosen)}] COMPLETE={t}",flush=True)
 print(f"DISCOVERY_2_SEARCH_COMPLETE={completed}/{len(chosen)}")
 print("CANDIDATE_SELECTION_MUTATED=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__": main()
