#!/usr/bin/env python3
"""One-shot controlled handoff. Requires explicit --execute."""
import argparse,os,signal,time,subprocess,json,pathlib
from scripts import checkpoint_transition_controller_20261011 as c
LEGACY=37791
ACTIVE=((21,25),(26,30))
def alive(pid):
 try:
  s=pathlib.Path(f'/proc/{pid}/stat').read_text()
  return s[s.rfind(')')+2:].split()[0] not in ('Z','X')
 except FileNotFoundError:return False
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');a=ap.parse_args()
 print('BEFORE',json.dumps({'legacy':alive(LEGACY),'windows':[{'w':w,'pids':c.pids_for(w),'generation':c.state(c.dest(w)).get('generation')} for w in ACTIVE],'memory':c.memory()}),flush=True)
 if not a.execute:return
 assert alive(LEGACY)
 assert c.memory()['available_gib']>=20
 os.kill(LEGACY,signal.SIGSTOP);print('LEGACY_SUSPENDED',flush=True)
 try:
  for w in ACTIVE:c.stop_runner(w,timeout=60)
  for w in ACTIVE:print('POST_STOP',w,c.integrity(w),flush=True)
  assert all(not c.pids_for(w) for w in ACTIVE)
  os.kill(LEGACY,signal.SIGKILL)
  for _ in range(20):
   if not alive(LEGACY):break
   time.sleep(.25)
  assert not alive(LEGACY),'LEGACY_NOT_STOPPED'
  print('LEGACY_STOPPED',flush=True)
  cmd=[str(c.ROOT/'.venv/bin/python'),'-u',str(c.ROOT/'scripts/checkpoint_transition_controller_20261011.py'),'--run','--slots','3','--workers','9']
  with (c.BASE/'three_window_transition.log').open('a') as log:
   p=subprocess.Popen(cmd,cwd=c.ROOT,env={**os.environ,'PYTHONPATH':str(c.ROOT)},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  print('SUCCESSOR_LAUNCHED',p.pid,flush=True)
 except BaseException:
  if alive(LEGACY):os.kill(LEGACY,signal.SIGCONT)
  raise
if __name__=='__main__':main()
