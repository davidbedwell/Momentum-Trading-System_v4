"""Fail-closed, host-local Stage-2 handoff supervisor.

Runs independently of ChatGPT. Never manufactures a PASS or a launch command.
A valid gate, independent durability receipt, and pinned executable are required.
"""
from __future__ import annotations
import fcntl,hashlib,json,os,subprocess,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CAL=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/calibration'
OUT=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/handoff'
CONFIG=ROOT/'Research/Design/MTS_STAGE2_V3_AUTOMATIC_HANDOFF_CONFIG.json'
PASS_FIELDS=('target_visitation_verified','fast_medium_slow_recovery_verified','null_controls_verified','evolutionary_search_power_verified','scientific_parameters_unchanged')

def atomic(path:Path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2,sort_keys=True));os.replace(tmp,path)

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def inspect():
    if not CONFIG.is_file():return 'STOPPED_ENGINEERING', 'missing pinned launch config',None
    cfg=json.loads(CONFIG.read_text())
    s=json.loads((CAL/'status.json').read_text()) if (CAL/'status.json').is_file() else {}
    state=s.get('state','MISSING')
    if state in {'ERROR','FAIL','STOPPED_ENGINEERING_SEARCH_POWER_NOT_IMPLEMENTED','STOPPED_SCIENTIFIC_CALIBRATION_FAIL'}:
        return 'STOPPED_ENGINEERING',f'calibration terminal state: {state}',None
    if state not in {'SCIENTIFIC_PASS','PASS'}:
        return 'WAITING_FOR_CALIBRATION',f'calibration state: {state}',None
    gatefile=CAL/'gate.json'
    if not gatefile.is_file():return 'STOPPED_ENGINEERING','PASS state without signed-off gate file',None
    gate=json.loads(gatefile.read_text())
    if gate.get('decision')!='PASS' or any(gate.get(k) is not True for k in PASS_FIELDS):
        return 'STOPPED_ENGINEERING','gate lacks frozen scientific PASS evidence',None
    if gate.get('scientific_parameters_changed') is True or gate.get('failed_criteria'):
        return 'STOPPED_ENGINEERING','gate reports modified parameters or failed criteria',None
    if gate.get('stage')!='V3_MATCHED_EVOLUTIONARY_CALIBRATION':
        return 'STOPPED_ENGINEERING','gate stage does not identify full evolutionary calibration',None
    receipt=CAL/'durability_receipt.json'
    if not receipt.is_file():return 'WAITING_FOR_DURABILITY','calibration durability receipt missing',None
    dr=json.loads(receipt.read_text())
    for k in ('git_remote_sha_verified','backup_manifest_verified','critical_checksums_verified'):
        if dr.get(k) is not True:return 'WAITING_FOR_DURABILITY',f'durability not verified: {k}',None
    executable=ROOT/cfg['stage2_script'];expected=cfg['stage2_script_sha256']
    if not executable.is_file() or sha(executable)!=expected:
        return 'STOPPED_ENGINEERING','pinned Stage-2 executable absent or hash mismatch',None
    if not cfg.get('approved_launch') or not cfg.get('dev117_only') or cfg.get('protected_bank_access'):
        return 'STOPPED_ENGINEERING','launch authorization/governance config invalid',None
    if cfg.get('calibration_gate_sha256') != sha(gatefile):
        return 'STOPPED_ENGINEERING','gate checksum does not match pinned authorization',None
    return 'AUTHORIZED','all machine-checked requirements satisfied',cfg

def once():
    OUT.mkdir(parents=True,exist_ok=True)
    with open(OUT/'controller.lock','a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        status,reason,cfg=inspect()
        started=OUT/'stage2_launch_receipt.json'
        if started.exists():
            return {'state':'ALREADY_LAUNCHED','receipt':str(started),'updated':time.time()}
        if status!='AUTHORIZED':return {'state':status,'reason':reason,'updated':time.time()}
        command=[cfg['python_executable'],str(ROOT/cfg['stage2_script']),'--config',str(ROOT/cfg['stage2_config'])]
        log=open(OUT/'stage2.stdout.log','ab',buffering=0)
        err=open(OUT/'stage2.stderr.log','ab',buffering=0)
        p=subprocess.Popen(command,cwd=str(ROOT),stdin=subprocess.DEVNULL,stdout=log,stderr=err,start_new_session=True)
        receipt={'pid':p.pid,'command':command,'gate_sha256':sha(CAL/'gate.json'),'script_sha256':sha(ROOT/cfg['stage2_script']),'timestamp':time.time(),'launch_state':'LAUNCHED_NOT_PASSED'}
        atomic(started,receipt)
        return {'state':'STAGE2_LAUNCHED','pid':p.pid,'updated':time.time()}

def loop():
    while True:
        try:
            result=once()
            atomic(OUT/'supervisor_state.json',result)
            if result['state'] in {'STAGE2_LAUNCHED','ALREADY_LAUNCHED','STOPPED_ENGINEERING'}:break
        except Exception as exc:
            atomic(OUT/'supervisor_state.json',{'state':'STOPPED_ENGINEERING','reason':repr(exc),'updated':time.time()});break
        time.sleep(30)

if __name__=='__main__':loop()
