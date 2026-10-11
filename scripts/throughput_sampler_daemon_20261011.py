#!/usr/bin/env python3
"""Persist read-only samples every 60s while four-window controller runs."""
import time,subprocess,sys,pathlib,datetime,json
from scripts.stage2_window_conveyor_20261011 import ROOT,BASE
log=BASE/'throughput_sampler_daemon.jsonl'
for n in range(120):
 p=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/throughput_compare_20261011.py')],cwd=ROOT,env={'PYTHONPATH':str(ROOT),'PATH':'/usr/bin:/bin'},capture_output=True,text=True,timeout=120)
 with log.open('a') as f:
  f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'iteration':n,'returncode':p.returncode,'stderr':p.stderr[-500:]})+'\n')
 if p.returncode:break
 time.sleep(60)
