#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json,statistics
from bisect import bisect_right
from collections import defaultdict
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore

TRIGGERS={"BREAKOUT","MOMENTUM","TREND","MEAN_REVERSION"}
CONTEXTS={"VOLATILITY","VOLUME_LIQUIDITY","MARKET_REGIME_STRUCTURE","RELATIVE_CROSS_SECTIONAL"}
WINDOWS=(5,10,20,40)
BOUNDARY="DISCOVERY_COMPOSITE_EXPERIMENT_2C_LITERAL_MARKET_SESSIONS_ONLY_NOT_VALIDATION_NOT_PROMOTION"

def st(v):
    return {"count":len(v),"mean":statistics.fmean(v) if v else None,
            "median":statistics.median(v) if v else None,
            "positive_fraction":sum(x>0 for x in v)/len(v) if v else None}

def load_candidate(row):
    d=json.loads(Path(row["source_report"]).read_text())
    for o in row["optimizers"]:
        for c in d["results"][row["family"]][o]:
            if c.get("candidate_id")==row["candidate_id"]:
                return d,c
    raise RuntimeError("candidate not found: "+str(row["candidate_id"]))

def latest_prior_session_distance(context_dates, trigger_date, session_pos):
    i=bisect_right(context_dates,trigger_date)-1
    if i<0: return None
    c=context_dates[i]
    ti=session_pos.get(trigger_date); ci=session_pos.get(c)
    if ti is None or ci is None or ci>ti: return None
    return ti-ci

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--derived-market-root",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    m=json.loads(Path(a.manifest).read_text())
    if m.get("verification_accessed") is not False: raise SystemExit("verification boundary violated")
    if m.get("candidate_selection_mutated") is not False: raise SystemExit("selection mutation boundary violated")

    store=ParquetDerivedMarketStore(a.derived_market_root)
    by=defaultdict(list)
    meta={}
    for r in m["retained_candidates"]:
        report,c=load_candidate(r)
        paths=sorted(c.get("paths",[]),key=lambda x:str(x["signal_date"]))
        x=dict(r);x["_paths"]=paths;x["_dates"]=sorted(str(p["signal_date"]) for p in paths)
        x["_base"]=st([float(p["fixed_horizon_return"]) for p in paths])
        by[r["ticker"]].append(x)
        meta[r["ticker"]]=report

    results=[]
    session_counts={}
    for ticker,rows in sorted(by.items()):
        rep=meta[ticker]
        predictors=list(store.query(DerivedMarketQuery(
            universe_id=rep["universe_id"],feature_set_id="mts_market_predictors",
            feature_set_version=rep["predictor_feature_set_version"],
            security_ids=(rep["security_id"],),
        )))
        sessions=sorted({str(r["effective_date"]) for r in predictors})
        session_pos={d:i for i,d in enumerate(sessions)}
        session_counts[ticker]=len(sessions)

        triggers=[r for r in rows if r["family"] in TRIGGERS]
        contexts=[r for r in rows if r["family"] in CONTEXTS]
        for tr in triggers:
          for nctx in (1,2,3):
           for ctxs in itertools.combinations(contexts,nctx):
            if len({c["family"] for c in ctxs})<nctx: continue
            for w in WINDOWS:
             for form in ("ALL_CONTEXTS","MAJORITY_CONTEXTS"):
              if nctx==1 and form=="MAJORITY_CONTEXTS": continue
              kept=[]
              for pth in tr["_paths"]:
                d=str(pth["signal_date"])
                active=0
                for c in ctxs:
                    dist=latest_prior_session_distance(c["_dates"],d,session_pos)
                    if dist is not None and dist<=w: active+=1
                need=nctx if form=="ALL_CONTEXTS" else (nctx//2+1)
                if active>=need: kept.append(pth)
              vals=[float(x["fixed_horizon_return"]) for x in kept];s=st(vals);b=tr["_base"]
              results.append({
                "ticker":ticker,"trigger_family":tr["family"],"trigger_candidate_id":tr["candidate_id"],
                "context_families":[c["family"] for c in ctxs],
                "context_candidate_ids":[c["candidate_id"] for c in ctxs],
                "context_count":nctx,"window_market_sessions":w,"form":form,
                "statistics":s,"trigger_baseline_statistics":b,
                "delta_mean_vs_trigger":s["mean"]-b["mean"] if vals else None,
                "delta_median_vs_trigger":s["median"]-b["median"] if vals else None,
                "retains_n_ge_10":len(vals)>=10,
                "incremental_mean_positive":bool(vals) and s["mean"]>b["mean"],
                "incremental_median_positive":bool(vals) and s["median"]>b["median"],
            })

    usable=[r for r in results if r["retains_n_ge_10"]]
    inc=[r for r in usable if r["incremental_mean_positive"] and r["incremental_median_positive"]]
    out={
      "format":"MTS_V4_TEMPORAL_CONTEXT_COMPOSITE_EXPERIMENT_2C_V1",
      "scientific_boundary":BOUNDARY,
      "source_experiment":"EXPERIMENT_2B_DESIGN_REPLAYED_WITH_LITERAL_MARKET_SESSION_CLOCK",
      "design":{
        "trigger_families":sorted(TRIGGERS),"context_families":sorted(CONTEXTS),
        "windows_market_sessions":list(WINDOWS),"forms":["ALL_CONTEXTS","MAJORITY_CONTEXTS"],
        "context_group_sizes":[1,2,3],"minimum_n":10,
        "session_clock":"DERIVED_MARKET_MTS_MARKET_PREDICTORS_EFFECTIVE_DATE_SEQUENCE",
        "no_new_combinations":True,"no_new_windows":True,"no_weights":True,"no_refit":True,
        "incremental_test":"mean and median both exceed frozen trigger baseline; descriptive Discovery evidence only"
      },
      "session_counts":session_counts,
      "composites":results,
      "usable_n_ge_10_count":len(usable),
      "incremental_mean_and_median_count":len(inc),
      "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(f"REPORT={a.output}");print(f"TICKERS={len(by)}");print(f"COMPOSITES_EVALUATED={len(results)}")
    print(f"USABLE_N_GE_10={len(usable)}");print(f"INCREMENTAL_MEAN_AND_MEDIAN={len(inc)}")
    for w in WINDOWS:
        u=[r for r in usable if r["window_market_sessions"]==w]
        i=[r for r in u if r["incremental_mean_positive"] and r["incremental_median_positive"]]
        print(f"WINDOW_{w}_USABLE={len(u)} WINDOW_{w}_INCREMENTAL={len(i)}")
    print("SESSION_CLOCK=DERIVED_MARKET_LITERAL_SESSIONS")
    print("CANDIDATE_SELECTION_MUTATED=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")

if __name__=="__main__": main()
