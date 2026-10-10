#!/usr/bin/env python3
"""Generation-zero parent evidence audit; never certify missing window horizons."""
import pathlib,json,hashlib,collections,math
ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=ROOT/"Research/Preparation/horizon_generational_20261010/Research/Runs/gen1-merit-screen-20261008/holding_window_chromosome_archive_20261009"
OUT=ROOT/"Research/Preparation/horizon_generational_20261010/parent_study"
def run():
 OUT.mkdir(parents=True,exist_ok=True)
 rows=[];families=collections.Counter();seen={}
 for f in sorted(SRC.glob("window_*_chromosomes.json")):
  raw=f.read_bytes();d=json.loads(raw);a,b=d["window"]
  for g in d["genomes"]:
   chrom=g["chromosomes"];side=g["side"]
   key=hashlib.sha256(json.dumps([side,chrom],sort_keys=True,separators=(",",":")).encode()).hexdigest()
   families.update(x[0] for x in chrom)
   hs={int(x["horizon"]):x for x in g["horizons"]}
   required=set(range(a,b+1));missing=sorted(required-set(hs))
   observed=[hs[h] for h in sorted(required & set(hs))]
   def metric(x):return round(x,8) if isinstance(x,(int,float)) and math.isfinite(x) else None
   score=max((float(x["lcb95"]) for x in observed if x.get("lcb95") is not None),default=None)
   rows.append({"window":[a,b],"side":side,"genome_hash":key,"source_file":f.name,"source_index":g["index"],
    "families":[x[0] for x in chrom],"screen_pass":g.get("screen_pass"),
    "observed_horizons":sorted(required&set(hs)),"missing_horizons":missing,
    "best_observed_lcb95":metric(score),"min_observed_cvar5":metric(min((x["cvar5"] for x in observed),default=float("nan"))),
    "max_observed_effective_n":max((x["effective_n"] for x in observed),default=None),
    "parent_eligibility":"PROVISIONAL_REQUIRES_WINDOW_REEVALUATION" if missing else "REQUIRES_MULTIPLICITY_AND_RISK_AUDIT"})
   seen[key]=1
 summary={"status":"PARENT_SELECTION_NOT_CERTIFIED","window_count":13,"assignments":len(rows),
  "unique_genomes":len(seen),"family_counts":dict(sorted(families.items())),
  "fully_measured_assignments":sum(not x["missing_horizons"] for x in rows),
  "source_sha256":{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(SRC.glob("window_*_chromosomes.json"))},
  "method":"No ranking from unmeasured days; LCB95 on available days is descriptive only, not multiplicity corrected.",
  "next_step":"Reevaluate frozen genomes on every day within each window using causal DEV80 paths; then rank LCB, net EV, tail loss, independence and family diversity."}
 (OUT/"parent_evidence_inventory.jsonl").write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in rows))
 (OUT/"parent_study_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 print(json.dumps({k:v for k,v in summary.items() if k!="source_sha256"},indent=2))
if __name__=="__main__":run()
