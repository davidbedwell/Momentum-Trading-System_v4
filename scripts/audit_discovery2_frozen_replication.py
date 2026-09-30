#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path

BOUNDARY="DISCOVERY2_FROZEN_REPLICATION_AUDIT_ONLY_NO_SEARCH_OUTCOME_INSPECTION"

def q(v,p):
 if not v:return None
 s=sorted(v); i=(len(s)-1)*p; lo=int(i); hi=min(lo+1,len(s)-1); f=i-lo
 return s[lo]*(1-f)+s[hi]*f

def summ(v):
 return {"n":len(v),"mean":statistics.fmean(v) if v else None,"median":statistics.median(v) if v else None,
         "q25":q(v,.25),"q75":q(v,.75),"min":min(v) if v else None,"max":max(v) if v else None}

def key(r): return (r["trigger_family"],tuple(sorted(r["member_families"])),r["form"],int(r["size"]))

def audit(name,d):
 apps=d["applications"]; out={}
 for k in sorted({key(r) for r in apps}):
  rs=[r for r in apps if key(r)==k]; usable=[r for r in rs if r["retains_n_ge_10"]]
  inc=[r for r in usable if r["incremental_mean_and_median"]]
  dm=[r["statistics"]["mean"]-r["trigger_baseline_statistics"]["mean"] for r in usable]
  dmed=[r["statistics"]["median"]-r["trigger_baseline_statistics"]["median"] for r in usable]
  bysrc=defaultdict(list); byt=defaultdict(list); bysec=defaultdict(list); bysize=defaultdict(list)
  for r in usable:
   bysrc[r["source_ticker"]].append(r); byt[r["ticker"]].append(r); bysec[r["sector"]].append(r); bysize[r["size_band"]].append(r)
  def groups(g):
   z={}
   for x,v in sorted(g.items()):
    good=[r for r in v if r["incremental_mean_and_median"]]
    z[x]={"usable_instances":len(v),"incremental_instances":len(good),
          "incremental_fraction":len(good)/len(v) if v else None}
   return z
  out["|".join([k[0],"+".join(k[1]),k[2],str(k[3])])]={
   "usable_instances":len(usable),"incremental_instances":len(inc),
   "incremental_fraction":len(inc)/len(usable) if usable else None,
   "usable_tickers":len(byt),"incremental_tickers":len({r["ticker"] for r in inc}),
   "delta_mean":summ(dm),"delta_median":summ(dmed),
   "by_source_ticker":groups(bysrc),"by_target_ticker":groups(byt),
   "by_sector":groups(bysec),"by_size_band":groups(bysize)}
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument("--d2",required=True);p.add_argument("--d2b",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 d2=json.loads(Path(a.d2).read_text()); d2b=json.loads(Path(a.d2b).read_text())
 for d in (d2,d2b):
  if d.get("verification_accessed") is not False or d.get("methodology",{}).get("target_search_results_read") is not False:
   raise RuntimeError("scientific boundary violated")
 audits={"D2_50":audit("D2_50",d2),"D2B_SUPPLEMENT":audit("D2B_SUPPLEMENT",d2b)}
 keys=sorted(set(audits["D2_50"])|set(audits["D2B_SUPPLEMENT"]))
 combined=[]
 for k in keys:
  a1=audits["D2_50"].get(k,{});a2=audits["D2B_SUPPLEMENT"].get(k,{})
  u=a1.get("usable_instances",0)+a2.get("usable_instances",0); inc=a1.get("incremental_instances",0)+a2.get("incremental_instances",0)
  combined.append({"structure":k,"usable_instances":u,"incremental_instances":inc,
   "incremental_fraction":inc/u if u else None,
   "incremental_tickers":a1.get("incremental_tickers",0)+a2.get("incremental_tickers",0),
   "usable_tickers":a1.get("usable_tickers",0)+a2.get("usable_tickers",0)})
 out={"format":"MTS_V4_DISCOVERY2_FROZEN_REPLICATION_AUDIT_V1","scientific_boundary":BOUNDARY,
      "source_d2":a.d2,"source_d2b":a.d2b,
      "methodology":{"search_outputs_inspected":False,"selection_or_refit":False,
       "effect_sizes":"raw endpoint-return delta versus transported trigger baseline",
       "dependence_views":["source_ticker","target_ticker","sector","relative_current_sp500_cap_tercile"],
       "note":"descriptive replication audit; sector/current-cap labels are current metadata, not PIT predictors"},
      "cohorts":audits,"combined":combined,"candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(f"REPORT={a.output}")
 for r in combined:
  print(f"{r['structure']} usable={r['usable_instances']} incremental={r['incremental_instances']} "
        f"fraction={r['incremental_fraction']:.3f} tickers={r['incremental_tickers']}/{r['usable_tickers']}")
 print("SEARCH_OUTPUTS_INSPECTED=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
