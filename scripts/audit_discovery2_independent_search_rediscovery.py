#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import Counter,defaultdict
from pathlib import Path

FAMILIES=("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE")

def top_unique(report,fam):
 seen=set();out=[]
 for opt in ("random","ga"):
  for c in report["families"][fam][opt]["top_candidates"]:
   cid=c["candidate_id"]
   if cid in seen:continue
   seen.add(cid);out.append(c)
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument("--d2-dir",required=True);p.add_argument("--d2b-dir",required=True);p.add_argument("--d2-classification",required=True);p.add_argument("--d2b-manifest",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 meta={}
 d2=json.loads(Path(a.d2_classification).read_text())
 for x in d2["tickers"]:meta[x["ticker"]]={"cohort":"D2_50","sector":x["sector"],"size_band":x["size_band"]}
 d2b=json.loads(Path(a.d2b_manifest).read_text())
 for x in d2b["tickers"]:meta[x["ticker"]]={"cohort":"D2B_SUPPLEMENT","sector":x["sector"],"size_band":x["size_band"]}
 rows=[];missing=[]
 for ticker,m in sorted(meta.items()):
  base=Path(a.d2_dir) if m["cohort"]=="D2_50" else Path(a.d2b_dir);f=base/f"{ticker}_COMPUTATIONAL_SEARCH_20260930.json"
  if not f.exists():missing.append(str(f));continue
  r=json.loads(f.read_text())
  if r.get("cohort")!="DISCOVERY":raise RuntimeError("non-Discovery search encountered")
  for fam in FAMILIES:
   cs=top_unique(r,fam)
   pos=[c for c in cs if c["metrics"].get("sample_size",0)>=10 and c["metrics"].get("mean_forward_return",0)>0 and c["metrics"].get("median_forward_return",0)>0]
   best=max(cs,key=lambda c:c["metrics"]["search_fitness"]) if cs else None
   rows.append({"ticker":ticker,**m,"family":fam,"unique_top_candidates":len(cs),"retained_positive_n10":len(pos),
    "has_retained_positive_n10":bool(pos),"best_candidate_id":best["candidate_id"] if best else None,
    "best_metrics":best["metrics"] if best else None})
 if missing:raise RuntimeError("missing search reports: "+",".join(missing))
 byfam=[]
 for fam in FAMILIES:
  fr=[r for r in rows if r["family"]==fam];yes=[r for r in fr if r["has_retained_positive_n10"]]
  bysec=defaultdict(lambda:[0,0]);bysize=defaultdict(lambda:[0,0]);byco=defaultdict(lambda:[0,0])
  for r in fr:
   for g,k in ((bysec,r["sector"]),(bysize,r["size_band"]),(byco,r["cohort"])):
    g[k][1]+=1;g[k][0]+=int(r["has_retained_positive_n10"])
  byfam.append({"family":fam,"tickers_with_retained_positive_n10":len(yes),"tickers_total":len(fr),
   "fraction":len(yes)/len(fr) if fr else None,
   "retained_positive_candidate_instances":sum(r["retained_positive_n10"] for r in fr),
   "by_cohort":{k:{"positive":v[0],"total":v[1]} for k,v in sorted(byco.items())},
   "by_sector":{k:{"positive":v[0],"total":v[1]} for k,v in sorted(bysec.items())},
   "by_size_band":{k:{"positive":v[0],"total":v[1]} for k,v in sorted(bysize.items())}})
 # co-occurrence is descriptive family-level independent-search recurrence, NOT composite rediscovery.
 co=[]
 for i,f1 in enumerate(FAMILIES):
  for f2 in FAMILIES[i+1:]:
   tick=[]
   for t in meta:
    a1=next(r for r in rows if r["ticker"]==t and r["family"]==f1);a2=next(r for r in rows if r["ticker"]==t and r["family"]==f2)
    if a1["has_retained_positive_n10"] and a2["has_retained_positive_n10"]:tick.append(t)
   co.append({"families":[f1,f2],"ticker_count":len(tick),"tickers":tick})
 out={"format":"MTS_V4_DISCOVERY2_INDEPENDENT_SEARCH_REDISCOVERY_AUDIT_V1",
  "scientific_boundary":"DISCOVERY_SEARCH_OUTPUTS_UNSEALED_AFTER_FROZEN_TRANSPORT_AND_EXECUTABLE_PATH_AUDITS; VERIFICATION_REMAINS_SEALED",
  "unsealed_search_outputs":True,"unseal_reason":"prespecified independent Discovery recurrence audit after frozen transport/path conclusion",
  "methodology":{"retained_positive_rule":"top-candidate union across random+ga; unique candidate_id; N>=10; mean>0; median>0",
   "composite_rediscovery_claim":False,"note":"single-family Search cannot literally rediscover frozen composite forms; co-occurrence is descriptive component-family recurrence only",
   "candidate_selection_mutated":False,"refit":False},
  "ticker_family_rows":rows,"family_summary":byfam,"pairwise_family_cooccurrence":co,
  "verification_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(f"REPORT={a.output}");print(f"TICKERS={len(meta)}")
 for x in sorted(byfam,key=lambda z:(-z["fraction"],z["family"])):
  print(f"{x['family']}: positive_tickers={x['tickers_with_retained_positive_n10']}/{x['tickers_total']} fraction={x['fraction']:.3f} retained_instances={x['retained_positive_candidate_instances']}")
 print("TOP_PAIRWISE_COOCCURRENCE")
 for x in sorted(co,key=lambda z:(-z["ticker_count"],z["families"]))[:12]:print(f"{'+'.join(x['families'])}: {x['ticker_count']}")
 print("COMPOSITE_REDISCOVERY_CLAIM=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
