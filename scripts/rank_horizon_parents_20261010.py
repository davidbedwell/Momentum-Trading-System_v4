#!/usr/bin/env python3
"""Descriptive generation-zero parent shortlist. Not a certified selection.

Selection prioritizes lower-confidence-bound net EV and tail risk. No heldout
access, no cross-window promotion, and no claim of multiplicity correction.
"""
import json,pathlib,math,collections,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/"Research/Preparation/horizon_generational_20261010/parent_study"
def finite(v):return isinstance(v,(int,float)) and math.isfinite(v)
def main():
 raw=[json.loads(s) for s in (BASE/"window_reevaluations.jsonl").read_text().splitlines() if s.strip()]
 assert len(raw)==283 and all(x["status"]=="EVALUATED_UNCERTIFIED" for x in raw)
 grouped=collections.defaultdict(list)
 for r in raw:
  a,b=r["window"];p=r["points"];expected=list(range(a,b+1))
  if [x["horizon"] for x in p]!=expected:raise ValueError("Missing window horizons")
  valid=[x for x in p if all(finite(x.get(k)) for k in ("ev_net","lcb95","cvar5","mae_tail5")) and x.get("effective_n",0)>=30]
  # No choosing the single best horizon: require robust within-window evidence.
  strong=[x for x in valid if x["ev_net"]>0 and x["lcb95"]>0]
  s={"window":[a,b],"side":r["side"],"genome_hash":r["genome_hash"],
     "source_index":r["source_index"],"valid_days":len(valid),"positive_lcb_days":len(strong),
     "all_days_positive_lcb":len(strong)==len(expected),
     "median_lcb95":sorted(x["lcb95"] for x in valid)[len(valid)//2] if valid else None,
     "worst_lcb95":min((x["lcb95"] for x in valid),default=None),
     "median_ev_net":sorted(x["ev_net"] for x in valid)[len(valid)//2] if valid else None,
     "worst_cvar5":min((x["cvar5"] for x in valid),default=None),
     "worst_mae_tail5":min((x["mae_tail5"] for x in valid),default=None),
     "status":"PROVISIONAL_NOT_MULTIPLICITY_CORRECTED"}
  grouped[(a,b)].append(s)
 output=[];summary=[]
 for w,rs in sorted(grouped.items()):
  rs.sort(key=lambda x:(x["positive_lcb_days"],x["median_lcb95"] if x["median_lcb95"] is not None else -float("inf"),x["worst_cvar5"] if x["worst_cvar5"] is not None else -float("inf")),reverse=True)
  for rank,x in enumerate(rs,1):x["descriptive_rank"]=rank;output.append(x)
  summary.append({"window":list(w),"candidates":len(rs),"all_days_positive_lcb":sum(x["all_days_positive_lcb"] for x in rs),
                  "any_positive_lcb":sum(x["positive_lcb_days"]>0 for x in rs),
                  "top_five":[{"index":x["source_index"],"side":x["side"],"positive_lcb_days":x["positive_lcb_days"],"median_lcb95":x["median_lcb95"]} for x in rs[:5]]})
 (BASE/"provisional_parent_rankings.jsonl").write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in output))
 (BASE/"provisional_parent_summary.json").write_text(json.dumps({"certification":"NOT_CERTIFIED","method":"within-window breadth of positive nominal LCB95, then median nominal LCB95, then worst CVaR5","windows":summary},indent=2)+"\n")
 print(json.dumps({"windows":len(summary),"candidates":len(output),"fully_positive_lcb":sum(x["all_days_positive_lcb"] for x in output),"top_windows":summary[:3]},indent=2))
if __name__=="__main__":main()
