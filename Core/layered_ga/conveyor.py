from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, hashlib, subprocess, sys, time
from .architecture import Stage

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'Research/Runs/layered'
STATE=RUN/'conveyor_state.json'
STAGE_DIRS={
 0:'stage0-ga0-archaeology-20261007',1:'stage1-context-map-20261007',
 2:'stage2-opportunity-20261007',3:'stage3-context-ablation-20261007',
 4:'stage4-entry-mae-20261007',5:'stage5-thesis-failure-20261007',
 6:'stage6-lifecycle-20261007',7:'stage7-capital-competition-20261007',
 8:'stage8-position-sizing-20261007',9:'stage9-portfolio-catastrophe-20261007',
 10:'stage10-report-card-20261007'}
RUNNERS={i:ROOT/'scripts'/f'run_stage{i}_20261007.py' for i in range(2,11)}
def readj(p): return json.loads(Path(p).read_text())
def gate(i): return readj(RUN/STAGE_DIRS[i]/'gate.json')
def passed(i): return (RUN/STAGE_DIRS[i]/'gate.json').exists() and gate(i).get('decision')=='PASS'
def write_state(stage,status,detail=''):
    x={'stage':stage,'stage_name':STAGE_DIRS.get(stage),'status':status,'detail':detail,'time':time.time()}
    STATE.write_text(json.dumps(x,indent=2)); print('CONVEYOR',json.dumps(x),flush=True)
def main():
    # Never substitute legacy Stage 2 for the frozen V3 calibration.
    v3=RUN/'stage2-opportunity-v3-20261007'/'calibration'
    evidence=v3/'gate.json'
    if not evidence.is_file() or readj(evidence).get('decision')!='PASS':
        status=readj(v3/'status.json').get('state','MISSING') if (v3/'status.json').is_file() else 'MISSING'
        write_state(2,'STOPPED_ENGINEERING',f'V3 calibration not certified ({status}); legacy fallback prohibited')
        return 20
    if not passed(0) or not passed(1): raise SystemExit('Stage0+1 must be PASS')
    for i in range(2,11):
        if passed(i):
            write_state(i,'ALREADY_PASS'); continue
        r=RUNNERS[i]
        if not r.exists():
            write_state(i,'STOPPED_ENGINEERING',f'missing runner {r}')
            return 20
        write_state(i,'RUNNING')
        cp=subprocess.run([sys.executable,str(r)],cwd=ROOT)
        if cp.returncode:
            write_state(i,'STOPPED_ENGINEERING',f'runner rc={cp.returncode}'); return cp.returncode
        g=gate(i)
        if g.get('decision')!='PASS':
            stop={'FAIL':'STOPPED_SCIENTIFIC','AMBIGUOUS':'STOPPED_REVIEW','ERROR':'STOPPED_ENGINEERING'}.get(g.get('decision'),'STOPPED_ENGINEERING')
            write_state(i,stop,g.get('reason','')); return 30
        write_state(i,'PASS')
    write_state(10,'COMPLETE','Stages 0-10 PASS')
    return 0
if __name__=='__main__': raise SystemExit(main())
