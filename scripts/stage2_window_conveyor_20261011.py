#!/usr/bin/env python3
"""Sequential Stage 2 window conveyor. Fail closed; never alter running first window."""
import json, os, pathlib, subprocess, sys, time, traceback
ROOT=pathlib.Path('/home/ubuntu/Momentum-Trading-System_v4')
BASE=ROOT/'Research/Runs/thirteen-window-normal-20261011'
AUTH=BASE/'server_authorization.json'
WINDOWS=((2,5),(6,10),(11,15),(16,20),(21,25),(26,30),(31,35),(36,40),(41,45),(46,50),(51,55),(56,60),(61,65))
STATUS=BASE/'conveyor_status.json'
def emit(**fields):
    obj={'updated_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),**fields}
    temp=STATUS.with_suffix('.tmp')
    temp.write_text(json.dumps(obj,indent=2)+'\n')
    os.replace(temp,STATUS)
    print(json.dumps(obj),flush=True)
def state(path):
    p=path/'state.json'
    if not p.exists():return {}
    return json.loads(p.read_text())
def alive(pid):
    try:
        stat=pathlib.Path(f'/proc/{pid}/stat').read_text().split()[2]
        return stat not in ('Z','X')
    except (FileNotFoundError,ProcessLookupError):return False
def main():
    if not AUTH.is_file():raise RuntimeError('MISSING_AUTHORIZATION')
    from scripts.thirteen_window_launch_guard_20261011 import require_launch_authorization
    require_launch_authorization(authorization_path=AUTH)
    for index,(lo,hi) in enumerate(WINDOWS):
        dest=BASE if index==0 else BASE/f'window_{lo:02d}_{hi:02d}'
        dest.mkdir(parents=True,exist_ok=True)
        s=state(dest)
        if s.get('completed'):
            emit(status='WINDOW_COMPLETE',window=[lo,hi],generation=s.get('generation'),reason=s.get('stop_reason'))
            continue
        if index==0 and alive(4402):
            emit(status='WAITING_FOR_EXISTING_FIRST_WINDOW',window=[lo,hi],pid=4402)
            while alive(4402):
                time.sleep(30)
            s=state(dest)
            if s.get('completed'):
                emit(status='WINDOW_COMPLETE',window=[lo,hi],generation=s.get('generation'),reason=s.get('stop_reason'))
                continue
            emit(status='RESUMING_FIRST_WINDOW',window=[lo,hi],generation=s.get('generation'))
        log=dest/'runner.log'
        cmd=[str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/run_thirteen_window_normal_20261011.py'),'--window',str(lo),str(hi),'--workers','28','--authorization-file',str(AUTH),'--output',str(dest)]
        emit(status='STARTING_WINDOW',window=[lo,hi],command=cmd)
        with log.open('a') as f:
            proc=subprocess.Popen(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT)},stdout=f,stderr=subprocess.STDOUT)
            emit(status='RUNNING_WINDOW',window=[lo,hi],pid=proc.pid)
            code=proc.wait()
        s=state(dest)
        if code!=0 or not s.get('completed'):
            raise RuntimeError(f'WINDOW_FAILED {lo}-{hi}: exit={code}, generation={s.get("generation")}, log={log}')
        emit(status='WINDOW_COMPLETE',window=[lo,hi],generation=s.get('generation'),reason=s.get('stop_reason'))
    emit(status='ALL_13_WINDOWS_COMPLETE')
if __name__=='__main__':
    try:main()
    except Exception as exc:
        emit(status='STOPPED_ERROR',error=str(exc),traceback=traceback.format_exc())
        sys.exit(1)
