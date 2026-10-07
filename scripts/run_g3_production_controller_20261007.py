#!/usr/bin/env python3
"""Machine-only V3 -> G3 transition controller. No assistant judgment authorizes launch."""
from __future__ import annotations
import json, hashlib, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'Research/G3'
V3=R/'MTS_G3_V3_PREREGISTERED_GATE_20261007.json';V3C=R/'MTS_G3_V3_CONFORMING_GATE_20261007.json';FREEZE=R/'MTS_G3_PRODUCTION_EXECUTION_FREEZE_20261007.sha256';LEDGER=R/'MTS_G3_PRODUCTION_CONTROLLER_20261007.json';PREP=R/'MTS_G3_PRODUCTION_DATA_PREP.stdout'
PASS={'PASS_2_OF_3','STRONG_PASS_3_OF_3'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(state,**kw):
    o={'controller':'MTS_G3_PRODUCTION_CONTROLLER_V1','state':state,'time':time.time(),**kw};LEDGER.write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o),flush=True);return o
def validate_v3():
    o=json.loads(V3.read_text())
    if o.get('format')!='MTS_G3_V3_PREREGISTERED_GATE' or o.get('complete') is not True or o.get('replicates')!=25:raise RuntimeError('STOP_BAD_V3_ARTIFACT')
    g=o.get('gate_decision');
    if not isinstance(g,dict) or g.get('state') not in PASS|{'FAIL_NO_LARGE_DISCOVERY'}:raise RuntimeError('STOP_BAD_V3_DECISION')
    return g

def main():
    if not V3.exists():return write('WAIT_V3')
    try:g=validate_v3()
    except Exception as e:return write('STOP_FAIL_CLOSED',reason=str(e))
    if g['state'] not in PASS:return write('STOP_V3_FAILED',v3=g)
    # First V3 executable omitted frozen temporal validation; preserve it as diagnostic only.
    if not V3C.exists():
        write('RUNNING_V3_CONFORMING_GATE',diagnostic_v3=g['state'])
        rc=subprocess.call([sys.executable,'scripts/run_g3_v3_conforming_gate_20261007.py','--workers','60'],cwd=ROOT)
        if rc:return write('STOP_V3_CONFORMING_EXECUTION_FAILED',returncode=rc)
    c=json.loads(V3C.read_text())
    if c.get('format')!='MTS_G3_V3_CONFORMING_GATE' or c.get('complete') is not True or c.get('replicates')!=25:return write('STOP_BAD_V3_CONFORMING_ARTIFACT')
    cg=c.get('gate_decision');cstate=cg.get('state') if isinstance(cg,dict) else None
    if cstate not in PASS:return write('STOP_V3_CONFORMING_FAILED',diagnostic_v3=g['state'],conforming_v3=cg)
    if not FREEZE.exists() or not FREEZE.read_text().strip():return write('WAIT_PRODUCTION_FREEZE',v3=cstate)
    if not PREP.exists() or 'PREP_COMPLETE' not in PREP.read_text():return write('WAIT_DATA_PREP',v3=cstate)
    # Exact one-generation benchmark uses production island/population architecture and must finish before launch.
    b=R/'MTS_G3_PRODUCTION_BENCHMARK_20261007.json'
    if not b.exists():
        write('RUNNING_EXACT_BENCHMARK',v3=cstate);rc=subprocess.call([sys.executable,'scripts/run_g3_production_discovery_20261007.py','--benchmark-only','--workers','60'],cwd=ROOT)
        if rc:return write('STOP_BENCHMARK_FAILED',returncode=rc)
    bo=json.loads(b.read_text())
    if bo.get('complete') is not True or bo.get('benchmark_only') is not True:return write('STOP_BAD_BENCHMARK')
    sec=float(bo['seconds']); eta=sec*200
    write('G3_LARGE_DISCOVERY_AUTHORIZED',v3=cstate,benchmark_seconds=sec,projected_seconds_no_plateau=eta,freeze_sha256=sha(FREEZE))
    rc=subprocess.call([sys.executable,'scripts/run_g3_production_discovery_20261007.py','--workers','60'],cwd=ROOT)
    if rc:return write('STOP_G3_EXECUTION_FAILED',returncode=rc)
    out=json.loads((R/'MTS_G3_PRODUCTION_DISCOVERY_RESULT_20261007.json').read_text())
    return write(out['decision'],promoted_count=out['promoted_count'],seconds=out['seconds'])
if __name__=='__main__':main()
