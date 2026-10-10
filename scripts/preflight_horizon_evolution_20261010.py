#!/usr/bin/env python3
"""Pre-launch gate for the independent 13-window evolutionary experiment.

Fail closed on evaluator mismatch, missing source data, or absent certification.
Never starts a paid compute job.
"""
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
WINDOWS=((2,5),(6,10),(11,15),(16,20),(21,25),(26,30),(31,35),(36,40),(41,45),(46,50),(51,55),(56,60),(61,65))
REQUIRED_HORIZONS=tuple(range(2,66))
BASE=ROOT/"Research/Preparation/horizon_generational_20261010"
ARCHIVE=BASE/"Research/Runs/gen1-merit-screen-20261008/holding_window_chromosome_archive_20261009"
PRED=ROOT/"Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet"
ARRAY=ROOT/"Research/Runs/gen1-merit-screen-20261008/phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz"
def check():
    from scripts.prepare_horizon_generation_study_20261010 import prepare
    report=prepare(ARCHIVE,BASE)
    reasons=[]
    for p in (PRED,ARRAY):
        if not p.is_file():reasons.append("MISSING_DEV80_DATA:"+str(p))
    # The old nine-horizon evaluation is incompatible with this new design.
    # Certification must prove causal, supported evaluation for ALL 64 horizons.
    cert=BASE/"thirteen_window_evaluator_certification.json"
    if not cert.is_file():reasons.append("MISSING_64_HORIZON_EVALUATOR_CERTIFICATION")
    else:
        d=json.loads(cert.read_text())
        if d.get("evaluated_horizons")!=list(REQUIRED_HORIZONS):reasons.append("INCOMPLETE_HORIZON_COVERAGE")
        for k in ("causal_pit_verified","dev80_only_verified","confidence_calibrated",
                  "multiple_testing_adjusted","risk_policy_verified","restart_recovery_verified",
                  "economic_review_verified","launch_dry_run_passed"):
            if d.get(k) is not True:reasons.append("UNCERTIFIED:"+k)
    result={"status":"READY" if not reasons else "BLOCKED","reasons":reasons,
            "windows":[list(x) for x in WINDOWS],"required_horizons":list(REQUIRED_HORIZONS),
            "source_manifest_sha256":report["source_manifest_sha256"],
            "dev80_only":True,"protected_heldouts_accessed":False}
    (BASE/"launch_readiness.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
if __name__=="__main__":
    r=check();print(json.dumps(r,indent=2));sys.exit(0 if r["status"]=="READY" else 2)
