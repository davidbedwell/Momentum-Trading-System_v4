"""Compute Stage2 structural and paired-response statistical evidence from observed paths.

No field is set true without its corresponding observed measurement.
Selection-adjusted heldout GA evidence is separate and remains mandatory.
"""
import json
from pathlib import Path
from math import isfinite
from Core.layered_ga.stage2_paired_recovery_v3 import paired_recovery, WINDOWS
from Core.layered_ga.stage2_calibration_gate_v3 import certify_calibration

ROOT = Path(__file__).resolve().parents[2]
CAL = ROOT / "Research/Runs/layered/stage2-opportunity-v3-20261007/calibration"

def measure_case(case):
    sides = case.get("sides", {})
    paths = [sides.get(side, {}) for side in ("LONG", "SHORT")]
    complete = all(len(p.get("points", [])) == 63 and
                   {int(x["horizon"]) for x in p["points"]} == set(range(1, 64)) and
                   len(p.get("paired_delta", [])) == 63 for p in paths)
    responses = [paired_recovery(p, case["shape"], case["effect"]) for p in paths] if complete else []
    lo, hi = WINDOWS[case["shape"]]
    positive = any(any(isfinite(float(x.get("lcb95",float("nan")))) and
                           float(x["lcb95"]) > 0 and lo <= int(x["horizon"]) <= hi
                           for x in p.get("points", [])) for p in paths)
    return {
        "family":case["family"],"shape":case["shape"],"effect":case["effect"],
        "target_baseline_evaluated":case.get("target_baseline_evaluated") is True,
        "full_63_day_curve":complete,
        "long_short_evaluated_separately":complete and case.get("long_short_evaluated_separately") is True,
        "target_region_positive_lcb95":positive,
        "target_region_overlap":any(r.get("pass") is True for r in responses) if responses else False,
        "null_target_specific_recovery":False if case["effect"] == 0 and all(r.get("null_rejected") for r in responses) else None,
        "ga_preserves_or_improves":None,
        "independent_effective_n_verified":None,
        "causal_costs_verified":None,
        "paired_recovery":responses,
        "evidence_limits":["No independent effective-N recomputation","No cost provenance recheck",
                           "No selection-adjusted heldout GA comparison"]
    }

def main():
    observed=json.loads((CAL/"observed_evidence.json").read_text())
    measured=[measure_case(c) for c in observed["cases"]]
    result=certify_calibration(measured,frozen_parameters_verified=False)
    dest=CAL/"ga4_statistical_evidence_measured.json"
    dest.write_text(json.dumps({"cases":measured,"gate":result},indent=2,allow_nan=False))
    print(json.dumps({"cases":len(measured),"decision":result["decision"],
                      "failures":len(result["failed_criteria"]),"report":str(dest)}))
if __name__=="__main__":
    main()
