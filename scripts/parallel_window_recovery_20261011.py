#!/usr/bin/env python3
"""Recover a stalled conveyor, adopting an existing runner without duplication."""
import os,time,json,pathlib,subprocess,concurrent.futures,threading,queue,datetime
from scripts.stage2_window_conveyor_20261011 import ROOT,BASE,AUTH,WINDOWS,state
from scripts.thirteen_window_launch_guard_20261011 import require_launch_authorization
EVENT=BASE/'parallel_conveyor_recovery_events.jsonl'
LOCK=threading.Lock()
def report(event,w=None,**kw):
 with LOCK:
  with EVENT.open('a') as f:
   f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event,'window':w,**kw})+'\n')
   f.flush();os.fsync(f.fileno())
def alive(pid):
 try:
  s=pathlib.Path(f'/proc/{pid}/stat').read_text()
  return s[s.rfind(')')+2:].split()[0]!='Z'
 except FileNotFoundError:return False
def run(w,adopt=None):
 lo,hi=w;dest=BASE/f'window_{lo:02d}_{hi:02d}'
 if state(dest).get('completed'):
  report('SKIP_COMPLETED',w);return
 if adopt:
  report('ADOPT',w,pid=adopt)
  while alive(adopt):time.sleep(5)
  code=None
 else:
  cmd=[str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/run_thirteen_window_normal_20261011.py'),'--window',str(lo),str(hi),'--workers','14','--authorization-file',str(AUTH),'--output',str(dest)]
  dest.mkdir(parents=True,exist_ok=True)
  with (dest/'runner.log').open('a') as f:
   p=subprocess.Popen(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT)},stdout=f,stderr=subprocess.STDOUT)
   report('START',w,pid=p.pid,workers=14)
   code=p.wait()
 s=state(dest)
 if code not in (None,0) or not s.get('completed'):
  report('FAIL',w,exit_code=code,generation=s.get('generation'))
  raise RuntimeError(f'Window {w} not completed')
 report('COMPLETE',w,generation=s.get('generation'),reason=s.get('stop_reason'))
def main():
 require_launch_authorization(authorization_path=AUTH)
 jobs=queue.Queue()
 for w in WINDOWS:
  lo,hi=w;d=BASE if w==WINDOWS[0] else BASE/f'window_{lo:02d}_{hi:02d}'
  if not state(d).get('completed'):jobs.put(w)
 stop=threading.Event();errors=[]
 def slot():
  while not stop.is_set():
   try:w=jobs.get_nowait()
   except queue.Empty:return
   try:run(w,33352 if w==[16,20] or w==(16,20) else None)
   except Exception as e:errors.append(str(e));stop.set()
   finally:jobs.task_done()
 report('RECOVERY_STARTED',slots=2,remaining=jobs.qsize())
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
  fs=[ex.submit(slot) for _ in range(2)]
  for f in fs:f.result()
 if errors:raise RuntimeError(str(errors))
 report('ALL_WINDOWS_COMPLETE')
if __name__=='__main__':main()
