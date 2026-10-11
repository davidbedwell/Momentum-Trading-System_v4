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
    # Independent Normal-only discovery uses the frozen GA4 retrospective
    # oracle crash exclusion. The live causal A/B/B1/C/R-1 tape is a separate
    # integrated-regime validation dependency, not a Normal GA launch gate.
    from Core.layered_ga.ga4_oracle_crash_mask import admissible_decisions
    from scripts.thirteen_window_crash_mask_20261011 import HORIZONS as MASK_HORIZONS
    if tuple(MASK_HORIZONS)!=REQUIRED_HORIZONS:
        reasons.append('CRASH_MASK_HORIZON_MISMATCH')
    if not (ROOT/'Research/Protocols/MTS_REENTRY_THREE_HYPOTHESIS_TEST_FREEZE_20261004.json').is_file():
        reasons.append('MISSING_FROZEN_GA4_CRASH_EPISODES')
    # Stage 2 is an exploratory library generator. Do not require later-stage
    # crash-deployment, portfolio-risk or trading-economics certification.
    cert=BASE/'stage2_horizon_readiness_20261011.json'
    if not cert.is_file():reasons.append('MISSING_STAGE2_READINESS_EVIDENCE')
    else:
        d=json.loads(cert.read_text())
        for k,v in d.get('checks',{}).items():
            if k!='new_server_authorized' and v.get('passed') is not True:
                reasons.append('STAGE2_UNVERIFIED:'+k)
        if d.get('stage')!=2 or d.get('purpose')!='EXPLORATORY_STRATEGY_LIBRARY_GENERATION':
            reasons.append('STAGE2_SCOPE_MISMATCH')
    # Recovered, immutable source lineage is essential. Never infer it from
    # a present-day similarly named feature factory.
    from Core.layered_ga.stage2_recovered_source_preflight_v3 import verify_recovered_sources
    try:
        frozen=verify_recovered_sources()
        if frozen['decision']!='PASS':reasons.append('FROZEN_SOURCE_HASH_MISMATCH_OR_MISSING')
    except (OSError,KeyError,ValueError) as exc:
        reasons.append('FROZEN_SOURCE_PROVENANCE_UNAVAILABLE:'+type(exc).__name__)
    result={"status":"READY" if not reasons else "BLOCKED","reasons":reasons,
            "windows":[list(x) for x in WINDOWS],"required_horizons":list(REQUIRED_HORIZONS),
            "source_manifest_sha256":report["source_manifest_sha256"],
            "dev80_only":True,"protected_heldouts_accessed":False}
    (BASE/"launch_readiness.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
if __name__=="__main__":
    r=check();print(json.dumps(r,indent=2));sys.exit(0 if r["status"]=="READY" else 2)
