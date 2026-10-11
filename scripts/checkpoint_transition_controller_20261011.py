#!/usr/bin/env python3
"""Checkpoint-safe successor conveyor. Independent of the running legacy controller.
Modes: --self-test, --preflight, --run. Never launch alongside legacy controller.
"""
import argparse,collections,datetime,fcntl,json,os,pathlib,signal,subprocess,sys,time
from scripts.stage2_window_conveyor_20261011 import ROOT,BASE,AUTH,WINDOWS,state
from scripts.thirteen_window_launch_guard_20261011 import require_launch_authorization
LOCK=BASE/'checkpoint_transition_controller.lock'
EVENT=BASE/'checkpoint_transition_events.jsonl'
def emit(event,**data):
 with EVENT.open('a') as f:
  f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event,**data})+'\n')
  f.flush();os.fsync(f.fileno())
def dest(w):return BASE if tuple(w)==tuple(WINDOWS[0]) else BASE/f'window_{w[0]:02d}_{w[1]:02d}'
def pids_for(w):
 out=[]
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode().split()
   if 'run_thirteen_window_normal_20261011.py' not in ' '.join(cmd) or '--window' not in cmd:continue
   i=cmd.index('--window')
   if tuple(map(int,cmd[i+1:i+3]))==tuple(w):out.append(int(p.name))
  except (OSError,ValueError,IndexError):continue
 return out
def integrity(w):
 d=dest(w);s=state(d)
 if not s:return {'status':'NOT_STARTED','generation':None}
 config=s.get('config',{})
 if config.get('window')!=list(w):raise RuntimeError(f'CONFIG_MISMATCH {w}')
 counts=collections.Counter();candidates=set();evaluated=set()
 for filename,kind in [('candidates.jsonl','c'),('evaluations.jsonl','e')]:
  p=d/filename
  if not p.exists():raise RuntimeError(f'MISSING_{filename} {w}')
  with p.open() as f:
   for line in f:
    r=json.loads(line);key=r['genome_hash']
    target=candidates if kind=='c' else evaluated
    if key in target:raise RuntimeError(f'DUPLICATE_{kind} {w}')
    target.add(key)
    if kind=='c':counts[r['generation']]+=1
 if evaluated-candidates:raise RuntimeError(f'ORPHAN_EVAL {w}')
 if counts and sorted(counts)!=list(range(max(counts)+1)):raise RuntimeError(f'GAP {w}')
 for g,n in counts.items():
  if n!=(config['initial_population_count'] if g==0 else config['batch']):raise RuntimeError(f'PARTIAL_GENERATION {w} {g}')
 generation=s['generation'];latest=max(counts) if counts else -1
 if latest>generation+1 or latest<generation:raise RuntimeError(f'JOURNAL_CHECKPOINT_MISMATCH {w}')
 if latest==generation+1:
  pending=d/'pending.json'
  if not pending.exists():raise RuntimeError(f'MISSING_PENDING {w}')
  if json.loads(pending.read_text())['generation']!=latest:raise RuntimeError(f'PENDING_MISMATCH {w}')
 if s.get('completed') and candidates!=evaluated:raise RuntimeError(f'COMPLETED_WITH_PENDING {w}')
 return {'status':'COMPLETED' if s.get('completed') else 'RESUMABLE','generation':generation,'pending_evaluations':len(candidates-evaluated)}
def memory():
 info={}
 for line in pathlib.Path('/proc/meminfo').read_text().splitlines():
  if line.startswith(('MemAvailable:','SwapTotal:','SwapFree:')):
   k,v,*_=line.split();info[k[:-1]]=int(v)/1048576
 return {'available_gib':info['MemAvailable'],'swap_used_gib':info['SwapTotal']-info['SwapFree']}
def preflight():
 require_launch_authorization(authorization_path=AUTH)
 checks=[{'window':list(w),**integrity(w),'pids':pids_for(w)} for w in WINDOWS]
 return {'checks':checks,'memory':memory()}
def stop_runner(w,timeout=45):
 # Only processes matching this exact window are signalled.
 found=pids_for(w)
 if not found:return
 emit('STOP_REQUESTED',window=list(w),pids=found)
 # Parent process is the one with a matching --window argument and direct controller PPID.
 # SIGTERM all matching workers to avoid orphaned pool children.
 for pid in found:
  try:os.kill(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 deadline=time.monotonic()+timeout
 while time.monotonic()<deadline and pids_for(w):time.sleep(.5)
 if pids_for(w):raise RuntimeError(f'STOP_TIMEOUT_MANUAL_INTERVENTION {w} {pids_for(w)}')
 emit('STOP_CONFIRMED',window=list(w),checkpoint=integrity(w))
def run(slots,workers):
 if (slots,workers) not in ((2,14),(3,9),(4,7)):raise RuntimeError('UNAPPROVED_ALLOCATION')
 lock=LOCK.open('a+')
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:raise RuntimeError('CONTROLLER_ALREADY_RUNNING')
 # Fail closed if any existing legacy controller remains.
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid():continue
  try:
   cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode()
   if 'parallel_window_recovery_20261011.py' in cmd or 'parallel_window_conveyor_20261011.py' in cmd:raise RuntimeError('LEGACY_CONTROLLER_RUNNING')
  except OSError:continue
 require_launch_authorization(authorization_path=AUTH)
 if any(pids_for(w) for w in WINDOWS):raise RuntimeError('ACTIVE_RUNNERS_PRESENT_REQUIRE_CONTROLLED_HANDOFF')
 pending=[w for w in WINDOWS if not state(dest(w)).get('completed')]
 emit('CONTROLLER_STARTED',slots=slots,workers=workers,remaining=len(pending))
 active={};paused=False
 try:
  while pending or active:
   mem=memory()
   if mem['available_gib']<16 or mem['swap_used_gib']>4:raise RuntimeError(f'MEMORY_GUARD {mem}')
   while pending and len(active)<slots:
    w=pending.pop(0);integrity(w)
    d=dest(w);d.mkdir(exist_ok=True,parents=True)
    cmd=[str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/run_thirteen_window_normal_20261011.py'),'--window',str(w[0]),str(w[1]),'--workers',str(workers),'--authorization-file',str(AUTH),'--output',str(d)]
    log=(d/'runner.log').open('a')
    proc=subprocess.Popen(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT)},stdout=log,stderr=subprocess.STDOUT)
    active[tuple(w)]=(proc,log);emit('START',window=list(w),pid=proc.pid,workers=workers)
   for w,(proc,log) in list(active.items()):
    code=proc.poll()
    if code is None:continue
    log.close();del active[w]
    result=integrity(w)
    if code or result['status']!='COMPLETED':raise RuntimeError(f'RUNNER_FAILED {w} code={code} {result}')
    emit('COMPLETE',window=list(w),generation=result['generation'])
   if active:time.sleep(5)
  emit('ALL_COMPLETE')
 except BaseException as exc:
  emit('HALT',reason=str(exc))
  for w in list(active):stop_runner(w)
  raise
 finally:lock.close()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--preflight',action='store_true');ap.add_argument('--run',action='store_true');ap.add_argument('--slots',type=int,default=2);ap.add_argument('--workers',type=int,default=14)
 a=ap.parse_args()
 if a.self_test:
  assert dest(WINDOWS[0])==BASE
  assert dest(WINDOWS[1])!=BASE
  assert memory()['available_gib']>0
  assert (a.slots,a.workers) in ((2,14),(3,9),(4,7))
  print(json.dumps({'status':'SELF_TEST_PASS','live_runners_touched':False}))
 elif a.preflight:print(json.dumps(preflight(),indent=2))
 elif a.run:run(a.slots,a.workers)
 else:ap.error('specify --self-test, --preflight or --run')
if __name__=='__main__':main()
