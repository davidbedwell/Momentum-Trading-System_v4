"""Audit DEV37 isolation before any heldout evaluation.

Never infer train/heldout membership from a DEV117 label. Requires an
authoritative frozen split manifest and verifies actual predictor membership.
Fails closed when membership is missing or cross-sectional features were
computed on the combined 117-security universe.
"""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/"Research/Runs/layered/stage2-opportunity-v3-20261007/cache"
CAL=CACHE.parent/"calibration"
FOLD_AUDIT=ROOT/"Research/Reports/MTS_FOLD_FEATURE_ISOLATION_AUDIT_20261006.json"
def run(manifest):
    train=set(manifest.get("DEV80",[]));held=set(manifest.get("DEV37",[]))
    failures=[]
    if len(train)!=80 or len(held)!=37 or train&held:
        failures.append("missing/invalid authoritative 80/37 membership")
    if not manifest.get("frozen_before_selection",False):
        failures.append("membership freeze predating selection not established")
    import pandas as pd
    frame=pd.read_parquet(CACHE/"dev117_predictors_v3.parquet",columns=["security_id"])
    used=set(frame.security_id.astype(str).unique())
    if held&used:
        failures.append("DEV37 securities present in existing selection evaluator input")
    if used!=train:
        failures.append("selection evaluator membership is not exactly DEV80")
    if FOLD_AUDIT.is_file():
        audit=json.loads(FOLD_AUDIT.read_text())
        for k,v in audit.items():
            if isinstance(v,dict) and v.get("fraction_changed",0)>0:
                failures.append("fold-specific feature recomputation required: "+k)
    return {"decision":"PASS" if not failures else "FAIL",
            "training_count":len(train),"heldout_count":len(held),
            "selection_input_count":len(used),
            "overlap_count":len(held&used),"failures":failures,
            "required_remediation":"Rebuild isolated DEV80 features and search; freeze winners; recompute isolated DEV37 features and evaluate once" if failures else "Proceed to predeclared DEV37 evaluation"}
if __name__=="__main__":
    m=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/"Research/Partitions/GA4_DEV80_DEV37_FROZEN_SPLIT.json"
    result=run(json.loads(m.read_text()) if m.is_file() else {})
    CAL.mkdir(parents=True,exist_ok=True)
    (CAL/"ga4_dev37_separation_audit.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
