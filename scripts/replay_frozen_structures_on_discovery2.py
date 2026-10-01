#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,statistics
from collections import defaultdict
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal,_finite

BOUNDARY="DISCOVERY2_INTERNAL_REPLICATION_EXACT_FROZEN_GENOMES_ONLY_NO_TARGET_SEARCH_INSPECTION"

def stats(v):
 return {"count":len(v),"mean":statistics.fmean(v) if v else None,"median":statistics.median(v) if v else None,
         "positive_fraction":sum(x>0 for x in v)/len(v) if v else None}

def accepted(signals,predictors,outcomes,h):
 col=f"forward_return_{h}__v1"; oi={(str(r["security_id"]),str(r["effective_date"])):r for r in outcomes}
 out=[]; cooldown=0
 for row,on in zip(predictors,signals):
  r=oi.get((str(row["security_id"]),str(row["effective_date"])))
  val=None if r is None else _finite(r.get(col))
  if on and val is not None and cooldown==0:
   out.append(float(val)); cooldown=h
  if cooldown: cooldown-=1
 return out

def structure_key(r):
 return (r["trigger_family"],tuple(sorted(r["member_families"])),r["form"],int(r["size"]))

def load_candidate(manifest_rows,ticker,cid,cache):
 k=(ticker,cid)
 if k in cache:return cache[k]
 mr=manifest_rows[k]
 trade=json.loads(Path(mr["source_report"]).read_text())
 search=json.loads(Path(trade["source_search_report"]).read_text())
 for opt in mr["optimizers"]:
  for c in trade["results"][mr["family"]][opt]:
   if c.get("candidate_id")==cid:
    out=(search,{"candidate_id":c["candidate_id"],"family_id":c["family_id"],"genome":c["genome"]})
    cache[k]=out; return out
 raise RuntimeError(f"candidate not found {ticker} {cid}")

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--frozen-robustness",required=True);p.add_argument("--source-manifest",required=True)
 p.add_argument("--target-classification",required=True);p.add_argument("--derived-market-root",required=True)
 p.add_argument("--output",required=True);a=p.parse_args()
 rob=json.loads(Path(a.frozen_robustness).read_text()); man=json.loads(Path(a.source_manifest).read_text())
 tgt=json.loads(Path(a.target_classification).read_text())
 for d in (rob,man,tgt):
  if d.get("verification_accessed") is not False: raise RuntimeError("verification boundary violated")
 rows={(r["ticker"],r["candidate_id"]):r for r in man["retained_candidates"]}
 ccache={}
 frozen=[]
 for r in rob["instances"]:
  members=[]
  for cid in r["member_candidate_ids"]:
   search,c=load_candidate(rows,r["ticker"],cid,ccache); members.append(c)
  frozen.append({"source_ticker":r["ticker"],"trigger_candidate_id":r["trigger_candidate_id"],
                 "trigger_family":r["trigger_family"],"member_candidate_ids":r["member_candidate_ids"],
                 "member_families":r["member_families"],"form":r["form"],"size":r["size"],"members":members})
 if not frozen: raise RuntimeError("no frozen instances")
 template_search=next(iter(ccache.values()))[0]
 store=ParquetDerivedMarketStore(a.derived_market_root); results=[]
 for ti,t in enumerate(tgt["tickers"],1):
  sid=str(t["security_id"]); ticker=t["ticker"]; sector=t["sector"]; size_band=t["size_band"]
  predictors=list(store.query(DerivedMarketQuery(universe_id=template_search["universe_id"],
    feature_set_id="mts_market_predictors",feature_set_version=template_search["predictor_feature_set_version"],
    security_ids=(sid,))))
  predictors.sort(key=lambda r:(str(r["effective_date"]),str(r["security_id"])))
  outcomes=list(store.query(DerivedMarketQuery(universe_id=template_search["universe_id"],
    feature_set_id="mts_historical_outcomes",feature_set_version=template_search["outcome_feature_set_version"],
    security_ids=(sid,))))
  for f in frozen:
   sigs=[_compile_signal(predictors,c) for c in f["members"]]
   ids=f["member_candidate_ids"]; trigger_idx=ids.index(f["trigger_candidate_id"]); k=len(sigs)
   if f["form"]=="ALL": combo=[all(s[i] for s in sigs) for i in range(len(predictors))]
   elif f["form"]=="2_OF_3": combo=[sum(bool(s[i]) for s in sigs)>=2 for i in range(len(predictors))]
   elif f["form"]=="3_OF_4": combo=[sum(bool(s[i]) for s in sigs)>=3 for i in range(len(predictors))]
   else: raise RuntimeError("unknown form")
   gated=[bool(sigs[trigger_idx][i]) and bool(combo[i]) for i in range(len(combo))]
   h=int(f["members"][trigger_idx]["genome"]["forward_horizon"])
   vals=accepted(gated,predictors,outcomes,h); base=accepted(sigs[trigger_idx],predictors,outcomes,h)
   s=stats(vals); b=stats(base); usable=s["count"]>=10
   inc=usable and s["mean"] is not None and b["mean"] is not None and s["median"] is not None and b["median"] is not None and s["mean"]>b["mean"] and s["median"]>b["median"]
   results.append({"ticker":ticker,"security_id":sid,"sector":sector,"size_band":size_band,
     "source_ticker":f["source_ticker"],"trigger_family":f["trigger_family"],"member_families":f["member_families"],
     "form":f["form"],"size":f["size"],"trigger_candidate_id":f["trigger_candidate_id"],
     "member_candidate_ids":f["member_candidate_ids"],"statistics":s,"trigger_baseline_statistics":b,
     "retains_n_ge_10":usable,"incremental_mean_and_median":inc})
  print(f"[{ti}/{len(tgt['tickers'])}] REPLAYED={ticker}",flush=True)

 by=defaultdict(list)
 for r in results: by[structure_key(r)].append(r)
 structures=[]
 for k,rs in sorted(by.items()):
  usable=[r for r in rs if r["retains_n_ge_10"]]; inc=[r for r in usable if r["incremental_mean_and_median"]]
  structures.append({"trigger_family":k[0],"member_families":list(k[1]),"form":k[2],"size":k[3],
   "applications":len(rs),"usable_instances_n_ge_10":len(usable),"incremental_instances":len(inc),
   "tickers_usable":sorted({r["ticker"] for r in usable}),"tickers_incremental":sorted({r["ticker"] for r in inc}),
   "ticker_count_usable":len({r["ticker"] for r in usable}),"ticker_count_incremental":len({r["ticker"] for r in inc})})
 out={"format":"MTS_V4_DISCOVERY2_FROZEN_STRUCTURE_REPLICATION_V1","scientific_boundary":BOUNDARY,
  "source_frozen_robustness":a.frozen_robustness,"source_manifest":a.source_manifest,
  "target_classification":a.target_classification,
  "methodology":{"target_search_results_read":False,"new_search":False,"new_genomes":False,"refit":False,
   "frozen_instance_count":len(frozen),"application":"each exact original frozen candidate-genome instance replayed on every target ticker",
   "minimum_n":10,"incremental_test":"composite mean and median both exceed its own frozen trigger genome baseline on the target ticker"},
  "target_ticker_count":len(tgt["tickers"]),"applications":results,"structures":structures,
  "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(f"REPORT={a.output}");print(f"TARGET_TICKERS={len(tgt['tickers'])}");print(f"FROZEN_INSTANCES={len(frozen)}")
 print(f"APPLICATIONS={len(results)}");print(f"STRUCTURES={len(structures)}")
 print("TARGET_SEARCH_RESULTS_READ=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
