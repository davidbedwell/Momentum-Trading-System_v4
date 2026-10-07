#!/usr/bin/env python3
"""Fail-closed G3 stage controller. MTS result artifacts, never assistant judgment, authorize transitions."""
from __future__ import annotations
import json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"Research/G3"
A=R/"MTS_G3_CLAUDE_PHASE_A_STOCK_LEVEL_V2_DIAGNOSTIC_20261007.json"
B=R/"MTS_G3_CLAUDE_PHASE_B_NA_VARIANCE_20261007.json"
C=R/"MTS_G3_CLAUDE_PHASE_C_PLANTED_HETEROGENEITY_20261007.json"
V3_FREEZE=R/"MTS_G3_V3_PROTOCOL_FREEZE.sha256"
LEDGER=R/"MTS_G3_AUTOMATED_STAGE_CONTROLLER_20261007.json"
REAL_PHASE_A={"NVDA":0.08679972398265211,"AAPL":0.06928131107790046,"XOM":0.06748516797062888}

def load(path):
    if not path.exists() or path.stat().st_size==0: raise RuntimeError(f"STOP_MISSING:{path.name}")
    return json.loads(path.read_text())

def required_n_80_one_sided(sd,effect):
    # Normal approximation, alpha=.05 one-sided, power=.80. Diagnostic branch only.
    if effect<=0: return math.inf
    return ((1.6448536269514722+0.8416212335729143)*sd/effect)**2

def decide():
    a=load(A)
    if a.get("format")!="MTS_G3_CLAUDE_PHASE_A_STOCK_LEVEL_V2_DIAGNOSTIC": raise RuntimeError("STOP_BAD_PHASE_A_FORMAT")
    n=int(a.get("count_above_0_003",-1))
    if n<=2: return {"state":"STOP_FEATURE_SET","reason":"PHASE_A_LE_2_OF_8"}
    if n<3: raise RuntimeError("STOP_AMBIGUOUS_PHASE_A")
    b=load(B); c=load(C)
    if b.get("format")!="MTS_G3_CLAUDE_PHASE_B_NA_VARIANCE" or b.get("replicates")!=50: raise RuntimeError("STOP_BAD_PHASE_B")
    if c.get("format")!="MTS_G3_CLAUDE_PHASE_C_PLANTED_HETEROGENEITY" or c.get("pass") is not True: return {"state":"STOP_SEARCH_ARCHITECTURE","reason":"PHASE_C_FAIL"}
    power={}
    for t in ("NVDA","AAPL","XOM"):
        sd=float(b["results"][t]["sd"]); effect=REAL_PHASE_A[t]-float(b["results"][t]["mean"])
        power[t]={"real":REAL_PHASE_A[t],"null_mean":float(b["results"][t]["mean"]),"effect":effect,"null_sd":sd,"n80_approx":required_n_80_one_sided(sd,effect)}
    worst=max(v["n80_approx"] for v in power.values())
    na_action="STATIONARY_BOOTSTRAP_EXPECTED_BLOCK_50" if worst>80 else ("INCREASE_NA_REPLICATES" if worst>=30 else "INVESTIGATE_SEARCH_INSTABILITY")
    state="V3_PROTOCOL_FREEZE_REQUIRED"
    if V3_FREEZE.exists() and V3_FREEZE.stat().st_size>0: state="V3_PLANTED_VALIDATION_AUTHORIZED"
    return {"state":state,"phase_a_count":n,"phase_c_pass":True,"na_action":na_action,"phase_b_power":power,"worst_n80_approx":worst,
            "invariants":["ALL_8_STOCKS_RETAINED","NO_TICKER_IDENTITY_GENE","NO_PROTECTED_DATA","NO_V3_INFERENCE_BEFORE_FREEZE","FAIL_CLOSED"]}

if __name__=="__main__":
    try: d=decide(); out={"controller":"MTS_G3_AUTOMATED_STAGE_CONTROLLER_V1","decision":d}
    except Exception as e: out={"controller":"MTS_G3_AUTOMATED_STAGE_CONTROLLER_V1","decision":{"state":"STOP_FAIL_CLOSED","reason":str(e)}}
    LEDGER.write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out,indent=2))
