#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,statistics
from collections import defaultdict
from pathlib import Path

EXPECTED_SHA="de141535ab20f45c2bb136456a306eadf0951e6e9ccbb93b74477622ca7be4e0"
STOPS=("0.020000","0.050000","0.100000","0.150000")

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def med(xs): return statistics.median(xs) if xs else None

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--input",required=True);p.add_argument("--output",required=True)
 a=p.parse_args()
 if sha(a.input)!=EXPECTED_SHA: raise RuntimeError("frozen executable report hash mismatch")
 d=json.loads(Path(a.input).read_text())
 if d.get("format")!="MTS_V4_VERIFICATION_A1_EXECUTABLE_REPLAY_V1": raise RuntimeError("wrong input format")
 if d.get("verification_a_remaining_accessed") is not False or d.get("verification_b_accessed") is not False: raise RuntimeError("verification boundary violated")
 rows=[r for t in d["targets"] for r in t["applications"]]
 groups=defaultdict(list)
 for r in rows:
  k=(r["trigger_family"],tuple(sorted(r["member_families"])),r["form"],int(r["size"]))
  groups[k].append(r)
 out_groups=[]
 for k,rs in sorted(groups.items()):
  usable=[r for r in rs if r["composite"]["trade_count"]>=10 and r["trigger_baseline"]["trade_count"]>=10]
  stop_summary={}
  for sk in STOPS:
   q=[r for r in usable if sk in r["stop_deltas"]]
   meanv=[r["stop_deltas"][sk]["delta_mean_realized_return"] for r in q if r["stop_deltas"][sk]["delta_mean_realized_return"] is not None]
   medv=[r["stop_deltas"][sk]["delta_median_realized_return"] for r in q if r["stop_deltas"][sk]["delta_median_realized_return"] is not None]
   evr=[r["stop_deltas"][sk]["delta_gross_ev_r"] for r in q if r["stop_deltas"][sk]["delta_gross_ev_r"] is not None]
   both=[r for r in q if r["stop_deltas"][sk]["delta_mean_realized_return"] is not None and r["stop_deltas"][sk]["delta_median_realized_return"] is not None and r["stop_deltas"][sk]["delta_mean_realized_return"]>0 and r["stop_deltas"][sk]["delta_median_realized_return"]>0]
   stop_summary[sk]={
    "usable_instances":len(q),"positive_mean_and_median_instances":len(both),
    "fraction_positive_both":len(both)/len(q) if q else None,
    "positive_ticker_breadth":len({r["ticker"] for r in both}),
    "usable_ticker_breadth":len({r["ticker"] for r in q}),
    "median_delta_mean_realized_return":med(meanv),
    "median_delta_median_realized_return":med(medv),
    "median_delta_gross_ev_r":med(evr)}
  out_groups.append({"trigger_family":k[0],"member_families":list(k[1]),"form":k[2],"size":k[3],
   "usable_instances":len(usable),"usable_tickers":len({r["ticker"] for r in usable}),"stops":stop_summary})
 result={"format":"MTS_V4_VERIFICATION_A1_FROZEN_STOP_DIAGNOSTICS_V1",
  "source_sha256":EXPECTED_SHA,
  "scientific_role":"DIAGNOSTIC_ONLY_NO_STOP_SELECTION_NO_OPTIMIZATION",
  "stops_evaluated":[0.02,0.05,0.10,0.15],
  "selection_permitted":False,"ranking_permitted":False,"refit":False,"search_run":False,
  "verification_a_remaining_accessed":False,"verification_b_accessed":False,"sol_calls":0,
  "structures":out_groups}
 Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("REPORT="+a.output)
 for g in out_groups:
  print(f"STRUCT {g['trigger_family']}|{'+'.join(g['member_families'])}|{g['form']}")
  for sk in STOPS:
   z=g["stops"][sk]
   print(f" STOP {float(sk)*100:.0f}% positive={z['positive_mean_and_median_instances']}/{z['usable_instances']} frac={(z['fraction_positive_both'] or 0):.3f} tickers={z['positive_ticker_breadth']}/{z['usable_ticker_breadth']} medDMean={(z['median_delta_mean_realized_return'] or 0):.6f} medDMedian={(z['median_delta_median_realized_return'] or 0):.6f} medDEVR={(z['median_delta_gross_ev_r'] or 0):.6f}")
 print("STOP_SELECTION=False");print("STOP_RANKING=False");print("SEARCH_RUN=False");print("REFIT=False");print("VERIFICATION_A_REMAINING_ACCESSED=False");print("VERIFICATION_B_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
