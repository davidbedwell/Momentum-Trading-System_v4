"""Independent, fail-closed certification of frozen catastrophic-risk evidence.

A replay is not certification. Certification requires a second independently
produced path replay, verified provenance, pre-search freeze and causal costs.
"""
import hashlib,json
from datetime import datetime
from pathlib import Path

def _sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()

def certify(policy,replay,independent,*,source_root):
    failures=[]
    source=Path(source_root)/policy.get("provenance",{}).get("source","")
    if not source.is_file() or _sha256(source)!=policy.get("provenance",{}).get("source_sha256"):
        failures.append("frozen source provenance invalid")
    try:
        frozen=datetime.fromisoformat(policy["frozen_at"].replace("Z","+00:00"))
        started=datetime.fromisoformat(policy["search_started_at"].replace("Z","+00:00"))
        if frozen>=started:failures.append("policy not frozen before search")
    except (KeyError,TypeError,ValueError,AttributeError):
        failures.append("pre-search freeze timestamp absent or invalid")
    if replay.get("policy_hash")!=policy.get("policy_hash"):
        failures.append("policy hash mismatch")
    thresholds=policy.get("thresholds",{})
    required={f"{side}:{kind}:{float(x):g}" for side in ("LONG","SHORT")
              for kind,key in (("fraction","loss_fraction_sensitivity"),("atr20","atr20_sensitivity"))
              for x in thresholds.get(key,[])}
    if len(required)!=16 or not required.issubset(replay.get("results",{})):
        failures.append("16 frozen side-by-threshold replay scenarios incomplete")
    for key in required.intersection(replay.get("results",{})):
        r=replay["results"][key]
        if r.get("eligible",0)<=0 or r.get("breached",0)!=r.get("gap_fills",0)+r.get("intraday_fills",0):
            failures.append(key+": inconsistent stop replay counts")
    if not replay.get("causal_costs_verified"):
        failures.append("causal transaction costs on executable fills not verified")
    if not replay.get("candidate_level_replay_verified"):
        failures.append("selected candidate-level risk replay missing")
    if not independent or independent.get("independently_verified") is not True:
        failures.append("independent recalculation not verified")
    else:
        if independent.get("policy_hash")!=policy.get("policy_hash"):
            failures.append("independent policy hash mismatch")
        if independent.get("raw_sha256")!=replay.get("raw_sha256"):
            failures.append("independent source data mismatch")
        if independent.get("results")!=replay.get("results"):
            failures.append("independent replay does not reproduce scenario results")
    return {"decision":"PASS" if not failures else "FAIL","failures":failures,
            "policy_hash":policy.get("policy_hash"),"scenario_count":len(required)}
