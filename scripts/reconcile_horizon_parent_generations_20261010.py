#!/usr/bin/env python3
"""Reconcile Gen1 and Gen2 genomes and create a traceable, provisional parent bank."""
import pathlib,json,csv,hashlib,collections,math
ROOT=pathlib.Path(__file__).resolve().parents[1]
G1=ROOT/"Research/Preparation/horizon_generational_20261010/Research/Runs/gen1-merit-screen-20261008/holding_window_chromosome_archive_20261009"
G2=ROOT/"Research/Runs/gen2-200-parent-20261010"
FREEZE=ROOT/"Research/Governance/GEN2_200_PARENT_FREEZE_20261009/frozen_200_parent_genomes.jsonl"
OUT=ROOT/"Research/Preparation/horizon_generational_20261010/parent_study"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 original={}
 for f in sorted(G1.glob("window_*_chromosomes.json")):
  d=json.loads(f.read_text())
  for g in d["genomes"]:
   k=g["index"];v={"chromosomes":g["chromosomes"],"side":g["side"],"families":g["families"]}
   if k in original and original[k]!=v:raise ValueError(f"Conflicting Gen1 identity {k}")
   original[k]=v
 for line in FREEZE.open():
  g=json.loads(line);original.setdefault(g["index"],{"chromosomes":g["chromosomes"],"side":g["side"],"families":g["families"]})
 offspring={}
 for s in (G2/"offspring.jsonl").open():
  r=json.loads(s);i=r["offspring_id"]
  if i in offspring:raise ValueError(f"Duplicate Gen2 ID {i}")
  offspring[i]=r
 rank=list(csv.DictReader((G2/"gen2_gen1_criteria_ranking.csv").open()))
 if len(rank)!=973:raise ValueError("Unexpected ranking length")
 evaluated={}
 for s in (G2/"evaluations.jsonl").open():
  r=json.loads(s);evaluated[r["offspring_id"]]=r
 out=[];missing=[];parents=collections.Counter()
 for r in rank:
  i=int(r["offspring_id"]);g=offspring.get(i);e=evaluated.get(i)
  if not g or not e or g["genome_hash"]!=r["genome_hash"] or e["genome_hash"]!=r["genome_hash"]:raise ValueError(f"Gen2 lineage mismatch {i}")
  pids=g["parent_indices"];absent=[p for p in pids if p not in original]
  if absent:missing.append({"offspring_id":i,"missing_gen1_parents":absent})
  parents.update(pids)
  out.append({"generation":2,"offspring_id":i,"overall_priority":int(r["overall_priority"]),
   "pareto_front":int(r["pareto_front"]),"genome_hash":r["genome_hash"],
   "parents":pids,"parents_resolved":not absent,"side":g["side"],"chromosomes":g["chromosomes"],
   "families":sorted({x[0] for x in g["chromosomes"]}),
   "best_horizon":int(r["best_horizon"]),"ev_net":float(r["ev_net"]),"lcb95":float(r["lcb95"]),
   "effective_n":int(r["effective_n"]),"cvar5_best":float(r["cvar5_best"]),
   "lcb_positive_count":int(r["lcb_positive_count"]),"positive_count":int(r["positive_count"]),
   "classification":"EXPLORATORY_CANDIDATE_NOT_CERTIFIED"})
 (OUT/"gen2_reconciled_ranked_candidates.jsonl").write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in out))
 (OUT/"gen1_parent_definitions.jsonl").write_text("".join(json.dumps({"gen1_index":k,**v},sort_keys=True)+"\n" for k,v in sorted(original.items())))
 summary={"status":"LINEAGE_AUDITED_PARENT_SELECTION_PENDING","gen1_unique_definitions":len(original),
  "gen2_ranked_candidates":len(out),"gen2_ranked_missing_parent_definitions":len(missing),
  "gen2_missing_parent_details":missing[:30],"gen2_top30":[{"id":x["offspring_id"],"priority":x["overall_priority"],"ev_net":x["ev_net"],"lcb95":x["lcb95"],"cvar5_best":x["cvar5_best"],"parents":x["parents"],"parents_resolved":x["parents_resolved"]} for x in out[:30]],
  "source_sha256":{"frozen_200_parents":sha(FREEZE),"offspring":sha(G2/"offspring.jsonl"),"evaluations":sha(G2/"evaluations.jsonl"),"ranking":sha(G2/"gen2_gen1_criteria_ranking.csv"),"manifest":sha(G2/"manifest.json")},
  "note":"Original Gen2 63-session evidence is not equivalent to reevaluated per-window parent fitness; not certified for promotion."}
 (OUT/"generation_reconciliation_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 print(json.dumps({k:v for k,v in summary.items() if k not in ("gen2_top30","source_sha256","gen2_missing_parent_details")},indent=2))
 print("TOP10",[(x["offspring_id"],x["parents"],x["parents_resolved"]) for x in out[:10]])
if __name__=="__main__":main()