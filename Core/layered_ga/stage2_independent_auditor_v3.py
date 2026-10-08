"""Independent fail-closed V3 scientific certification audit.

Observational target curves are not GA recovery evidence. A PASS is impossible
until a versioned, independently audited multiobjective evolutionary ledger
and frozen catastrophic safeguards are supplied.
"""
import json
from pathlib import Path
from Core.layered_ga.stage2_calibration_gate_v3 import SHAPES,EFFECTS

def audit(observed, evolutionary=None, safeguards=None):
    cases=observed.get("cases",[])
    failures=[]
    expected={(f,s,e) for f in {c.get("family") for c in cases} for s in SHAPES for e in EFFECTS}
    identities=[(c.get("family"),c.get("shape"),c.get("effect")) for c in cases]
    if len(cases)!=45 or len(set(identities))!=45 or set(identities)!=expected:
        failures.append("45 unique cases and complete effect ladders not established")
    for c in cases:
        ident=f"{c.get('family')}/{c.get('shape')}/{c.get('effect')}"
        if not c.get("target_baseline_evaluated"):failures.append(ident+": missing target baseline")
        if not c.get("full_63_day_curve"):failures.append(ident+": incomplete horizon path")
        if not c.get("long_short_evaluated_separately"):failures.append(ident+": missing separate sides")
        sides=c.get("sides",{})
        for side in ("LONG","SHORT"):
            data=sides.get(side,{})
            if len(data.get("points",[]))!=63:failures.append(ident+"/"+side+": incomplete points")
            if len(data.get("paired_delta",[]))!=63:failures.append(ident+"/"+side+": incomplete paired null")
            if c.get("effect")==0 and any(abs(float(p.get("delta_ev_net",0)))>1e-10 for p in data.get("paired_delta",[])):
                failures.append(ident+"/"+side+": null response not zero")
        if c.get("effect")==.02:
            if not any(sides.get(side,{}).get("region",{}).get("observed_positive_lcb95") and
                       sides.get(side,{}).get("region",{}).get("observed_stable_plateau_overlap")
                       for side in ("LONG","SHORT")):
                failures.append(ident+": strong planted signal lacks positive LCB and stable target overlap")
    if not evolutionary or evolutionary.get("method")!="NSGA_II_TWO_OBJECTIVE_V3" or evolutionary.get("independent_selection_audit") is not True:
        failures.append("independently audited true multiobjective evolutionary selection missing")
    if not evolutionary or evolutionary.get("selection_adjusted_statistical_validation") is not True:
        failures.append("selection-adjusted independent statistical validation missing")
    if not safeguards or safeguards.get("frozen_before_search") is not True or safeguards.get("independently_verified") is not True:
        failures.append("independently verified ex-ante catastrophic-risk safeguards missing")
    return {"decision":"PASS" if not failures else "FAIL","certification_scope":"V3 scientific calibration",
            "cases":len(cases),"failure_count":len(failures),"failed_criteria":failures}

if __name__=="__main__":
    root=Path(__file__).resolve().parents[2]
    cal=root/"Research/Runs/layered/stage2-opportunity-v3-20261007/calibration"
    observed=json.loads((cal/"observed_evidence.json").read_text())
    def optional(name):
        p=cal/name
        return json.loads(p.read_text()) if p.is_file() else None
    result=audit(observed,optional("multiobjective_evolutionary_certification.json"),
                 optional("catastrophic_safeguards_certification.json"))
    (cal/"independent_scientific_audit.json").write_text(json.dumps(result,indent=2))
    print(json.dumps({"decision":result["decision"],"cases":result["cases"],
                      "failure_count":result["failure_count"],"failed_criteria":result["failed_criteria"][:20]},indent=2))
