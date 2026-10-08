"""Reproducible GA4 scientific audit from Git-tracked code and external evidence.

Does not open protected banks. Missing evidence is an explicit FAIL, not PASS.
Usage: python scripts/run_ga4_scientific_certification_20261008.py
"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from Core.layered_ga.ga4_heldout_evidence_pipeline import run_file
from Core.layered_ga.ga4_catastrophic_risk_certification import certify
CAL=ROOT/"Research/Runs/layered/stage2-opportunity-v3-20261007/calibration"
POLICY=ROOT/"Research/Design/MTS_STAGE2_V3_CATASTROPHIC_POLICY_FREEZE_20261007.json"

def read(path):
    return json.loads(path.read_text()) if path.is_file() else None

def main():
    CAL.mkdir(parents=True,exist_ok=True)
    input_file=CAL/"ga4_frozen_heldout_input.json"
    heldout=None
    failures=[]
    if input_file.is_file():
        try:
            heldout=run_file(input_file,CAL/"ga4_heldout_validation.json")
        except (ValueError,KeyError,TypeError) as exc:
            failures.append("heldout: "+str(exc))
    else:
        failures.append("no eligible frozen independent heldout input; protected banks untouched")
    policy=read(POLICY)
    replay=read(CAL/"ga4_observed_stop_replay.json")
    independent=read(CAL/"ga4_independent_risk_replay.json")
    if policy is None:failures.append("frozen risk policy missing")
    if replay is None:failures.append("observed OHLC risk replay missing")
    risk=certify(policy or {},replay or {},independent,source_root=ROOT)
    if risk["decision"]!="PASS":failures.extend("risk: "+x for x in risk["failures"])
    if not heldout or not heldout.get("independently_verified"):
        failures.append("selection-adjusted heldout result lacks external independent verification")
    result={"decision":"FAIL" if failures else "PASS","failures":failures,
            "heldout":heldout,"catastrophic_risk":risk,
            "protected_bank_policy":"Never read Verification A/B, DEV50, BLIND17 for this run"}
    dest=CAL/"ga4_scientific_certification.json"
    dest.write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps({"decision":result["decision"],"failure_count":len(failures),"report":str(dest)}))
    return result
if __name__=="__main__":main()
