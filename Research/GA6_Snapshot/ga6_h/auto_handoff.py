#!/usr/bin/env python3
"""Wait for GA6-v3-with defense to finish; launch GA6-H only after real-evaluator preflight.
Never launches the synthetic diagnostic evaluator.
"""
import json,os,subprocess,time,datetime
from pathlib import Path
ROOT=Path('/opt/mts/ga6_h')
STATUS=ROOT/'audits'/'ga6h_auto_handoff_status.json'
GA6_PID=498968
GA6_RUN=Path('/opt/mts/ga6/runs/A_v2_full_evolution_20261022')
COMMAND_FILE=ROOT/'production_launch.json'
def write(**kwargs):
    STATUS.parent.mkdir(exist_ok=True,parents=True)
    STATUS.write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**kwargs},indent=2))
def alive(pid):
    try:
        s=Path(f'/proc/{pid}/stat').read_text().split()
        return s[2]!='Z'
    except FileNotFoundError:return False
def ga6_running():
    if alive(GA6_PID):return True
    try:
        data=subprocess.check_output(['pgrep','-af','structural_runner_A_v2'],text=True)
        return any('A_v2_full_evolution_20261022' in x and 'pgrep -af' not in x for x in data.splitlines())
    except subprocess.CalledProcessError:return False
def ready():
    if not COMMAND_FILE.exists():return None,'real historical evaluator and production launch configuration not yet installed'
    config=json.loads(COMMAND_FILE.read_text())
    if config.get('evaluator_kind')!='historical_net_ev_v1':return None,'refusing nonhistorical evaluator'
    cmd=config.get('command')
    if not isinstance(cmd,list) or not cmd or any(not isinstance(x,str) for x in cmd):
        return None,'invalid launch command'
    if 'diagnostic' in ' '.join(cmd).lower():return None,'refusing diagnostic runner'
    if config.get('preflight_passed') is not True:return None,'historical evaluator preflight not passed'
    return cmd,None
def main():
    while True:
        if ga6_running():
            write(state='waiting_for_ga6_v3_with_defense',ga6_pid=GA6_PID,ga6_run=str(GA6_RUN))
            time.sleep(30);continue
        cmd,error=ready()
        if error:
            write(state='ga6_finished_waiting_for_historical_evaluator',reason=error,ga6_run=str(GA6_RUN))
            time.sleep(30);continue
        log=(ROOT/'audits'/'ga6h_auto_launch.log').open('a')
        proc=subprocess.Popen(cmd,cwd='/opt/mts',stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        write(state='ga6h_launched',pid=proc.pid,command=cmd,ga6_run=str(GA6_RUN))
        return
if __name__=='__main__':main()
