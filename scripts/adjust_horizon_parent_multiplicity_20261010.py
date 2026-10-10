#!/usr/bin/env python3
"""Conservative within-window Bonferroni parent evidence, not full GA certification.

Uses already computed cluster standard errors, adjusts for 283x64 screened
genome-horizon tests. Does NOT fix shared-market dependence or search bias.
"""
import json,pathlib,math,statistics,collections
BASE=pathlib.Path(__file__).resolve().parents[1]/"Research/Preparation/horizon_generational_20261010/parent_study"
def main():
 raw=[json.loads(s) for s in (BASE/"window_reevaluations.jsonl").read_text().splitlines() if s.strip()]
 m=sum(len(r["points"]) for r in raw)
 z=statistics.NormalDist().inv_cdf(1-.05/m)
 ranked=[]
 for r in raw:
  points=r["points"];adjusted=[]
  for p in points:
   ev=p.get("ev_net");se=p.get("se_cluster");n=p.get("effective_n",0)
   if not isinstance(ev,(int,float)) or not isinstance(se,(int,float)) or not math.isfinite(ev) or not math.isfinite(se) or n<30:
    adjusted.append(None)
   else:adjusted.append(ev-z*se)
  valid=[x for x in adjusted if x is not None]
  ranked.append({"window":r["window"],"genome_hash":r["genome_hash"],"source_index":r["source_index"],"side":r["side"],
   "adjusted_lcb_by_day":adjusted,"all_days_adjusted_positive":len(valid)==len(points) and all(x>0 for x in valid),
   "positive_adjusted_days":sum(x>0 for x in valid),
   "median_adjusted_lcb":statistics.median(valid) if valid else None,
   "worst_adjusted_lcb":min(valid) if valid else None,
   "worst_cvar5":min((p.get("cvar5",float("inf")) for p in points),default=None),
   "status":"CONSERVATIVE_SCREEN_ONLY_NOT_EPISODE_CERTIFIED"})
 by=collections.defaultdict(list)
 for r in ranked:by[tuple(r["window"])].append(r)
 for group in by.values():
  group.sort(key=lambda x:(x["positive_adjusted_days"],x["median_adjusted_lcb"] if x["median_adjusted_lcb"] is not None else -1e99,x["worst_cvar5"]),reverse=True)
  for i,r in enumerate(group,1):r["provisional_rank_adjusted"]=i
 (BASE/"multiplicity_adjusted_parent_screen.jsonl").write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in ranked))
 summary={"test_count":m,"bonferroni_z":z,"total_candidates":len(ranked),
  "all_days_positive_adjusted":sum(r["all_days_adjusted_positive"] for r in ranked),
  "windows":[{"window":list(k),"candidates":len(v),"all_days_positive_adjusted":sum(r["all_days_adjusted_positive"] for r in v),
    "top_five":[{"index":r["source_index"],"side":r["side"],"positive_adjusted_days":r["positive_adjusted_days"],
     "median_adjusted_lcb":r["median_adjusted_lcb"]} for r in v[:5]]} for k,v in sorted(by.items())],
  "certification":"NOT_CERTIFIED",
  "limitations":["Bonferroni controls nominal multiple comparisons conditional on these SE estimates; cluster independence is not established.",
  "GA selection/search and market episode dependence require separate correction and independent validation.",
  "No automatic parent promotion or launch authorized."]}
 (BASE/"multiplicity_adjusted_parent_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 print(json.dumps({"test_count":m,"bonferroni_z":z,"all_days_positive_adjusted":summary["all_days_positive_adjusted"],"first_window":summary["windows"][0]},indent=2))
if __name__=="__main__":main()
