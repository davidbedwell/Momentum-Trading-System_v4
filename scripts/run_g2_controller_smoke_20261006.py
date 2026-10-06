#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,tempfile,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.conforming_ga.ga_g2 import evolve_g2
from Core.conforming_ga.g2evolution import initial_population_g2
from Core.conforming_ga.g2schema import genome_hash

OUT=ROOT/"Research/Conformance/MTS_G2_CONTROLLER_SMOKE_20261006.json"

def metric(g):
 h=int(genome_hash(g)[:8],16)
 return {"cagr":.05+(h%1000)/100000.,"mdd":-.05,"gross":.5,"safe_fraction":.5,
 "short_share":0.,"turnover":.1,"holdings_hhi":.2,"gfc_return":0.,"recovery_capture":0.}

def hp(r):return {k:[genome_hash(g) for g in v] for k,v in r["populations"].items()}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 mechanics={"plateau_window":1,"plateau_gain_threshold":999.,"migration_interval":1,
 "checkpoint_interval":1,"extension_base":2,"extension_step":1,"extension_max":3,
 "extension_window":1,"extension_threshold":-1.}
 with tempfile.TemporaryDirectory(prefix="mts_g2_smoke_") as td:
  td=Path(td)
  full=evolve_g2(evaluator=metric,master_seed="CONTROLLER_SMOKE",fold=0,generations=2,
   population_size=4,workers=2,checkpoint_dir=td/"full",mechanics=mechanics)
  ck=td/"full/g2_fold0_gen0001.pkl"
  resumed=evolve_g2(evaluator=metric,master_seed="CONTROLLER_SMOKE",fold=0,generations=2,
   population_size=4,workers=2,resume_path=ck,checkpoint_dir=td/"resume",mechanics=mechanics)
  checks={
   "extension_fired":full["events"]["extensions"]==1 and full["final_budget"]==3,
   "migration_exercised":full["events"]["migration_events"]>=1,
   "plateau_freeze_all_islands":full["events"]["freeze_events"]==9 and all(x["frozen"] for x in full["plateau_state"].values()),
   "reallocation_skips_frozen_evaluations":full["events"]["frozen_island_generation_skips"]==9 and all(len(v)==2 for v in full["history"].values()),
   "checkpoint_resume_population_bit_identical":hp(full)==hp(resumed),
   "checkpoint_resume_state_identical":full["plateau_state"]==resumed["plateau_state"] and full["aggregate_hv_history"]==resumed["aggregate_hv_history"] and full["events"]==resumed["events"],
   "terminal_generation_exact":full["completed_generations"]==3 and resumed["completed_generations"]==3,
  }
  report={"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"events":full["events"],
   "test_only_mechanics":mechanics,"production_defaults_unchanged":True,
   "controller":"Core/conforming_ga/ga_g2.py","controller_sha256":sha(ROOT/"Core/conforming_ga/ga_g2.py"),
   "fixture":"Tests/conforming_ga/test_g2_controller_semantics.py","fixture_sha256":sha(ROOT/"Tests/conforming_ga/test_g2_controller_semantics.py")}
  OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
  (OUT.with_suffix(OUT.suffix+".sha256")).write_text(sha(OUT)+"\n")
  print(json.dumps(report,indent=2,sort_keys=True))
  if report["status"]!="PASS":raise SystemExit(2)
if __name__=="__main__":main()
