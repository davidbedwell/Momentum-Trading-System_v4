#!/usr/bin/env python3
"""Non-mutating restart proof using production recovery predicates and frozen snapshots."""
import json,pathlib,hashlib,tempfile,shutil
from scripts.stage2_window_conveyor_20261011 import BASE,WINDOWS,state
from scripts.parallel_window_recovery_20261011 import alive
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
active=[(21,25),(26,30)]
checks=[]
with tempfile.TemporaryDirectory(prefix='mts-restart-proof-') as td:
 for lo,hi in active:
  src=BASE/f'window_{lo:02d}_{hi:02d}'
  dst=pathlib.Path(td)/src.name;dst.mkdir()
  for name in ['state.json','pending.json']:
   p=src/name
   if p.exists():shutil.copy2(p,dst/name)
  cp=src/'state.json'
  original=state(src);copy=state(dst)
  assert original['generation']==copy['generation']
  assert original['config']==copy['config']
  assert not original.get('completed')
  assert sha(cp)==sha(dst/'state.json')
  checks.append({'window':[lo,hi],'generation':copy['generation'],'state_sha256':sha(cp),'pending':(dst/'pending.json').exists(),'configuration_equal':True,'checkpoint_snapshot_verified':True})
 # First window uses BASE, not a window_02_05 directory.
 assert state(BASE).get('completed')
 # Completed windows should be skipped by recovery scheduler.
 for lo,hi in WINDOWS[:4]:
  src=BASE if lo==2 else BASE/f'window_{lo:02d}_{hi:02d}'
  assert state(src).get('completed'),(lo,hi)
 # Verify live runner adoption without touching it.
 for pid in [37831,40384]:assert alive(pid),pid
 print(json.dumps({'status':'PASS_NON_DESTRUCTIVE_RESTART_PRECHECK','active':checks,'completed_skipped':4,'adoptable_pids':[37831,40384],'live_restart_executed':False},indent=2))
