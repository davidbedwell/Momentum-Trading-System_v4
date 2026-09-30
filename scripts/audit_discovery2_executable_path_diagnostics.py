#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path

STOPS=("0.020000","0.050000","0.100000","0.150000")
def sk(r): return (r["trigger_family"],tuple(sorted(r["member_families"])),r["form"],int(r["size"]))
def med(x): return statistics.median(x) if x else None
def mean(x): return statistics.fmean(x) if x else None
def q(x,p):
 if not x:return None
 s=sorted(x);i=(len(s)-1)*p;lo=int(i);hi=min(lo+1,len(s)-1);f=i-lo
 return s[lo]*(1-f)+s[hi]*f
def desc(x): return {"n":len(x),"mean":mean(x),"median":med(x),"q25":q(x,.25),"q75":q(x,.75),"min":min(x) if x else None,"max":max(x) if x else None}

def cohort(path):
 d=json.loads(Path(path).read_text())
 if d["methodology"]["target_search_results_read"] is not False or d["verification_accessed"] is not False: raise RuntimeError("boundary")
 return d

def main():
 p=argparse.ArgumentParser();p.add_argument("--d2",required=True);p.add_argument("--d2b",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 ds=[("D2_50",cohort(a.d2)),("D2B_SUPPLEMENT",cohort(a.d2b))]
 rows=[]
 for cname,d in ds:
  for r in d["applications"]: rows.append((cname,r))
 groups=defaultdict(list)
 for cname,r in rows: groups[sk(r)].append((cname,r))
 outrows=[]
 for k,rs in sorted(groups.items()):
  usable=[(c,r) for c,r in rs if r["composite"]["trade_count"]>=10 and r["trigger_baseline"]["trade_count"]>=10]
  fixed=[r["delta_fixed_mean"] for _,r in usable if r["delta_fixed_mean"] is not None]
  maes=[];mfes=[]
  for _,r in usable:
   cm=r["composite"]["mae_return"]["mean"];bm=r["trigger_baseline"]["mae_return"]["mean"]
   cf=r["composite"]["mfe_return"]["mean"];bf=r["trigger_baseline"]["mfe_return"]["mean"]
   if cm is not None and bm is not None:maes.append(cm-bm)
   if cf is not None and bf is not None:mfes.append(cf-bf)
  stop={}
  for s in STOPS:
   sr=[r for _,r in usable if s in r["stop_deltas"]]
   dm=[r["stop_deltas"][s]["delta_mean_realized_return"] for r in sr]
   dr=[r["stop_deltas"][s]["delta_gross_ev_r"] for r in sr]
   both=[r for r in sr if r["stop_deltas"][s]["delta_mean_realized_return"]>0 and r["stop_deltas"][s]["delta_median_realized_return"]>0]
   tick={r["ticker"] for r in both}
   cr=[r["composite"]["stop_scenarios"][s]["stop_rate"] for r in sr]
   br=[r["trigger_baseline"]["stop_scenarios"][s]["stop_rate"] for r in sr]
   stop[s]={"instances":len(sr),"improved_mean_and_median":len(both),"improved_tickers":len(tick),
    "delta_mean_realized_return":desc(dm),"delta_gross_ev_r":desc(dr),
    "composite_stop_rate":desc(cr),"baseline_stop_rate":desc(br),
    "median_stop_rate_delta":med([x-y for x,y in zip(cr,br)]) if sr else None}
  outrows.append({"trigger_family":k[0],"member_families":list(k[1]),"form":k[2],"size":k[3],
   "usable_instances":len(usable),"usable_tickers":len({r["ticker"] for _,r in usable}),
   "fixed_horizon_delta_mean":desc(fixed),"mae_mean_delta":desc(maes),"mfe_mean_delta":desc(mfes),"stops":stop,
   "by_cohort":{c:{"usable":sum(1 for cc,_ in usable if cc==c)} for c,_ in ds}})
 out={"format":"MTS_V4_DISCOVERY2_EXECUTABLE_PATH_DIAGNOSTICS_V1",
  "scientific_boundary":"FROZEN_EXECUTABLE_REPLICATION_DIAGNOSTICS_NO_SEARCH_INSPECTION_NOT_VALIDATION",
  "sources":[a.d2,a.d2b],"methodology":{"stop_fractions":[.02,.05,.10,.15],"stop_selection":False,
   "transaction_costs":"NOT_APPLIED","mae_delta":"composite mean MAE minus trigger mean MAE; positive means less adverse excursion",
   "mfe_delta":"composite mean MFE minus trigger mean MFE; positive means greater favorable excursion",
   "all_usable_transported_applications_included":True,"target_search_results_read":False,"refit":False},
  "structures":outrows,"candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(f"REPORT={a.output}")
 for i,r in enumerate(outrows,1):
  print(f"{i}. {r['trigger_family']}|{'+'.join(r['member_families'])}|{r['form']} usable={r['usable_instances']} tickers={r['usable_tickers']}")
  print(f"   MAE_DELTA_MED={r['mae_mean_delta']['median']:.6f} MFE_DELTA_MED={r['mfe_mean_delta']['median']:.6f}")
  for s in STOPS:
   z=r["stops"][s]; print(f"   STOP={float(s):.0%} improved={z['improved_mean_and_median']}/{z['instances']} tickers={z['improved_tickers']} delta_mean_med={z['delta_mean_realized_return']['median']:.6f} stoprate_delta_med={z['median_stop_rate_delta']:.6f}")
 print("STOP_SELECTED=False");print("TARGET_SEARCH_RESULTS_READ=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
