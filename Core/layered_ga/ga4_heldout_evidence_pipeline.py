"""GA4 heldout integration: external, frozen, independently audited input only.

This module does not unlock or read protected Verification A/B, DEV50 or BLIND17.
The supplied heldout must be distinct from every row used for training/selection.
No heldout is treated as independent merely because its filename says so.
"""
import hashlib,json
from pathlib import Path
import numpy as np
from .ga4_selection_adjusted_validation import validate

REQUIRED=("selection_digest","selection_frozen_at","heldout_opened_at",
          "attempted_hypotheses","training_security_ids","heldout_security_ids",
          "candidate_masks","baseline_mask","net_returns","cluster_ids",
          "provenance","independent_membership_audit")

def _hash(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def run_evidence(evidence):
    missing=[k for k in REQUIRED if k not in evidence]
    if missing:raise ValueError("missing required evidence: "+",".join(missing))
    if evidence["selection_frozen_at"]>=evidence["heldout_opened_at"]:
        raise ValueError("heldout opened before selection freeze")
    training=set(evidence["training_security_ids"])
    heldout=set(evidence["heldout_security_ids"])
    if not training or not heldout or training&heldout:
        raise ValueError("training/heldout overlap or empty bank")
    if evidence["independent_membership_audit"] is not True:
        raise ValueError("independent membership audit required")
    provenance=evidence["provenance"]
    if not isinstance(provenance,dict) or not provenance.get("source_sha256") or not provenance.get("selection_ledger_sha256"):
        raise ValueError("source and preselection ledger hashes required")
    n=len(evidence["net_returns"])
    if n==0 or len(evidence["cluster_ids"])!=n or len(evidence["baseline_mask"])!=n:
        raise ValueError("heldout row alignment")
    for name,mask in evidence["candidate_masks"].items():
        if len(mask)!=n:raise ValueError("candidate row alignment: "+name)
    result=validate(evidence["candidate_masks"],evidence["baseline_mask"],
                    evidence["net_returns"],evidence["cluster_ids"],
                    attempts=evidence["attempted_hypotheses"],
                    digest=evidence["selection_digest"])
    result["input_digest"]=_hash(evidence)
    result["membership_disjoint_verified"]=True
    result["source_provenance"]=provenance
    result["independently_verified"]=False
    result["certification"]="PENDING_INDEPENDENT_EXTERNAL_AUDIT"
    return result

def run_file(input_path,output_path):
    evidence=json.loads(Path(input_path).read_text())
    result=run_evidence(evidence)
    Path(output_path).write_text(json.dumps(result,indent=2,allow_nan=False))
    return result
