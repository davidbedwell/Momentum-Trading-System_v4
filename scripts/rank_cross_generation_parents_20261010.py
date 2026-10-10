#!/usr/bin/env python3
"""Produce provisional per-window rankings; no blind access or certification."""
import json,pathlib,collections,statistics,hashlib,math
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"Research/Preparation/horizon_generational_20261010/parent_study"
def load(name):
 return [json.loads(s) for s in (OUT/name).open()]
def main():
 g1=load("window_reevaluations.jsonl");g2=load("gen2_window_reevaluations.jsonl")
 definitions={r["gen1_index"]:r for r in load("gen1_parent_definitions.jsonl")}
 offspring={r["offspring_id"]:r for r in load("gen2_reconciled_ranked_candidates.jsonl")}
 bank=collections.defaultdict(list)
 for generation,rows in ((1,g1),(2,g2)):
  for r in rows:
   if r["status"]!="EVALUATED_UNCERTIFIED":continue
   pts=r["points"];w=tuple(r["window"])
   if len(pts)!=w[1]-w[0]+1 or any(not all(k in p and isinstance(p[k],(int,float)) and math.isfinite(p[k]) for k in ("lcb95","ev_net","cvar5","effective_n")) for p in pts):continue
   lcb=[p["lcb95"] for p in pts];ev=[p["ev_net"] for p in pts];cv=[p["cvar5"] for p in pts]
   ident=r["source_index"]
   genes=(definitions[ident] if generation==1 else offspring[ident])["chromosomes"]
   sig=hashlib.sha256(json.dumps([r["side"],genes],sort_keys=True,separators=(",",":")).encode()).hexdigest()
   bank[w].append({"generation":generation,"id":ident,"window":list(w),"genome_hash":sig,
    "positive_lcb_days":sum(x>0 for x in lcb),"all_lcb_positive":all(x>0 for x in lcb),
    "median_lcb95":statistics.median(lcb),"min_lcb95":min(lcb),"median_ev":statistics.median(ev),
    "worst_cvar5":min(cv),"min_effective_n":min(p["effective_n"] for p in pts),
    "families":sorted({x[0] for x in genes}),"side":r["side"],
    "evidence":"DEV80_EXPLORATORY_UNCERTIFIED"})
 report=[];selected=[];dups=[]
 for w,rows in sorted(bank.items()):
  dedup={}
  for r in rows:
   old=dedup.get(r["genome_hash"])
   if old:
    dups.append({"window":list(w),"kept":old["id"],"removed":r["id"],"generation_removed":r["generation"]})
    if (r["generation"],-r["id"])>(old["generation"],-old["id"]):dedup[r["genome_hash"]]=r
   else:dedup[r["genome_hash"]]=r
  ranked=sorted(dedup.values(),key=lambda r:(r["positive_lcb_days"],r["median_lcb95"],r["min_lcb95"],r["worst_cvar5"],r["min_effective_n"]),reverse=True)
  for i,r in enumerate(ranked,1):r["provisional_rank"]=i
  # Diversity is descriptive only: top 10 + first unseen family signatures among remainder.
  pick=ranked[:10];sigs={tuple(r["families"]) for r in pick}
  for r in ranked[10:]:
   if len(pick)>=15:break
   fs=tuple(r["families"])
   if fs not in sigs:pick.append(r);sigs.add(fs)
  selected.extend(pick)
  report.append({"window":list(w),"evaluated":len(rows),"unique":len(ranked),
   "gen2_evaluated":sum(r["generation"]==2 for r in rows),
   "all_lcb_positive":sum(r["all_lcb_positive"] for r in ranked),
   "top5":[{"id":r["id"],"generation":r["generation"],"positive_lcb_days":r["positive_lcb_days"],
    "median_ev":r["median_ev"],"median_lcb95":r["median_lcb95"],"worst_cvar5":r["worst_cvar5"]} for r in ranked[:5]]})
 (OUT/"cross_generation_window_rankings.jsonl").write_text("".join(json.dumps(r,sort_keys=True)+"\n" for w in sorted(bank) for r in sorted(bank[w],key=lambda x:(x["positive_lcb_days"],x["median_lcb95"],x["min_lcb95"],x["worst_cvar5"]),reverse=True)))
 (OUT/"provisional_diversified_parent_pool.jsonl").write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in selected))
 summary={"status":"PROVISIONAL_UNCERTIFIED_NOT_FROZEN","windows":report,"diversified_parent_assignments":len(selected),"genome_hash_duplicates":len(dups),
 "method":"rank nominal per-day cluster LCB, median LCB, min LCB, worst CVaR5, effective N; first 10 plus up to 5 distinct family signatures per window",
 "limitations":["Selection on DEV80 is not independent validation","No multiple-selection correction for Gen2 combined screen","No independent market episode testing","CVaR5 is per trade not portfolio max drawdown","Gen2 evaluated top 30 only; not all 973","Diversity based on family signature only, not signal correlation"]}
 (OUT/"cross_generation_parent_study_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 print(json.dumps({"status":summary["status"],"selected":len(selected),"duplicates":len(dups),"windows":report},indent=2))
if __name__=="__main__":main()