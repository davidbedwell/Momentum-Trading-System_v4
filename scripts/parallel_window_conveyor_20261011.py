#!/usr/bin/env python3
"""Two-slot independent-window conveyor; per-window durable state and fail-closed checks."""
import concurrent.futures,json,os,pathlib,subprocess,sys,datetime,threading,queue
from scripts.stage2_window_conveyor_20261011 import ROOT,BASE,AUTH,WINDOWS,state
from scripts.thirteen_window_launch_guard_20261011 import require_launch_authorization
STATUS=BASE/'parallel_conveyor_status.json'
def report(event,window=None,**kw):
 data={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event,'window':window,**kw}
 with (BASE/'parallel_conveyor_events.jsonl').open('a') as f:f.write(json.dumps(data)+'\n');f.flush();os.fsync(f.fileno())
 tmp=STATUS.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2));os.replace(tmp,STATUS)
 print(json.dumps(data),flush=True)
def run(window):
 lo,hi=window;index=WINDOWS.index(window);dest=BASE if index==0 else BASE/f'window_{lo:02d}_{hi:02d}'
 dest.mkdir(parents=True,exist_ok=True)
 if state(dest).get('completed'):report('SKIP_COMPLETED',window);return
 cmd=[str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/run_thirteen_window_normal_20261011.py'),'--window',str(lo),str(hi),'--workers','14','--authorization-file',str(AUTH),'--output',str(dest)]
 with (dest/'runner.log').open('a') as f:
  proc=subprocess.Popen(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT)},stdout=f,stderr=subprocess.STDOUT)
  report('START',window,pid=proc.pid,workers=14)
  code=proc.wait()
 s=state(dest)
 if code or not s.get('completed'):
  report('FAIL',window,exit_code=code,generation=s.get('generation'))
  raise RuntimeError(f'WINDOW_FAILED {window} code={code} gen={s.get("generation")}')
 report('COMPLETE',window,generation=s.get('generation'),reason=s.get('stop_reason'))
def main():
 require_launch_authorization(authorization_path=AUTH)
 todo=[]
 for w in WINDOWS:
  lo,hi=w;dest=BASE if w==WINDOWS[0] else BASE/f'window_{lo:02d}_{hi:02d}'
  if not state(dest).get('completed'):todo.append(w)
 report('CONVEYOR_STARTED',remaining=todo,slots=2)
 # Strict two-slot queue; fail closed before dispatching another window.
 jobs=queue.Queue()
 for w in todo:jobs.put(w)
 stop=threading.Event();errors=[]
 def slot():
  while not stop.is_set():
   try:w=jobs.get_nowait()
   except queue.Empty:return
   try:run(w)
   except BaseException as exc:errors.append((w,repr(exc)));stop.set()
   finally:jobs.task_done()
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
  fs=[ex.submit(slot) for _ in range(2)]
  for f in fs:f.result()
 if errors:raise RuntimeError(f'PARALLEL_WINDOW_FAILURE {errors}')
 report('ALL_WINDOWS_COMPLETE')
if __name__=='__main__':
 try:main()
 except Exception as exc:report('CONVEYOR_FAILED',error=repr(exc));sys.exit(1)
