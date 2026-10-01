#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal
FAMS=("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE")
def uniq(r,f):
 s=set();z=[]
 for o in ("random","ga"):
  for c in r["families"][f][o]["top_candidates"]:
   if c["candidate_id"] not in s:s.add(c["candidate_id"]);z.append(c)
 return z
def main():
 p=argparse.ArgumentParser()
 for x in ("d2-dir","d2b-dir","d2-classification","d2b-manifest","derived-market-root","output"):p.add_argument("--"+x,required=True)
 a=p.parse_args();meta={}
 for x in json.loads(Path(a.d2_classification).read_text())["tickers"]:meta[x["ticker"]]={"cohort":"D2_50"}
 for x in json.loads(Path(a.d2b_manifest).read_text())["tickers"]:meta[x["ticker"]]={"cohort":"D2B_SUPPLEMENT"}
 reports={};sources=defaultdict(list)
 for t,m in meta.items():
  b=Path(a.d2_dir) if m["cohort"]=="D2_50" else Path(a.d2b_dir);r=json.loads((b/f"{t}_COMPUTATIONAL_SEARCH_20260930.json").read_text());reports[t]=r
  for f in FAMS:
   for c in uniq(r,f):sources[f].append((t,c))
 store=ParquetDerivedMarketStore(a.derived_market_root);rows=[]
 for i,(target,r) in enumerate(sorted(reports.items()),1):
  pred=list(store.query(DerivedMarketQuery(universe_id=r["universe_id"],feature_set_id="mts_market_predictors",feature_set_version=r["predictor_feature_set_version"],security_ids=(r["security_id"],))));pred.sort(key=lambda x:str(x["effective_date"]))
  out=list(store.query(DerivedMarketQuery(universe_id=r["universe_id"],feature_set_id="mts_historical_outcomes",feature_set_version=r["outcome_feature_set_version"],security_ids=(r["security_id"],))))
  oi={(str(x["security_id"]),str(x["effective_date"])):x for x in out};base={}
  for f in FAMS:
   for src,c in sources[f]:
    if src==target:continue
    h=int(c["genome"]["forward_horizon"]);col=f"forward_return_{h}__v1"
    if h not in base:
     vals=[float(o[col]) for o in out if o.get(col) is not None];base[h]=(statistics.fmean(vals),statistics.median(vals))
    vals=[]
    for pr,on in zip(pred,_compile_signal(pred,c)):
     if not on:continue
     o=oi.get((str(pr["security_id"]),str(pr["effective_date"])))
     if o is not None and o.get(col) is not None:vals.append(float(o[col]))
    if len(vals)<10:continue
    em=statistics.fmean(vals)-base[h][0];ed=statistics.median(vals)-base[h][1]
    rows.append({"source_ticker":src,"target_ticker":target,"family":f,"candidate_id":c["candidate_id"],"horizon":h,"n":len(vals),"excess_mean":em,"excess_median":ed,"positive_both":em>0 and ed>0})
  print(f"[{i}/{len(reports)}] TRANSPORTED_TO={target}",flush=True)
 summ=[]
 for f in FAMS:
  x=[r for r in rows if r["family"]==f];good=[r for r in x if r["positive_both"]]
  ut={r["target_ticker"] for r in x};gt={r["target_ticker"] for r in good};us={r["source_ticker"] for r in x};gs={r["source_ticker"] for r in good}
  bysrc=defaultdict(lambda:[0,0])
  for r in x:bysrc[r["source_ticker"]][1]+=1;bysrc[r["source_ticker"]][0]+=int(r["positive_both"])
  summ.append({"family":f,"usable_transports":len(x),"positive_both_transports":len(good),"fraction":len(good)/len(x) if x else None,
   "target_breadth":len(gt),"usable_targets":len(ut),"source_breadth":len(gs),"usable_sources":len(us),
   "median_excess_mean":statistics.median([r["excess_mean"] for r in x]) if x else None,
   "median_excess_median":statistics.median([r["excess_median"] for r in x]) if x else None,
   "source_concentration":{k:{"positive":v[0],"usable":v[1],"fraction":v[0]/v[1]} for k,v in sorted(bysrc.items())}})
 result={"format":"MTS_V4_DISCOVERY2_CROSS_TICKER_SINGLE_FAMILY_TRANSPORT_V1","scientific_boundary":"DISCOVERY_INTERNAL_TRANSPORT_NOT_VERIFICATION",
  "methodology":{"exact_saved_genomes":True,"self_transport_excluded":True,"new_search":False,"new_genomes":False,"refit":False,"winner_selection":False,
  "baseline":"target ticker unconditional same frozen horizon","usable_n_min":10,"positive_both_definition":"excess mean >0 and excess median >0"},
  "family_summary":summ,"transport_rows":rows,"verification_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(f"REPORT={a.output}")
 for z in sorted(summ,key=lambda q:(-(q["fraction"] or -1),q["family"])):
  print(f"{z['family']}: positive={z['positive_both_transports']}/{z['usable_transports']} fraction={z['fraction']:.3f} targets={z['target_breadth']}/{z['usable_targets']} sources={z['source_breadth']}/{z['usable_sources']} med_excess_mean={z['median_excess_mean']:.6f} med_excess_median={z['median_excess_median']:.6f}")
 print("SELF_TRANSPORT=False");print("WINNER_SELECTION=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
