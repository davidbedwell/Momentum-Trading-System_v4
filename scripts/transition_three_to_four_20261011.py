#!/usr/bin/env python3
"""Controlled live transition 3x9 to 4x7. Fails closed on integrity errors."""
import os,signal,time,subprocess,pathlib,json
from scripts import checkpoint_transition_controller_20261011 as c
OLD=42401
def alive(pid):
 try:
  s=pathlib.Path(f'/proc/{pid}/stat').read_text()
  return s[s.rfind(')')+2:].split()[0] not in ('Z','X')
 except FileNotFoundError:return False
def main():
 assert alive(OLD),'OLD_CONTROLLER_NOT_RUNNING'
 assert c.memory()['available_gib']>=20
 active=[w for w in c.WINDOWS if c.pids_for(w)]
 assert 1<=len(active)<=3,active
 print('PRE',json.dumps({'active':active,'memory':c.memory()}),flush=True)
 os.kill(OLD,signal.SIGSTOP)
 print('OLD_PAUSED',flush=True)
 try:
  for w in active:c.stop_runner(w,timeout=60)
  for w in active:print('CHECKPOINT',w,c.integrity(w),flush=True)
  assert not any(c.pids_for(w) for w in c.WINDOWS)
  os.kill(OLD,signal.SIGKILL)
  for _ in range(30):
   if not alive(OLD):break
   time.sleep(.2)
  assert not alive(OLD),'OLD_CONTROLLER_NOT_STOPPED'
  cmd=[str(c.ROOT/'.venv/bin/python'),'-u',str(c.ROOT/'scripts/checkpoint_transition_controller_20261011.py'),'--run','--slots','4','--workers','7']
  with (c.BASE/'four_window_transition.log').open('a') as log:
   p=subprocess.Popen(cmd,cwd=c.ROOT,env={**os.environ,'PYTHONPATH':str(c.ROOT)},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  print('FOUR_WINDOW_CONTROLLER',p.pid,flush=True)
 except BaseException:
  if alive(OLD):os.kill(OLD,signal.SIGCONT)
  raise
if __name__=='__main__':main()
