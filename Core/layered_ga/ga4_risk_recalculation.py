"""Independent path-level catastrophic risk sensitivity recalculation.

Uses cached observed adverse excursions and terminal outcomes, never a synthetic
2R cap. Terminal returns are NOT treated as actual stop fills; this is a
sensitivity bound and cannot certify executable stop performance.
"""
import hashlib
import json
import numpy as np
from pathlib import Path
from Core.layered_ga.stage2_data_v3 import load_path_cache

ROOT = Path(__file__).resolve().parents[2]
CAL = ROOT / "Research/Runs/layered/stage2-opportunity-v3-20261007/calibration"
POLICY = ROOT / "Research/Design/MTS_STAGE2_V3_CATASTROPHIC_POLICY_FREEZE_20261007.json"

def recalculate(paths, policy):
    lo = np.asarray(paths.low_excursion, dtype=float)
    hi = np.asarray(paths.high_excursion, dtype=float)
    endpoint = np.asarray(paths.endpoint_return, dtype=float)
    if lo.shape != hi.shape or lo.shape != endpoint.shape or endpoint.ndim != 2:
        raise ValueError("misaligned outcome and adverse excursion matrices")
    result = {}
    for side, adverse, returns in (("LONG", -lo, endpoint), ("SHORT", hi, -endpoint)):
        valid = np.isfinite(adverse) & np.isfinite(returns)
        if not valid.any():
            raise ValueError("no finite paths")
        a = adverse[valid]
        r = returns[valid]
        cuts = {}
        for threshold in policy["thresholds"]["loss_fraction_sensitivity"]:
            cuts[str(threshold)] = {"breach_count": int(np.count_nonzero(a >= threshold)),
                                    "breach_fraction": float(np.mean(a >= threshold)),
                                    "terminal_loss_fraction_given_breach": float(np.mean(r[a >= threshold] < 0)) if np.any(a >= threshold) else None}
        result[side] = {"valid_path_count": int(valid.sum()),
                        "uncapped_terminal_mean_return": float(np.mean(r)),
                        "uncapped_adverse_p95": float(np.quantile(a, .95)),
                        "loss_fraction_sensitivity": cuts}
    return result

def main():
    policy = json.loads(POLICY.read_text())
    source = ROOT / policy["provenance"]["source"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != policy["provenance"]["source_sha256"]:
        raise ValueError("frozen source hash mismatch")
    paths, _ = load_path_cache(CAL.parent / "cache")
    result = {"policy_hash": policy["policy_hash"],
              "source_sha256_verified": True,
              "recalculation": recalculate(paths, policy),
              "limitations": ["ATR20 thresholds not evaluated without aligned ATR20 series",
                              "gap-through executable fill prices not available in cached excursions",
                              "no independent stop-fill certification claimed"],
              "independently_verified": False,
              "status": "MEASURED_SENSITIVITY_PARTIAL"}
    dest = CAL / "ga4_risk_path_sensitivity.json"
    dest.write_text(json.dumps(result, indent=2, allow_nan=False))
    print(json.dumps({"status": result["status"], "valid_paths": {k:v["valid_path_count"] for k,v in result["recalculation"].items()}, "report":str(dest)}))
if __name__ == "__main__":
    main()
