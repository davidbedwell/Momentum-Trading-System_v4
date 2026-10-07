#!/usr/bin/env python3
"""Machine-only V3 -> G3 transition controller. No assistant judgment authorizes launch."""
from __future__ import annotations
import json, hashlib, subprocess, sys, time, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'Research/G3'
V3=R/'MTS_G3_V3_PREREGISTERED_GATE_20261007.json';V3C=R/'MTS_G3_V3_CONFORMING_GATE_20261007.json';V4=R/'MTS_G3_V4_PREREGISTERED_GATE_20261007.json';V4FREEZE=R/'MTS_G3_V4_EXECUTION_FREEZE_20261007.sha256';FREEZE=R/'MTS_G3_PRODUCTION_EXECUTION_FREEZE_20261007.sha256';LEDGER=R/'MTS_G3_PRODUCTION_CONTROLLER_20261007.json';PREP=R/'MTS_G3_PRODUCTION_DATA_PREP.stdout'
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

def verify_hash_manifest(path):
    lines=[x.strip() for x in path.read_text().splitlines() if x.strip()]
    if not lines: raise RuntimeError('EMPTY_HASH_MANIFEST')
    for line in lines:
        h,name=line.split(None,1); q=ROOT/name.strip()
        if not q.exists() or sha(q)!=h: raise RuntimeError('EXECUTION_FREEZE_HASH_MISMATCH:'+name)

def verify_freeze(): verify_hash_manifest(FREEZE)
def child_env():
    e=os.environ.copy();e['PYTHONPATH']=str(ROOT)+(os.pathsep+e['PYTHONPATH'] if e.get('PYTHONPATH') else '');return e
def call_child(args):return subprocess.call(args,cwd=ROOT,env=child_env())
def main():
    if not V3.exists():return write('WAIT_V3')
    try:g=validate_v3()
    except Exception as e:return write('STOP_FAIL_CLOSED',reason=str(e))
    # Diagnostic V3 is provenance only. It can neither authorize nor veto production.
    if not V3C.exists():
        write('RUNNING_V3_CONFORMING_GATE',diagnostic_v3=g['state'])
        rc=call_child([sys.executable,'scripts/run_g3_v3_conforming_gate_20261007.py','--workers','60'])
        if rc:return write('STOP_V3_CONFORMING_EXECUTION_FAILED',returncode=rc)
    c=json.loads(V3C.read_text());cg=c.get('gate_decision');cstate=cg.get('state') if isinstance(cg,dict) else None
    if c.get('format')!='MTS_G3_V3_CONFORMING_GATE' or c.get('complete') is not True or c.get('replicates')!=25:return write('STOP_BAD_V3_CONFORMING_ARTIFACT')
    # V3C failure is immutable provenance. V4 is the sole prospective repaired formal gate.
    if not V4FREEZE.exists():return write('WAIT_V4_EXECUTION_FREEZE',v3c=cstate)
    try:verify_hash_manifest(V4FREEZE)
    except Exception as e:return write('STOP_V4_EXECUTION_FREEZE_INVALID',reason=str(e))
    if not V4.exists():
        write('RUNNING_V4_PREREGISTERED_GATE',v3c=cstate)
        rc=call_child([sys.executable,'scripts/run_g3_v4_preregistered_gate_20261007.py','--workers','60'])
        if rc:return write('STOP_V4_EXECUTION_FAILED',returncode=rc)
    v4=json.loads(V4.read_text());vg=v4.get('gate_decision');vstate=vg.get('state') if isinstance(vg,dict) else None
    if v4.get('format')!='MTS_G3_V4_PREREGISTERED_GATE' or v4.get('complete') is not True or v4.get('replicates')!=25:return write('STOP_BAD_V4_ARTIFACT')
    if vstate not in PASS:return write('STOP_V4_FAILED',v3c=cstate,v4=vg)
    if not FREEZE.exists():return write('WAIT_PRODUCTION_FREEZE',v4=vstate)
    try:verify_freeze()
    except Exception as e:return write('STOP_EXECUTION_FREEZE_INVALID',reason=str(e))
    if not PREP.exists() or 'PREP_COMPLETE' not in PREP.read_text():return write('WAIT_DATA_PREP',v4=vstate)
    reach=R/'MTS_G3_PRODUCTION_REACHABILITY_20261007.json'
    if not reach.exists():
        write('RUNNING_SEARCH_REACHABILITY');rc=call_child([sys.executable,'scripts/run_g3_production_reachability_20261007.py'])
        if rc:return write('STOP_SEARCH_REACHABILITY_EXECUTION_FAILED',returncode=rc)
    rr=json.loads(reach.read_text())
    if rr.get('decision')!='PASS_SEARCH_REACHABILITY':return write('STOP_SEARCH_REACHABILITY_FAILED',descriptor_occupancy=rr.get('descriptor_occupancy'))
    b=R/'MTS_G3_PRODUCTION_BENCHMARK_REAL_20261007.json'
    if not b.exists():
        write('RUNNING_EXACT_BENCHMARK',v4=vstate);rc=call_child([sys.executable,'scripts/run_g3_production_discovery_20261007.py','--arm','REAL','--benchmark-only','--workers','60'])
        if rc:return write('STOP_BENCHMARK_FAILED',returncode=rc)
    bo=json.loads(b.read_text())
    if bo.get('complete') is not True or bo.get('benchmark_only') is not True:return write('STOP_BAD_BENCHMARK')
    projected_storage=int(bo.get('projected_checkpoint_storage_bytes',10**18))
    if projected_storage>500*1024**3:return write('STOP_CHECKPOINT_STORAGE_INFEASIBLE',projected_checkpoint_storage_bytes=projected_storage)
    util=float(bo.get('aggregate_cpu_utilization',0));sec=float(bo['seconds']);eta=sec*200*2
    if util<.80:return write('STOP_PARALLEL_UTILIZATION_FAILED',aggregate_cpu_utilization=util,benchmark_seconds=sec)
    if eta>14*86400:return write('STOP_COMPUTE_INFEASIBLE',projected_seconds=eta)
    write('G3_REAL_AUTHORIZED',v4=vstate,benchmark_seconds=sec,projected_seconds_real_plus_null=eta,aggregate_cpu_utilization=util)
    real=R/'MTS_G3_PRODUCTION_DISCOVERY_REAL_20261007.json';null=R/'MTS_G3_PRODUCTION_DISCOVERY_NULL_20261007.json'
    if not real.exists():
        rc=call_child([sys.executable,'scripts/run_g3_production_discovery_20261007.py','--arm','REAL','--workers','60'])
        if rc:return write('STOP_G3_REAL_EXECUTION_FAILED',returncode=rc)
    if not null.exists():
        write('G3_MATCHED_NULL_AUTHORIZED');rc=call_child([sys.executable,'scripts/run_g3_production_discovery_20261007.py','--arm','NULL','--workers','60'])
        if rc:return write('STOP_G3_NULL_EXECUTION_FAILED',returncode=rc)
    ro=json.loads(real.read_text());no=json.loads(null.read_text());threshold=float(no.get('null_max_stat',float('inf')))
    survivors={k:v for k,v in ro.get('promoted',{}).items() if float(v['axes'][0])>threshold}
    final={'format':'MTS_G3_PRODUCTION_FINAL_CALIBRATION_V1','complete':True,'real_promoted_before_null':len(ro.get('promoted',{})),'matched_null_max_stat':threshold,'final_candidate_count':len(survivors),'final_candidates':survivors,'decision':'G3_FINALISTS_READY_FOR_ANALYSIS' if survivors else 'STOP_G3_NO_NULL_CALIBRATED_FINALISTS'}
    (R/'MTS_G3_PRODUCTION_FINAL_CALIBRATION_20261007.json').write_text(json.dumps(final,indent=2)+'\n')
    return write(final['decision'],final_candidate_count=len(survivors),matched_null_max_stat=threshold)
if __name__=='__main__':main()
