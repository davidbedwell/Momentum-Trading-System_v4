#!/usr/bin/env python3
"""Fail-closed launch controller for the USER-APPROVED MTS GA redesign.
Scientific requirements are controlled by Research/Protocols/MTS_GA_REDESIGN_EXPERIMENT_FREEZE_20261005.md.
This controller NEVER substitutes the V2 reduced runner.
"""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path("/home/ubuntu/Momentum-Trading-System_v4")
FREEZE=ROOT/"Research/Protocols/MTS_GA_REDESIGN_EXPERIMENT_FREEZE_20261005.md"
RUNNER=ROOT/"scripts/run_ga_redesign_approved_20261006.py"
PREFLIGHT=ROOT/"Tests/test_ga_redesign_approved_preflight_20261006.py"
STATUS=ROOT/"Research/State/MTS_GA_REDESIGN_LAUNCH_STATUS_20261006.json"
LOG=ROOT/"Research/Logs/MTS_GA_REDESIGN_APPROVED_20261006.log"
REPORT=ROOT/"Research/Reports/MTS_GA_REDESIGN_FINAL_REPORT_20261006.md"
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def write(stage,**kw):
    STATUS.parent.mkdir(parents=True,exist_ok=True)
    x={"stage":stage,"time":time.time(),"freeze_sha256":sha(FREEZE),**kw}
    STATUS.write_text(json.dumps(x,indent=2,sort_keys=True))
    print(json.dumps(x,indent=2),flush=True)
def main():
    # Fail closed: old V2 is explicitly prohibited as a launch target.
    missing=[str(p) for p in (RUNNER,PREFLIGHT) if not p.exists()]
    if missing:
        write("IMPLEMENTATION_REQUIRED",missing=missing,
              prohibited_substitute="scripts/run_horizon_free_ga_frozen_architecture_v2_20261005.py")
        return 20
    env=os.environ.copy()
    for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
        env[k]="1"
    q=subprocess.run([str(ROOT/".venv/bin/python"),"-m","pytest","-q",str(PREFLIGHT)],cwd=ROOT,env=env)
    if q.returncode:
        write("PREFLIGHT_FAILED",returncode=q.returncode); return q.returncode
    write("PREFLIGHT_PASSED_LAUNCHING",workers=32,blas_threads=1)
    with open(LOG,"ab",buffering=0) as out:
        p=subprocess.Popen([str(ROOT/".venv/bin/python"),str(RUNNER),"--workers","32","--base-generations","500","--max-generations","800","--post-run-report",str(REPORT)],cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
    write("GA_RUNNING",pid=p.pid,workers=32,blas_threads=1,log=str(LOG),report=str(REPORT))
    return 0
if __name__=="__main__": raise SystemExit(main())
