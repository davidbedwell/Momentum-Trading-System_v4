"""GA4 Stage 2 evidence builders: preserve observations, never self-certify."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from Core.layered_ga.stage2_certification_evidence_v3 import audit_evolutionary_ledger, audit_catastrophic_policy

ROOT = Path(__file__).resolve().parents[2]
CAL = ROOT / "Research/Runs/layered/stage2-opportunity-v3-20261007/calibration"
POLICY = ROOT / "Research/Design/MTS_STAGE2_V3_CATASTROPHIC_POLICY_FREEZE_20261007.json"

def evolutionary_evidence(batch, heldout=None):
    """Normalize real per-case generations and audit them without invented validation."""
    cases = []
    for case in batch.get("cases", []):
        ledger = {"generations": case.get("generations", []),
                  "heldout_selection_adjusted_validation": heldout.get(case["family"], {}).get(case["shape"], {}).get(str(case["effect"])) if isinstance(heldout, dict) else None}
        cases.append({"identity": {k: case.get(k) for k in ("family", "shape", "effect", "side", "seed")},
                      "unique_evaluations": case.get("unique_evaluations"),
                      "ledger": ledger, "audit_failures": audit_evolutionary_ledger(ledger)})
    sides = {c["identity"]["side"] for c in cases}
    failures = []
    if len(cases) != 90 or sides != {"LONG", "SHORT"}:
        failures.append("45 calibration cases require separately evaluated LONG and SHORT evolutionary ledgers (90 total)")
    if any(c["audit_failures"] for c in cases):
        failures.append("per-case independent evolutionary evidence incomplete")
    return {"status": "ENGINEERING_EVIDENCE_ONLY", "cases": cases,
            "engineering_gaps": failures, "scientific_certification": "NOT_CERTIFIED"}

def catastrophic_evidence(policy, observed=None, search_start=None, independent=None):
    """Bind frozen source provenance and measured recalculation; reject unsupported chronology."""
    result = dict(policy)
    source = ROOT / policy["provenance"]["source"]
    digest = hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None
    result["source_hash_verified"] = digest == policy["provenance"]["source_sha256"]
    result["search_started_at"] = search_start
    result["independent_recalculation"] = independent
    result["observed_path_count"] = len(observed.get("cases", [])) if isinstance(observed, dict) else 0
    result["audit_failures"] = audit_catastrophic_policy(result)
    if not result["source_hash_verified"]:
        result["audit_failures"].append("frozen source hash mismatch")
    result["scientific_certification"] = "NOT_CERTIFIED"
    return result

def main():
    CAL.mkdir(parents=True, exist_ok=True)
    batch = json.loads((CAL / "nsga2_batch_evolutionary_evidence.json").read_text())
    policy = json.loads(POLICY.read_text())
    observed_path = CAL / "observed_evidence.json"
    observed = json.loads(observed_path.read_text()) if observed_path.exists() else None
    evo = evolutionary_evidence(batch)
    risk = catastrophic_evidence(policy, observed, search_start=datetime.fromtimestamp(batch["started_at"], timezone.utc).isoformat())
    for filename, artifact in (("ga4_evolutionary_evidence_engineering.json", evo),
                               ("ga4_catastrophic_evidence_engineering.json", risk)):
        (CAL / filename).write_text(json.dumps(artifact, indent=2, allow_nan=False))
    print(json.dumps({"evolutionary_cases": len(evo["cases"]), "evolutionary_gaps": evo["engineering_gaps"],
                      "risk_audit_failures": risk["audit_failures"], "source_hash_verified": risk["source_hash_verified"]}, indent=2))

if __name__ == "__main__":
    main()
