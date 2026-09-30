#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal,_finite

BOUNDARY="DISCOVERY_EXPERIMENT_2D_RECURRING_STRUCTURE_ROBUSTNESS_REPLAY_ONLY_NOT_VALIDATION_NOT_PROMOTION"

def st(v):
    return {"count":len(v),"mean":statistics.fmean(v) if v else None,
            "median":statistics.median(v) if v else None,
            "positive_fraction":sum(x>0 for x in v)/len(v) if v else None,
            "min":min(v) if v else None,"max":max(v) if v else None}

def thirds(trades):
    trades=sorted(trades,key=lambda x:x["date"]); n=len(trades)
    if n<3:return []
    cuts=(0,n//3,(2*n)//3,n); out=[]
    for i in range(3):
        seg=trades[cuts[i]:cuts[i+1]]; vals=[x["ret"] for x in seg]
        x=st(vals);x.update({"third":i+1,"first_date":seg[0]["date"] if seg else None,
                             "last_date":seg[-1]["date"] if seg else None})
        out.append(x)
    return out

def loo(vals):
    if len(vals)<2:return {"count":len(vals),"mean_min":None,"mean_max":None}
    means=[statistics.fmean(vals[:i]+vals[i+1:]) for i in range(len(vals))]
    return {"count":len(vals),"mean_min":min(means),"mean_max":max(means)}

def concentration(vals):
    pos=sorted([x for x in vals if x>0],reverse=True); s=sum(pos)
    def share(n): return sum(pos[:n])/s if s>0 else None
    return {"positive_return_sum":s,"top1_share":share(1),"top2_share":share(2),"top3_share":share(3)}

def load_candidate(row):
    trade=json.loads(Path(row["source_report"]).read_text())
    search=json.loads(Path(trade["source_search_report"]).read_text())
    for o in row["optimizers"]:
        for c in trade["results"][row["family"]][o]:
            if c.get("candidate_id")==row["candidate_id"]:
                return search,{"candidate_id":c["candidate_id"],"family_id":c["family_id"],"genome":c["genome"]}
    raise RuntimeError("candidate not found "+str(row["candidate_id"]))

def accepted(signals,predictors,outcomes,horizon):
    col=f"forward_return_{horizon}__v1"
    oi={(str(r["security_id"]),str(r["effective_date"])):r for r in outcomes}
    vals=[];cooldown=0
    for row,on in zip(predictors,signals):
        out=oi.get((str(row["security_id"]),str(row["effective_date"])))
        val=None if out is None else _finite(out.get(col))
        if on and val is not None and cooldown==0:
            vals.append({"date":str(row["effective_date"]),"ret":float(val)})
            cooldown=horizon
        if cooldown: cooldown-=1
    return vals

def key_of(r):
    return (r["trigger_family"],tuple(sorted(r["member_families"])),r["form"],int(r["size"]))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--experiment",required=True)
    p.add_argument("--recurrence",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--derived-market-root",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()

    exp=json.loads(Path(a.experiment).read_text())
    rec=json.loads(Path(a.recurrence).read_text())
    man=json.loads(Path(a.manifest).read_text())
    for d in (exp,rec,man):
        if d.get("verification_accessed") is not False or d.get("candidate_selection_mutated") is not False:
            raise SystemExit("scientific boundary violated")

    recurring={key_of(r) for r in rec["recurring_structures_ge_2_tickers"]}
    target=[r for r in exp["composites"] if key_of(r) in recurring]

    manifest_rows={(r["ticker"],r["candidate_id"]):r for r in man["retained_candidates"]}
    store=ParquetDerivedMarketStore(a.derived_market_root)
    cache={}
    results=[]

    for r in target:
        ticker=r["ticker"]
        ids=r["member_candidate_ids"]
        members=[]
        for cid in ids:
            mr=manifest_rows[(ticker,cid)]
            search,c=load_candidate(mr)
            members.append((mr,search,c))
        trigger_idx=ids.index(r["trigger_candidate_id"])
        trigger=members[trigger_idx][2]
        search=members[0][1]
        ck=ticker
        if ck not in cache:
            predictors=list(store.query(DerivedMarketQuery(
                universe_id=search["universe_id"],feature_set_id="mts_market_predictors",
                feature_set_version=search["predictor_feature_set_version"],
                security_ids=(search["security_id"],))))
            predictors.sort(key=lambda x:(str(x["effective_date"]),str(x["security_id"])))
            outcomes=list(store.query(DerivedMarketQuery(
                universe_id=search["universe_id"],feature_set_id="mts_historical_outcomes",
                feature_set_version=search["outcome_feature_set_version"],
                security_ids=(search["security_id"],))))
            cache[ck]=(predictors,outcomes)
        predictors,outcomes=cache[ck]
        sigs=[_compile_signal(predictors,c) for _,_,c in members]
        k=len(members)
        if r["form"]=="ALL":
            combo=[all(s[i] for s in sigs) for i in range(len(predictors))]
        elif r["form"]=="2_OF_3":
            combo=[sum(bool(s[i]) for s in sigs)>=2 for i in range(len(predictors))]
        elif r["form"]=="3_OF_4":
            combo=[sum(bool(s[i]) for s in sigs)>=3 for i in range(len(predictors))]
        else:
            raise RuntimeError("unknown form "+r["form"])
        gated=[bool(sigs[trigger_idx][i]) and bool(combo[i]) for i in range(len(predictors))]
        h=int(trigger["genome"]["forward_horizon"])
        trades=accepted(gated,predictors,outcomes,h)
        base=accepted(sigs[trigger_idx],predictors,outcomes,h)
        vals=[x["ret"] for x in trades];bvals=[x["ret"] for x in base]
        s=st(vals);bs=st(bvals)
        t3=thirds(trades);b3=thirds(base)
        third_compare=[]
        for i in range(min(len(t3),len(b3))):
            third_compare.append({
                "third":i+1,
                "composite_mean":t3[i]["mean"],"trigger_mean":b3[i]["mean"],
                "delta_mean":None if t3[i]["mean"] is None or b3[i]["mean"] is None else t3[i]["mean"]-b3[i]["mean"],
                "composite_median":t3[i]["median"],"trigger_median":b3[i]["median"],
                "delta_median":None if t3[i]["median"] is None or b3[i]["median"] is None else t3[i]["median"]-b3[i]["median"],
                "composite_n":t3[i]["count"],"trigger_n":b3[i]["count"],
            })
        results.append({
            "ticker":ticker,"trigger_family":r["trigger_family"],"trigger_candidate_id":r["trigger_candidate_id"],
            "member_families":r["member_families"],"member_candidate_ids":ids,"form":r["form"],"size":r["size"],
            "statistics":s,"trigger_baseline_statistics":bs,
            "delta_mean_vs_trigger":None if s["mean"] is None or bs["mean"] is None else s["mean"]-bs["mean"],
            "delta_median_vs_trigger":None if s["median"] is None or bs["median"] is None else s["median"]-bs["median"],
            "chronological_thirds":t3,"trigger_chronological_thirds":b3,"third_comparison":third_compare,
            "leave_one_out":loo(vals),"winner_concentration":concentration(vals),
            "accepted_trades":trades
        })

    by_structure=defaultdict(list)
    for r in results: by_structure[key_of(r)].append(r)
    structures=[]
    for key,rows in sorted(by_structure.items()):
        ticker_set=sorted({r["ticker"] for r in rows})
        usable=[r for r in rows if r["statistics"]["count"]>=10]
        inc=[r for r in usable if (r["delta_mean_vs_trigger"] or 0)>0 and (r["delta_median_vs_trigger"] or 0)>0]
        chrono_good=[]
        for r in usable:
            comps=r["third_comparison"]
            good=sum(1 for x in comps if x["delta_mean"] is not None and x["delta_median"] is not None and x["delta_mean"]>0 and x["delta_median"]>0)
            chrono_good.append(good)
        structures.append({
            "trigger_family":key[0],"member_families":list(key[1]),"form":key[2],"size":key[3],
            "tickers_present":ticker_set,"ticker_count":len(ticker_set),"instances":len(rows),
            "usable_instances_n_ge_10":len(usable),"incremental_instances":len(inc),
            "incremental_tickers":sorted({r["ticker"] for r in inc}),
            "incremental_ticker_count":len({r["ticker"] for r in inc}),
            "median_incremental_thirds_per_usable_instance":statistics.median(chrono_good) if chrono_good else None
        })

    out={"format":"MTS_V4_EXPERIMENT_2D_RECURRING_STRUCTURE_ROBUSTNESS_REPLAY_V1",
         "scientific_boundary":BOUNDARY,
         "source_experiment":a.experiment,"source_recurrence":a.recurrence,
         "methodology":{"new_search":False,"new_combinations":False,"candidate_selection":False,
                        "replayed_structures":"only structures already recurring on 2+ tickers in frozen recurrence report",
                        "chronology":"fixed thirds by accepted trade date; no refit",
                        "leave_one_out":"mean sensitivity after removing each accepted trade",
                        "winner_concentration":"share of positive-return sum from top 1/2/3 trades"},
         "instances":results,"structures":structures,
         "structure_count":len(structures),
         "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(f"REPORT={a.output}")
    print(f"STRUCTURES_REPLAYED={len(structures)}")
    print(f"INSTANCES_REPLAYED={len(results)}")
    for n in (2,3,4):
        print(f"STRUCTURES_INCREMENTAL_GE_{n}_TICKERS={sum(s['incremental_ticker_count']>=n for s in structures)}")
    print("CHRONOLOGY=FIXED_THIRDS_NO_REFIT")
    print("CANDIDATE_SELECTION_MUTATED=False")
    print("VERIFICATION_ACCESSED=False")
    print("SOL_CALLS=0")

if __name__=="__main__": main()
