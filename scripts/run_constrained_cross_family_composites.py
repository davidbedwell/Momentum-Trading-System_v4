#!/usr/bin/env python3
import argparse,itertools,json,math,statistics
from collections import defaultdict
from pathlib import Path

BOUNDARY="DISCOVERY_COMPOSITE_EXPERIMENT_2_ONLY_NOT_VALIDATION_NOT_PROMOTION"
def st(v):
    return {"count":len(v),"mean":statistics.fmean(v) if v else None,
            "median":statistics.median(v) if v else None,
            "positive_fraction":sum(x>0 for x in v)/len(v) if v else None}
def load_candidate(r):
    d=json.loads(Path(r["source_report"]).read_text())
    opts=r["optimizers"]
    for o in opts:
        for c in d["results"][r["family"]][o]:
            if c.get("candidate_id")==r["candidate_id"]: return c
    raise RuntimeError("candidate not found: "+str(r["candidate_id"]))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();m=json.loads(Path(a.manifest).read_text())
    if m.get("verification_accessed") is not False: raise SystemExit("verification boundary violated")
    rows=m["retained_candidates"]; by=defaultdict(list)
    for r in rows:
        c=load_candidate(r)
        paths=sorted(c.get("paths",[]),key=lambda x:str(x["signal_date"]))
        rr=dict(r);rr["_paths"]=paths;rr["_signals"]={str(x["signal_date"]) for x in paths}
        rr["_base"]=st([float(x["fixed_horizon_return"]) for x in paths]);by[r["ticker"]].append(rr)
    outrows=[]
    for ticker,cs in sorted(by.items()):
      for k in (2,3,4):
       for group in itertools.combinations(cs,k):
        fams=[x["family"] for x in group]
        if len(set(fams))<k: continue
        modes=["ALL"] + (["2_OF_3"] if k==3 else []) + (["3_OF_4"] if k==4 else [])
        for trigger in group:
         others=[x for x in group if x is not trigger]
         for mode in modes:
          kept=[]
          for path in trigger["_paths"]:
            day=str(path["signal_date"])
            votes=1+sum(day in x["_signals"] for x in others)
            need=k if mode=="ALL" else (2 if mode=="2_OF_3" else 3)
            if votes>=need: kept.append(path)
          vals=[float(x["fixed_horizon_return"]) for x in kept]
          s=st(vals); b=trigger["_base"]
          outrows.append({
            "ticker":ticker,"size":k,"mode":mode,
            "trigger_family":trigger["family"],
            "trigger_candidate_id":trigger["candidate_id"],
            "member_families":fams,
            "member_candidate_ids":[x["candidate_id"] for x in group],
            "statistics":s,"trigger_baseline_statistics":b,
            "delta_mean_vs_trigger":(s["mean"]-b["mean"]) if vals else None,
            "delta_median_vs_trigger":(s["median"]-b["median"]) if vals else None,
            "retains_n_ge_10":len(vals)>=10,
            "incremental_mean_positive":bool(vals) and s["mean"]>b["mean"],
            "incremental_median_positive":bool(vals) and s["median"]>b["median"],
            "signal_dates":[str(x["signal_date"]) for x in kept],
        })
    usable=[r for r in outrows if r["retains_n_ge_10"]]
    incremental=[r for r in usable if r["incremental_mean_positive"] and r["incremental_median_positive"]]
    out={"format":"MTS_V4_CONSTRAINED_CROSS_FAMILY_COMPOSITE_EXPERIMENT_2_V1",
         "scientific_boundary":BOUNDARY,
         "design":{
           "source":"frozen retained Experiment-1 candidates only",
           "group_sizes":[2,3,4],
           "forms":{"2":["ALL"],"3":["ALL","2_OF_3"],"4":["ALL","3_OF_4"]},
           "execution":"each member is evaluated in turn as the trigger; trigger preserves its frozen horizon/return path; other members act only as same-signal-date gates",
           "no_weights":True,"no_threshold_optimization":True,"no_refit":True,
           "minimum_n_for_comparison":10,
           "incremental_test":"composite mean and median must both exceed its trigger baseline; descriptive Discovery test, not promotion"
         },
         "composites":outrows,"usable_n_ge_10_count":len(usable),
         "incremental_mean_and_median_count":len(incremental),
         "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(f"REPORT={a.output}");print(f"TICKERS={len(by)}")
    print(f"COMPOSITES_EVALUATED={len(outrows)}");print(f"USABLE_N_GE_10={len(usable)}")
    print(f"INCREMENTAL_MEAN_AND_MEDIAN={len(incremental)}")
    for k in (2,3,4):
      x=[r for r in usable if r["size"]==k]
      y=[r for r in x if r["incremental_mean_positive"] and r["incremental_median_positive"]]
      print(f"SIZE_{k}_USABLE={len(x)} SIZE_{k}_INCREMENTAL={len(y)}")
    print("CANDIDATE_SELECTION_MUTATED=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__": main()
