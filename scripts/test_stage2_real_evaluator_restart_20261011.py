#!/usr/bin/env python3
"""Kill and resume a real Horizon evaluator subprocess using DEV80 and journal."""
import json,os,pathlib,subprocess,sys,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
WORKER='''import json,pathlib,sys,time,os
from scripts.run_thirteen_window_normal_20261011 import worker_init,evaluate
from scripts.thirteen_window_oct09_seeds_20261011 import load
from scripts.audit_evolution_domains_20261010 import schema
from scripts.evolution_safety_20261010 import durable_append,recover_jsonl
os.environ['MTS_WINDOW_LOW']='2';os.environ['MTS_WINDOW_HIGH']='5'
p=pathlib.Path(sys.argv[1]);cs=load(schema())[0][:3];done={r['genome_hash'] for r in recover_jsonl(p/'evaluations.jsonl')}
worker_init()
for c in cs:
 if c['genome_hash'] in done:continue
 r=evaluate(c)
 durable_append(p/'evaluations.jsonl',[r])
 print('EVALUATED',c['genome_hash'],r['status'],flush=True)
 time.sleep(5)
'''
with tempfile.TemporaryDirectory(prefix='stage2-real-restart-') as d:
 p=pathlib.Path(d);w=p/'worker.py';w.write_text(WORKER);env=os.environ.copy();env['PYTHONPATH']=str(ROOT)
 cmd=[sys.executable,str(w),str(p)]
 proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 try:
  from scripts.evolution_safety_20261010 import recover_jsonl
  deadline=time.monotonic()+90
  while time.monotonic()<deadline:
   done=recover_jsonl(p/'evaluations.jsonl')
   if len(done)>=1:break
   if proc.poll() is not None:raise RuntimeError('Evaluator failed before first journal: '+proc.stderr.read().decode()[-1200:])
   time.sleep(.25)
  else:raise RuntimeError('real evaluator timeout')
  proc.kill();proc.wait(timeout=10)
  first=recover_jsonl(p/'evaluations.jsonl')
  assert len(first)==1,('kill not between evaluations',len(first))
  replay=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
  if replay.returncode:raise RuntimeError(replay.stderr[-1200:])
  after=recover_jsonl(p/'evaluations.jsonl')
  assert len(after)==3 and len({r['genome_hash'] for r in after})==3
  assert after[0]==first[0] and all(r['status']=='EVALUATED_UNCERTIFIED' for r in after),after
  print(json.dumps({'status':'PASS_REAL_HORIZON_EVALUATOR_KILL_RESUME','completed_before_kill':1,'completed_after_resume':3,'window':[2,5],'dev80_only':True}))
 finally:
  if proc.poll() is None:proc.kill();proc.wait()
