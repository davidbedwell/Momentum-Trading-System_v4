#!/usr/bin/env python3
"""Durable fail-closed MTS G2 workflow orchestrator.

Owns approved stage transitions; Chat is not the runtime supervisor.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time,inspect,uuid

REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:sys.path.insert(0,str(REPO))
STATE=REPO/"Research/Conformance/MTS_G2_WORKFLOW_STATE_20261006.json"
HEARTBEAT=REPO/"Research/Conformance/MTS_G2_WORKFLOW_HEARTBEAT_20261006.json"
MANIFEST=REPO/"Research/Protocols/MTS_G2_WORKFLOW_APPROVED_MANIFEST_20261006.json"

STAGES=("NULL_CALIBRATION","ADVERSARIAL_CERTIFICATION","PRODUCTION_GA")
COMMANDS={
 "NULL_CALIBRATION":[str(REPO/".venv/bin/python"),str(REPO/"scripts/run_h7_null_g2_20261006.py")],
 "ADVERSARIAL_CERTIFICATION":[str(REPO/".venv/bin/python"),str(REPO/"scripts/run_g2_certification_20261006.py")],
 "PRODUCTION_GA":[str(REPO/".venv/bin/python"),str(REPO/"scripts/run_g2_production_ga_20261006.py")],
}
EVIDENCE={
 "NULL_CALIBRATION":REPO/"Research/Conformance/MTS_H7_NULL_CALIBRATION_20261006.json",
 "ADVERSARIAL_CERTIFICATION":REPO/"Research/Conformance/MTS_G2_PRODUCTION_CERTIFICATION_20261006.json",
 "PRODUCTION_GA":REPO/"Research/Reports/MTS_G2_PRODUCTION_GA_20261006.json",
}

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def atomic(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+".tmp")
 tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n");os.replace(tmp,path)

def load(path):
 return json.loads(path.read_text())

def evidence_ok(stage):
 p=EVIDENCE[stage]
 if not p.is_file():return False
 try:return bool(load(p).get("passed",False))
 except Exception:return False

def heartbeat(stage,status,**kw):
 atomic(HEARTBEAT,{"workflow":"MTS_G2_PRODUCTION_20261006","stage":stage,"status":status,
   "pid":os.getpid(),"timestamp":time.time(),**kw})

def verify_manifest():
 if not MANIFEST.is_file():raise RuntimeError("APPROVED_MANIFEST_MISSING")
 m=load(MANIFEST)
 if m.get("schema")!="MTS-GA-G2":raise RuntimeError("MANIFEST_SCHEMA_DRIFT")
 # Calibration delta is explicit and isolated: planted=64 only. Null/production remain 250.
 if m["planted"]["population_per_island"]!=64:raise RuntimeError("PLANTED_POP_DRIFT")
 if m["null"]["population_per_island"]!=250 or m["production"]["population_per_island"]!=250:
  raise RuntimeError("PRODUCTION_POP_DRIFT")
 if m["production"]["base_generations"]!=500 or m["production"]["max_generations"]!=800:
  raise RuntimeError("GENERATION_BUDGET_DRIFT")
 if m["production"]["islands"]!=9:raise RuntimeError("ISLAND_CONFIG_DRIFT")
 # Worker count/fold concurrency are execution resources, not scientific parameters.
 # Runtime compute_plan may scale them to available CPUs while population/islands/generation budgets remain frozen.
 if m["production"].get("plateau_structural_mutation_multiplier") is None:
  raise RuntimeError("SCIENTIFIC_BLOCKER: plateau structural-mutation up-weight numeric value is not approved")
 return m

def verify_semantic_fingerprint(m):
 # FIRST gate: bind runtime code plus controlled behavioral fixture evidence.
 b=m.get("mutation_semantic_evidence_binding",{})
 art=REPO/b.get("artifact","");fix=REPO/b.get("fixture","")
 if not art.is_file() or sha(art)!=b.get("artifact_sha256"):raise RuntimeError("SEMANTIC_EVIDENCE_HASH_DRIFT")
 if not fix.is_file() or sha(fix)!=b.get("fixture_sha256"):raise RuntimeError("SEMANTIC_FIXTURE_HASH_DRIFT")
 ev=load(art)
 if not ev.get("passed") or ev.get("fixture_sha256")!=b.get("fixture_sha256"):raise RuntimeError("SEMANTIC_EVIDENCE_NOT_PASS")
 if len(ev.get("controlled_fixtures",[]))!=int(b.get("controlled_fixture_count",-1)):raise RuntimeError("SEMANTIC_FIXTURE_SET_DRIFT")
 return verify_mutation_runtime(m)

def verify_mutation_runtime(m):
 # Runtime half of semantic fingerprint; evidence half is verified above.
 from Core.conforming_ga import g2evolution as ge
 p=m["production"]
 if tuple(p.get("structural_mutation_class_ids",()))!=(4,5,6,11):raise RuntimeError("MUTATION_STRUCTURAL_SET_DRIFT")
 if float(p.get("plateau_structural_mutation_multiplier",0))!=2.0:raise RuntimeError("MUTATION_PLATEAU_MULTIPLIER_DRIFT")
 if int(p.get("plateau_structural_mutation_duration_generations",0))!=40:raise RuntimeError("MUTATION_PLATEAU_WINDOW_DRIFT")
 if ge.STRUCTURAL_MUTATION_CLASSES!=frozenset((4,5,6,11)):raise RuntimeError("RUNTIME_STRUCTURAL_SET_DRIFT")
 expected={4:{"insert":1.0,"delete":1.0,"replace":1.0},5:{"wrap":1.0,"unwrap":1.0},6:{"module_add":1.0,"module_delete":1.0,"module_duplicate":1.0}}
 for c,w in expected.items():
  if ge.WITHIN_CLASS_OPERATION_WEIGHTS[c]!=w:raise RuntimeError(f"WITHIN_CLASS_RATIO_DRIFT:{c}")
 if tuple(ge.WRAP_FAMILIES)!=("ifsoft","softthresh","temporal"):raise RuntimeError("WRAP_FAMILY_DRIFT")
 # Mechanical API separation: multiplier belongs to class selection, never
 # conditional operation selection.
 if "structural_multiplier" not in inspect.signature(ge.choose_mutation_class).parameters:raise RuntimeError("CLASS_FIRST_API_DRIFT")
 if "structural_multiplier" in inspect.signature(ge.choose_operation_within_class).parameters:raise RuntimeError("WITHIN_CLASS_MULTIPLIER_LEAK")
 # Bind exact implementation files used by the run.
 bound=m.get("runtime_code_bindings",{})
 for rel,want in bound.items():
  path=REPO/rel
  if not path.is_file() or sha(path)!=want:raise RuntimeError(f"RUNTIME_CODE_HASH_DRIFT:{rel}")
 # Recursive semantics must be active in imported implementation.
 for name in ("replace_subtree","wrap_subtree","unwrap_subtree"):
  src=inspect.getsource(getattr(ge,name))
  if "_expr_paths" not in src or "_replace_at_path" not in src:raise RuntimeError(f"NONRECURSIVE_MUTATION_DRIFT:{name}")
 return True

def verify_config_diff(m):
 # SECOND gate: complete approved configuration plus exact evidence/runner bindings.
 m=verify_manifest()
 c=m["production"].get("controller_semantic_gate",{})
 for key,hkey in (("controller","controller_sha256"),("fixture","fixture_sha256"),("smoke_runner","smoke_runner_sha256"),("evidence","evidence_sha256")):
  q=REPO/c.get(key,"")
  if not q.is_file() or sha(q)!=c.get(hkey):raise RuntimeError(f"CONTROLLER_GATE_HASH_DRIFT:{key}")
 if load(REPO/c["evidence"]).get("status")!="PASS":raise RuntimeError("CONTROLLER_GATE_NOT_PASS")
 for sec in ("finalist_selection","stage_b_mutation_freeze"):
  z=m["production"][sec]
  for key in ("implementation","fixture"):
   if key in z:
    q=REPO/z[key]
    if not q.is_file() or sha(q)!=z.get(key+"_sha256"):raise RuntimeError(f"{sec.upper()}_HASH_DRIFT:{key}")
 rg=m["null"].get("runner_gate",{})
 for key in ("runner","fixture","fold_worker","compute_plan","compute_fixture"):
  q=REPO/rg.get(key,"")
  if not q.is_file() or sha(q)!=rg.get(key+"_sha256"):raise RuntimeError(f"NULL_RUNNER_GATE_HASH_DRIFT:{key}")
 return m

def verify_null_preflight(m):
 # THIRD gate occurs before any 250/island child workload can be created.
 if m["null"].get("population_per_island")!=250:raise RuntimeError("NULL_POP_DRIFT")
 b=m["null"].get("transformation_conformance",{})
 art=REPO/b.get("artifact","");aud=REPO/b.get("invariant_audit","")
 if not art.is_file() or sha(art)!=b.get("sha256"):raise RuntimeError("NULL_TRANSFORM_EVIDENCE_DRIFT")
 ev=load(art)
 if not ev.get("passed"):raise RuntimeError("NULL_TRANSFORM_NOT_PASS")
 if not aud.is_file() or sha(aud)!=b.get("invariant_audit_sha256"):raise RuntimeError("NULL_INVARIANT_AUDIT_DRIFT")
 if load(aud).get("status")!="PASS":raise RuntimeError("NULL_INVARIANT_AUDIT_NOT_PASS")
 for rel,want in ev.get("bindings",{}).items():
  q=REPO/rel
  if not q.is_file() or sha(q)!=want:raise RuntimeError(f"NULL_BOUND_SOURCE_DRIFT:{rel}")
 runner=REPO/"scripts/run_h7_null_g2_20261006.py"
 if not runner.is_file():raise RuntimeError("NULL_RUNNER_MISSING")
 return True

def run_stage(stage):
 cmd=COMMANDS[stage]
 if not Path(cmd[1]).is_file():raise RuntimeError(f"STAGE_RUNNER_MISSING:{cmd[1]}")
 started=time.time();heartbeat(stage,"RUNNING",command=cmd,started=started,run_id=load(STATE).get("run_id"))
 log=REPO/f"Research/Logs/MTS_G2_WORKFLOW_{stage}_20261006.log";log.parent.mkdir(parents=True,exist_ok=True)
 with open(log,"ab",buffering=0) as out:
  p=subprocess.Popen(cmd,cwd=REPO,stdout=out,stderr=subprocess.STDOUT)
  while p.poll() is None:
   heartbeat(stage,"RUNNING",child_pid=p.pid,elapsed_seconds=time.time()-started,log=str(log.relative_to(REPO)),run_id=load(STATE).get("run_id"))
   time.sleep(30)
 rc=p.returncode
 if rc:raise RuntimeError(f"{stage}_EXIT_{rc}")
 if not evidence_ok(stage):raise RuntimeError(f"{stage}_EVIDENCE_MISSING_OR_FAIL")
 heartbeat(stage,"PASS",elapsed_seconds=time.time()-started,evidence=str(EVIDENCE[stage].relative_to(REPO)))

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--start",choices=STAGES,default="NULL_CALIBRATION");a=ap.parse_args()
 # Manifest/config diff is checked before every transition.
 try:
  m=load(MANIFEST) if MANIFEST.is_file() else None
  start=STAGES.index(a.start)
  now=time.time(); run_id=uuid.uuid4().hex
  state={"workflow":"MTS_G2_PRODUCTION_20261006","status":"RUNNING","stage":a.start,"completed":[],"started":now,"run_id":run_id}
  if STATE.is_file():
   old=load(STATE)
   if old.get("workflow")==state["workflow"]:
    state["completed"]=list(old.get("completed",[]))
    state["previous_execution"]={"run_id":old.get("run_id"),"status":old.get("status"),"stage":old.get("stage"),"error":old.get("error"),"failed_at":old.get("failed_at")}
  state.pop("error",None); state.pop("failed_at",None)
  atomic(STATE,state)
  heartbeat(a.start,"RUNNING",run_id=run_id,resume=True)
  for stage in STAGES[start:]:
   # Allow already-passed durable evidence to advance without rerunning.
   if evidence_ok(stage):
    if stage not in state["completed"]:state["completed"].append(stage)
    state["stage"]=stage;atomic(STATE,state);continue
   # Required launch ordering: semantic fingerprint -> config diff ->
   # null-specific preflight -> workload creation.
   m=load(MANIFEST)
   verify_semantic_fingerprint(m)
   heartbeat(stage,"SEMANTIC_FINGERPRINT_PASS")
   m=verify_config_diff(m)
   heartbeat(stage,"CONFIG_DIFF_PASS")
   if stage=="NULL_CALIBRATION":
    verify_null_preflight(m)
    heartbeat(stage,"NULL_PREFLIGHT_PASS")
   state["stage"]=stage;atomic(STATE,state)
   run_stage(stage)
   state["completed"].append(stage);atomic(STATE,state)
  state["status"]="PASS";state["finished"]=time.time();atomic(STATE,state);heartbeat("COMPLETE","PASS")
  return 0
 except Exception as e:
  state=load(STATE) if STATE.is_file() else {"workflow":"MTS_G2_PRODUCTION_20261006"}
  state.update({"status":"BLOCKED","error":str(e),"failed_at":time.time()});atomic(STATE,state)
  heartbeat(state.get("stage","UNKNOWN"),"BLOCKED",error=str(e))
  print("MTS_G2_WORKFLOW_BLOCKED",e,file=sys.stderr);return 2

if __name__=="__main__":raise SystemExit(main())
