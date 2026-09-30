#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal

FAMILIES=("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE")

def unique_top(r,f):
 seen=set();out=[]
 for opt in ("random","ga"):
  for c in r["families"][f][opt]["top_candidates"]:
   if c["candidate_id"] not in seen:seen.add(c["candidate_id"]);out.append(c)
 return out

def replay(pred,out,c):
 h=int(c["genome"]["forward_horizon"]);col=f"forward_return_{h}__v1"
 oi={(str(x["security_id"]),str(x["effective_date"])):x for x in out}
 vals=[]
 for row,on in zip(pred,_compile_signal(pred,c)):
  if not on:continue
  x=oi.get((str(row["security_id"]),str(row["effective_date"])))
  if x is not None and x.get(col) is not None:vals.append(float(x[col]))
 return {"signal_count":len(vals),"mean_forward_return":statistics.fmean(vals) if vals else None,
         "median_forward_return":statistics.median(vals) if vals else None,
         "positive_fraction":sum(v>0 for v in vals)/len(vals) if vals else None}

def main():
 p=argparse.ArgumentParser();p.add_argument("--d2-dir",required=True);p.add_argument("--d2b-dir",required=True);p.add_argument("--d2-classification",required=True);p.add_argument("--d2b-manifest",required=True);p.add_argument("--derived-market-root",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 meta={}
 for x in json.loads(Path(a.d2_classification).read_text())["tickers"]:meta[x["ticker"]]={"cohort":"D2_50","sector":x["sector"],"size_band":x["size_band"]}
 for x in json.loads(Path(a.d2b_manifest).read_text())["tickers"]:meta[x["ticker"]]={"cohort":"D2B_SUPPLEMENT","sector":x["sector"],"size_band":x["size_band"]}
 store=ParquetDerivedMarketStore(a.derived_market_root);rows=[]
 for i,(ticker,m) in enumerate(sorted(meta.items()),1):
  base=Path(a.d2_dir) if m["cohort"]=="D2_50" else Path(a.d2b_dir);f=base/f"{ticker}_COMPUTATIONAL_SEARCH_20260930.json";r=json.loads(f.read_text())
  pred=list(store.query(DerivedMarketQuery(universe_id=r["universe_id"],feature_set_id="mts_market_predictors",feature_set_version=r["predictor_feature_set_version"],security_ids=(r["security_id"],))));pred.sort(key=lambda x:str(x["effective_date"]))
  out=list(store.query(DerivedMarketQuery(universe_id=r["universe_id"],feature_set_id="mts_historical_outcomes",feature_set_version=r["outcome_feature_set_version"],security_ids=(r["security_id"],))))
  for fam in FAMILIES:
   cs=unique_top(r,fam);reps=[]
   for c in cs:
    z=replay(pred,out,c);reps.append({"candidate_id":c["candidate_id"],"genome":c["genome"],"replay_metrics":z,
      "retained":z["signal_count"]>=10 and z["mean_forward_return"] is not None and z["mean_forward_return"]>0 and z["median_forward_return"] is not None and z["median_forward_return"]>0})
   kept=[x for x in reps if x["retained"]]
   rows.append({"ticker":ticker,**m,"family":fam,"unique_saved_top_candidates":len(reps),"retained_count":len(kept),"has_retained":bool(kept),"candidates":reps})
  print(f"[{i}/{len(meta)}] REPLAYED={ticker}",flush=True)
 fs=[]
 for fam in FAMILIES:
  x=[r for r in rows if r["family"]==fam];yes=[r for r in x if r["has_retained"]]
  fs.append({"family":fam,"positive_tickers":len(yes),"total_tickers":len(x),"fraction":len(yes)/len(x),
    "retained_instances":sum(r["retained_count"] for r in x),
    "by_cohort":{c:{"positive":sum(r["has_retained"] for r in x if r["cohort"]==c),"total":sum(1 for r in x if r["cohort"]==c)} for c in ("D2_50","D2B_SUPPLEMENT")}})
 co=[]
 for i,f1 in enumerate(FAMILIES):
  for f2 in FAMILIES[i+1:]:
   ts=[t for t in meta if next(r for r in rows if r["ticker"]==t and r["family"]==f1)["has_retained"] and next(r for r in rows if r["ticker"]==t and r["family"]==f2)["has_retained"]]
   co.append({"families":[f1,f2],"ticker_count":len(ts),"tickers":ts})
 result={"format":"MTS_V4_DISCOVERY2_DETERMINISTIC_SAVED_CANDIDATE_REPLAY_V1","scientific_boundary":"DISCOVERY_ONLY_SEARCH_ALREADY_UNSEALED_VERIFICATION_SEALED",
  "retention_rule":"N>=10 AND mean>0 AND median>0","methodology":{"new_search":False,"new_genomes":False,"refit":False,"saved_top_candidates_only":True,"median_computed_by_deterministic_replay":True,"composite_rediscovery_claim":False},
  "ticker_family_rows":rows,"family_summary":fs,"pairwise_family_cooccurrence":co,"candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(f"REPORT={a.output}");print(f"TICKERS={len(meta)}")
 for x in sorted(fs,key=lambda z:(-z["fraction"],z["family"])):print(f"{x['family']}: positive_tickers={x['positive_tickers']}/{x['total_tickers']} fraction={x['fraction']:.3f} retained_instances={x['retained_instances']} D2={x['by_cohort']['D2_50']['positive']}/50 D2B={x['by_cohort']['D2B_SUPPLEMENT']['positive']}/17")
 print("TOP_PAIRWISE_COOCCURRENCE")
 for x in sorted(co,key=lambda z:(-z["ticker_count"],z["families"]))[:12]:print(f"{'+'.join(x['families'])}: {x['ticker_count']}")
 print("NEW_SEARCH=False");print("NEW_GENOMES=False");print("COMPOSITE_REDISCOVERY_CLAIM=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
