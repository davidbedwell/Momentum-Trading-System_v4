#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json,statistics
from collections import defaultdict
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal,_finite

BOUNDARY="DISCOVERY_COMPOSITE_EXPERIMENT_2D_RAW_BOOLEAN_STATES_ONLY_NOT_VALIDATION_NOT_PROMOTION"

def st(v):
    return {"count":len(v),"mean":statistics.fmean(v) if v else None,
            "median":statistics.median(v) if v else None,
            "positive_fraction":sum(x>0 for x in v)/len(v) if v else None}

def load(row):
    trade=json.loads(Path(row["source_report"]).read_text())
    search=json.loads(Path(trade["source_search_report"]).read_text())
    for o in row["optimizers"]:
        for c in trade["results"][row["family"]][o]:
            if c.get("candidate_id")==row["candidate_id"]:
                return search,{"candidate_id":c["candidate_id"],"family_id":c["family_id"],"genome":c["genome"]}
    raise RuntimeError("candidate not found "+str(row["candidate_id"]))

def accepted_returns(signals,predictors,outcomes,horizon):
    col=f"forward_return_{horizon}__v1"
    oi={(str(r["security_id"]),str(r["effective_date"])):r for r in outcomes}
    vals=[];dates=[];cooldown=0
    for row,on in zip(predictors,signals):
        out=oi.get((str(row["security_id"]),str(row["effective_date"])))
        value=None if out is None else _finite(out.get(col))
        if on and value is not None and cooldown==0:
            vals.append(float(value));dates.append(str(row["effective_date"]));cooldown=horizon
        if cooldown: cooldown-=1
    return vals,dates

def main():
    p=argparse.ArgumentParser();p.add_argument("--manifest",required=True)
    p.add_argument("--derived-market-root",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();m=json.loads(Path(a.manifest).read_text())
    if m.get("verification_accessed") is not False or m.get("candidate_selection_mutated") is not False:
        raise SystemExit("scientific boundary violated")
    store=ParquetDerivedMarketStore(a.derived_market_root)
    by=defaultdict(list);meta={}
    for r in m["retained_candidates"]:
        search,c=load(r);x=dict(r);x["_candidate"]=c;by[r["ticker"]].append(x);meta[r["ticker"]]=search

    rows=[]
    for ticker,cands in sorted(by.items()):
        rep=meta[ticker]
        predictors=list(store.query(DerivedMarketQuery(
            universe_id=rep["universe_id"],feature_set_id="mts_market_predictors",
            feature_set_version=rep["predictor_feature_set_version"],security_ids=(rep["security_id"],))))
        predictors.sort(key=lambda r:(str(r["effective_date"]),str(r["security_id"])))
        outcomes=list(store.query(DerivedMarketQuery(
            universe_id=rep["universe_id"],feature_set_id="mts_historical_outcomes",
            feature_set_version=rep["outcome_feature_set_version"],security_ids=(rep["security_id"],))))
        for x in cands:
            x["_signal"]=_compile_signal(predictors,x["_candidate"])
            h=int(x["_candidate"]["genome"]["forward_horizon"])
            v,d=accepted_returns(x["_signal"],predictors,outcomes,h)
            x["_base"]=st(v);x["_base_dates"]=d

        for k in (2,3,4):
          for group in itertools.combinations(cands,k):
            if len({x["family"] for x in group})<k: continue
            for trigger in group:
              h=int(trigger["_candidate"]["genome"]["forward_horizon"])
              # ALL: every frozen genome Boolean is true on the trigger session.
              allsig=[all(x["_signal"][i] for x in group) for i in range(len(predictors))]
              forms=[("ALL",allsig)]
              if k==3:
                forms.append(("2_OF_3",[sum(bool(x["_signal"][i]) for x in group)>=2 for i in range(len(predictors))]))
              if k==4:
                forms.append(("3_OF_4",[sum(bool(x["_signal"][i]) for x in group)>=3 for i in range(len(predictors))]))
              for form,sig in forms:
                # A composite may only enter where the designated trigger itself is true.
                gated=[bool(trigger["_signal"][i]) and bool(sig[i]) for i in range(len(sig))]
                vals,dates=accepted_returns(gated,predictors,outcomes,h);s=st(vals);b=trigger["_base"]
                rows.append({"ticker":ticker,"size":k,"form":form,
                  "trigger_family":trigger["family"],"trigger_candidate_id":trigger["candidate_id"],
                  "member_families":[x["family"] for x in group],
                  "member_candidate_ids":[x["candidate_id"] for x in group],
                  "statistics":s,"trigger_baseline_statistics":b,
                  "delta_mean_vs_trigger":s["mean"]-b["mean"] if vals else None,
                  "delta_median_vs_trigger":s["median"]-b["median"] if vals else None,
                  "retains_n_ge_10":len(vals)>=10,
                  "incremental_mean_positive":bool(vals) and s["mean"]>b["mean"],
                  "incremental_median_positive":bool(vals) and s["median"]>b["median"],
                  "accepted_signal_dates":dates})
    usable=[r for r in rows if r["retains_n_ge_10"]]
    inc=[r for r in usable if r["incremental_mean_positive"] and r["incremental_median_positive"]]
    out={"format":"MTS_V4_RAW_BOOLEAN_STATE_COMPOSITE_EXPERIMENT_2D_V1","scientific_boundary":BOUNDARY,
      "design":{"source":"61 frozen Experiment-1 retained genomes","group_sizes":[2,3,4],
       "forms":{"2":["ALL"],"3":["ALL","2_OF_3"],"4":["ALL","3_OF_4"]},
       "semantics":"compile each frozen genome Boolean on every predictor session; combine Boolean states first; require designated trigger true; then apply trigger frozen horizon non-overlap and frozen outcome eligibility",
       "minimum_n":10,"no_new_genomes":True,"no_new_thresholds":True,"no_weights":True,"no_refit":True,
       "incremental_test":"composite mean and median both exceed the same trigger genome baseline"},
      "composites":rows,"usable_n_ge_10_count":len(usable),"incremental_mean_and_median_count":len(inc),
      "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(f"REPORT={a.output}");print(f"TICKERS={len(by)}");print(f"COMPOSITES_EVALUATED={len(rows)}")
    print(f"USABLE_N_GE_10={len(usable)}");print(f"INCREMENTAL_MEAN_AND_MEDIAN={len(inc)}")
    for k in (2,3,4):
        u=[r for r in usable if r["size"]==k];ii=[r for r in u if r["incremental_mean_positive"] and r["incremental_median_positive"]]
        print(f"SIZE_{k}_USABLE={len(u)} SIZE_{k}_INCREMENTAL={len(ii)}")
    print("COMPOSITION=RAW_BOOLEAN_STATES_BEFORE_NONOVERLAP")
    print("CANDIDATE_SELECTION_MUTATED=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
