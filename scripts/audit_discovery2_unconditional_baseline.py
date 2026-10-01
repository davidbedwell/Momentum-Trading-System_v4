#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal

FAMILIES=("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE")
def unique_top(r,f):
 seen=set();z=[]
 for opt in ("random","ga"):
  for c in r["families"][f][opt]["top_candidates"]:
   if c["candidate_id"] not in seen: seen.add(c["candidate_id"]);z.append(c)
 return z
def stats(x):
 return {"n":len(x),"mean":statistics.fmean(x) if x else None,"median":statistics.median(x) if x else None}
def main():
 p=argparse.ArgumentParser()
 for x in ("d2-dir","d2b-dir","d2-classification","d2b-manifest","derived-market-root","output"):p.add_argument("--"+x,required=True)
 a=p.parse_args();meta={}
 for x in json.loads(Path(a.d2_classification).read_text())["tickers"]:meta[x["ticker"]]={"cohort":"D2_50","sector":x["sector"],"size_band":x["size_band"]}
 for x in json.loads(Path(a.d2b_manifest).read_text())["tickers"]:meta[x["ticker"]]={"cohort":"D2B_SUPPLEMENT","sector":x["sector"],"size_band":x["size_band"]}
 store=ParquetDerivedMarketStore(a.derived_market_root);rows=[]
 for i,(t,m) in enumerate(sorted(meta.items()),1):
  base=Path(a.d2_dir) if m["cohort"]=="D2_50" else Path(a.d2b_dir);r=json.loads((base/f"{t}_COMPUTATIONAL_SEARCH_20260930.json").read_text())
  pred=list(store.query(DerivedMarketQuery(universe_id=r["universe_id"],feature_set_id="mts_market_predictors",feature_set_version=r["predictor_feature_set_version"],security_ids=(r["security_id"],))));pred.sort(key=lambda x:str(x["effective_date"]))
  out=list(store.query(DerivedMarketQuery(universe_id=r["universe_id"],feature_set_id="mts_historical_outcomes",feature_set_version=r["outcome_feature_set_version"],security_ids=(r["security_id"],))))
  oi={(str(x["security_id"]),str(x["effective_date"])):x for x in out}
  for fam in FAMILIES:
   for c in unique_top(r,fam):
    h=int(c["genome"]["forward_horizon"]);col=f"forward_return_{h}__v1";sig=[];basevals=[]
    mask=_compile_signal(pred,c)
    for row,on in zip(pred,mask):
     o=oi.get((str(row["security_id"]),str(row["effective_date"])))
     if o is None or o.get(col) is None:continue
     v=float(o[col]);basevals.append(v)
     if on:sig.append(v)
    ss,bs=stats(sig),stats(basevals)
    rows.append({"ticker":t,**m,"family":fam,"candidate_id":c["candidate_id"],"horizon":h,"signal":ss,"unconditional_same_horizon":bs,
     "excess_mean":None if ss["mean"] is None or bs["mean"] is None else ss["mean"]-bs["mean"],
     "excess_median":None if ss["median"] is None or bs["median"] is None else ss["median"]-bs["median"]})
  print(f"[{i}/{len(meta)}] BASELINED={t}",flush=True)
 summary=[]
 for fam in FAMILIES:
  x=[r for r in rows if r["family"]==fam and r["signal"]["n"]>=10]
  both=[r for r in x if r["excess_mean"]>0 and r["excess_median"]>0]
  tick=defaultdict(list)
  for r in x:tick[r["ticker"]].append(r)
  tickboth=[t for t,v in tick.items() if any(r["excess_mean"]>0 and r["excess_median"]>0 for r in v)]
  summary.append({"family":fam,"usable_instances":len(x),"positive_excess_mean_and_median_instances":len(both),
   "tickers_with_any_positive_excess_mean_and_median":len(tickboth),"usable_tickers":len(tick),
   "median_excess_mean":statistics.median([r["excess_mean"] for r in x]) if x else None,
   "median_excess_median":statistics.median([r["excess_median"] for r in x]) if x else None})
 result={"format":"MTS_V4_DISCOVERY2_UNCONDITIONAL_BASELINE_AUDIT_V1","scientific_boundary":"DESCRIPTIVE_DISCOVERY_BASELINE_AUDIT_NOT_NEW_PROMOTION_GATE",
  "baseline":"same ticker, same frozen forward horizon, all available outcome dates","methodology":{"new_search":False,"new_genomes":False,"refit":False,"threshold_added":False,"saved_top_candidates_only":True},
  "candidate_rows":rows,"family_summary":summary,"verification_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(f"REPORT={a.output}")
 for x in sorted(summary,key=lambda z:(-(z["median_excess_mean"] or -999),z["family"])):
  print(f"{x['family']}: usable={x['usable_instances']} excess_both={x['positive_excess_mean_and_median_instances']} tickers={x['tickers_with_any_positive_excess_mean_and_median']}/{x['usable_tickers']} median_excess_mean={x['median_excess_mean']:.6f} median_excess_median={x['median_excess_median']:.6f}")
 print("NEW_THRESHOLD=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
