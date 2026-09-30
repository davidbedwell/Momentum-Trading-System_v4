#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ALGO="MTS_V4_A1_METADATA_ONLY_BALANCED_SHA256_V1"
def tie(seed,*x): return hashlib.sha256("|".join((seed,)+tuple(map(str,x))).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for x in ("partition","sectors","market-caps","protocol","output"):p.add_argument("--"+x,required=True)
 p.add_argument("--seed",default="MTS-A1-20260930");a=p.parse_args()
 ph=hashlib.sha256(Path(a.protocol).read_bytes()).hexdigest()
 d=json.loads(Path(a.partition).read_text());pool=None
 cohorts=d.get("cohorts")
 if isinstance(cohorts,dict) and isinstance(cohorts.get("VERIFICATION_A"),list):
  pool=cohorts["VERIFICATION_A"]
 if pool is None:
  for k,v in d.items():
   if k.lower().replace("_","") in ("verificationa","verificationatickers") and isinstance(v,list):pool=v;break
 if pool is None: raise RuntimeError("Verification A list not found")
 def tk(x): return x if isinstance(x,str) else x.get("ticker") or x.get("symbol")
 names={tk(x) for x in pool};names.discard(None)
 if len(names)!=100:raise RuntimeError(f"expected 100 names, got {len(names)}")
 with open(a.sectors,newline="") as f: sm={r["ticker"]:r.get("sector") or r.get("sector_id") for r in csv.DictReader(f)}
 with open(a.market_caps,newline="") as f: rr=list(csv.DictReader(f))
 cm={}
 for r in rr:
  t=r.get("ticker") or r.get("symbol");v=r.get("market_cap") or r.get("market_cap_usd")
  if t in names and v not in ("",None):cm[t]=float(v)
 miss=sorted(t for t in names if not sm.get(t) or t not in cm)
 if miss:raise RuntimeError("missing metadata: "+",".join(miss))
 rows=[{"ticker":t,"sector":sm[t],"market_cap":cm[t]} for t in sorted(names)]
 vals=sorted((r["market_cap"],r["ticker"]) for r in rows);rank={t:i for i,(_,t) in enumerate(vals)}
 for r in rows:
  i=rank[r["ticker"]];r["size_band"]=("LOWER" if i<100/3 else ("MIDDLE" if i<200/3 else "UPPER"))+"_CURRENT_SP500_CAP_TERCILE"
 by=defaultdict(list)
 for r in rows:by[r["sector"]].append(r)
 chosen=[];used=set();bc=Counter()
 for s in sorted(by,key=lambda s:(len(by[s]),s)):
  r=min(by[s],key=lambda r:(bc[r["size_band"]],tie(a.seed,"sector",s,r["ticker"])))
  chosen.append(r);used.add(r["ticker"]);bc[r["size_band"]]+=1
 sc=Counter(r["sector"] for r in chosen)
 while len(chosen)<20:
  r=min((r for r in rows if r["ticker"] not in used),key=lambda r:(sc[r["sector"]],bc[r["size_band"]],tie(a.seed,"fill",r["ticker"])))
  chosen.append(r);used.add(r["ticker"]);sc[r["sector"]]+=1;bc[r["size_band"]]+=1
 chosen=sorted(chosen,key=lambda r:r["ticker"]);remain=sorted((r for r in rows if r["ticker"] not in used),key=lambda r:r["ticker"])
 out={"format":"MTS_V4_VERIFICATION_A1_FROZEN_SELECTION_V1","algorithm":ALGO,"seed":a.seed,"protocol_sha256":ph,"partition_source":a.partition,"a1":chosen,"verification_a_remaining":remain,"outcomes_accessed":False,"predictors_accessed":False,"prices_accessed":False,"search_run":False,"verification_b_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("PROTOCOL_SHA256="+ph);print("A1_COUNT=20");print("A1="+",".join(r["ticker"] for r in chosen));print("A1_SECTORS="+json.dumps(dict(sorted(Counter(r["sector"] for r in chosen).items()))));print("A1_SIZE_BANDS="+json.dumps(dict(sorted(Counter(r["size_band"] for r in chosen).items()))));print("VERIFICATION_A_REMAINING=80");print("OUTCOMES_ACCESSED=False");print("PREDICTORS_ACCESSED=False");print("PRICES_ACCESSED=False");print("SEARCH_RUN=False");print("VERIFICATION_B_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
