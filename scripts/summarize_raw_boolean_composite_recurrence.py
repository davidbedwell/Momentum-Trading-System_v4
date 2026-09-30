#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path

BOUNDARY="DISCOVERY_EXPERIMENT_2D_RECURRENCE_ANALYSIS_ONLY_NOT_VALIDATION_NOT_PROMOTION"

def med(v): return statistics.median(v) if v else None
def mean(v): return statistics.fmean(v) if v else None

def thirds(rows):
    rows=sorted(rows,key=lambda r:r["date"])
    n=len(rows)
    if n<3: return []
    cuts=[0,n//3,(2*n)//3,n]
    out=[]
    for j in range(3):
        seg=rows[cuts[j]:cuts[j+1]]
        vals=[x["ret"] for x in seg]
        out.append({"third":j+1,"count":len(vals),
                    "mean":mean(vals),"median":med(vals),
                    "positive_fraction":sum(x>0 for x in vals)/len(vals) if vals else None,
                    "first_date":seg[0]["date"] if seg else None,
                    "last_date":seg[-1]["date"] if seg else None})
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--experiment",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    d=json.loads(Path(a.experiment).read_text())
    if d.get("verification_accessed") is not False or d.get("candidate_selection_mutated") is not False:
        raise SystemExit("scientific boundary violated")
    comps=d["composites"]

    # Structure ignores candidate IDs and ticker, retaining only conceptual form.
    groups=defaultdict(list)
    for r in comps:
        key=(r["trigger_family"],tuple(sorted(r["member_families"])),r["form"],int(r["size"]))
        groups[key].append(r)

    summaries=[]
    for key,rows in sorted(groups.items()):
        trigger,members,form,size=key
        by_ticker=defaultdict(list)
        for r in rows: by_ticker[r["ticker"]].append(r)
        ticker_rows=[]
        for ticker,trs in sorted(by_ticker.items()):
            # Same conceptual structure can arise from candidate-ID variants. Summarize without selecting a winner:
            # record all usable instances, and ticker-level median deltas across those usable instances.
            usable=[x for x in trs if x["retains_n_ge_10"]]
            inc=[x for x in usable if x["incremental_mean_positive"] and x["incremental_median_positive"]]
            dm=[x["delta_mean_vs_trigger"] for x in usable if x["delta_mean_vs_trigger"] is not None]
            dmed=[x["delta_median_vs_trigger"] for x in usable if x["delta_median_vs_trigger"] is not None]
            ticker_rows.append({
                "ticker":ticker,"instances_tested":len(trs),"usable_instances":len(usable),
                "incremental_instances":len(inc),
                "median_delta_mean":med(dm),"median_delta_median":med(dmed),
                "all_usable_incremental":bool(usable) and len(inc)==len(usable),
                "any_usable_incremental":bool(inc)
            })
        usable=[r for r in rows if r["retains_n_ge_10"]]
        inc=[r for r in usable if r["incremental_mean_positive"] and r["incremental_median_positive"]]
        tickers_tested=sorted({r["ticker"] for r in rows})
        tickers_usable=sorted({r["ticker"] for r in usable})
        tickers_incremental=sorted({r["ticker"] for r in inc})
        dm=[r["delta_mean_vs_trigger"] for r in usable if r["delta_mean_vs_trigger"] is not None]
        dmed=[r["delta_median_vs_trigger"] for r in usable if r["delta_median_vs_trigger"] is not None]
        ns=[r["statistics"]["count"] for r in usable]

        summaries.append({
            "trigger_family":trigger,"member_families":list(members),"form":form,"size":size,
            "instances_tested":len(rows),"usable_instances_n_ge_10":len(usable),
            "incremental_instances":len(inc),
            "incremental_fraction_of_usable":len(inc)/len(usable) if usable else None,
            "tickers_tested":tickers_tested,"tickers_tested_count":len(tickers_tested),
            "tickers_usable":tickers_usable,"tickers_usable_count":len(tickers_usable),
            "tickers_incremental":tickers_incremental,"tickers_incremental_count":len(tickers_incremental),
            "median_delta_mean":med(dm),"mean_delta_mean":mean(dm),
            "median_delta_median":med(dmed),"mean_delta_median":mean(dmed),
            "median_n":med(ns),"min_n":min(ns) if ns else None,"max_n":max(ns) if ns else None,
            "ticker_detail":ticker_rows
        })

    # Chronological stability for every usable incremental instance, using accepted signal dates
    # and the return values already represented by its frozen statistics cannot be reconstructed
    # from the 2D artifact alone because per-trade returns were not stored. Mark explicitly.
    recurring=[s for s in summaries if s["tickers_incremental_count"]>=2]
    out={
        "format":"MTS_V4_EXPERIMENT_2D_CROSS_TICKER_RECURRENCE_V1",
        "scientific_boundary":BOUNDARY,
        "source_experiment":a.experiment,
        "methodology":{
            "new_search":False,"candidate_selection":False,"winner_picking_within_structure":False,
            "structure_key":"trigger_family + sorted member_families + form + group_size",
            "ticker_level_summary":"median across all usable candidate-ID instances for the same conceptual structure",
            "recurrence_threshold_reported":"2+ tickers with at least one usable incremental instance",
            "chronological_stability":"UNAVAILABLE_FROM_2D_ARTIFACT_BECAUSE_PER_TRADE_RETURNS_WERE_NOT_STORED; requires deterministic replay, not new search"
        },
        "structures":summaries,
        "recurring_structures_ge_2_tickers":recurring,
        "structure_count":len(summaries),
        "recurring_structure_count_ge_2_tickers":len(recurring),
        "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(f"REPORT={a.output}")
    print(f"STRUCTURES={len(summaries)}")
    print(f"RECURRING_STRUCTURES_GE_2_TICKERS={len(recurring)}")
    for n in (2,3,4,5):
        print(f"RECUR_GE_{n}_TICKERS={sum(s['tickers_incremental_count']>=n for s in summaries)}")
    print("CHRONOLOGY=REQUIRES_DETERMINISTIC_REPLAY_NO_NEW_SEARCH")
    print("CANDIDATE_SELECTION_MUTATED=False")
    print("VERIFICATION_ACCESSED=False")
    print("SOL_CALLS=0")

if __name__=="__main__": main()
