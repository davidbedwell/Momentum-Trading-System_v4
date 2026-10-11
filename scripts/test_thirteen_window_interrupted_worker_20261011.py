#!/usr/bin/env python3
"""Actually kill a journaled evaluation subprocess and replay missing tasks.
Isolated evaluator fixture, not a production Horizon runner certification.
"""
import hashlib,json,os,pathlib,signal,subprocess,sys,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.evolution_safety_20261010 import atomic_json,durable_append,recover_jsonl
WORKER='''import hashlib,json,pathlib,sys,time
from scripts.evolution_safety_20261010 import durable_append
p=pathlib.Path(sys.argv[1]);delay=float(sys.argv[2]);cs=[json.loads(s) for s in (p/'candidates.jsonl').read_text().splitlines()];done={r['genome_hash'] for r in (json.loads(s) for s in (p/'evaluations.jsonl').read_text().splitlines())}
for c in cs:
 if c['genome_hash'] in done:continue
 time.sleep(delay)
 durable_append(p/'evaluations.jsonl',[{'genome_hash':c['genome_hash'],'value':hashlib.sha256(c['genome_hash'].encode()).hexdigest()}])
'''
with tempfile.TemporaryDirectory(prefix='mts-interrupt-') as d:
 p=pathlib.Path(d);cs=[{'generation':0,'genome_hash':f'fixture-{i:03d}'} for i in range(12)]
 atomic_json(p/'pending.json',{'generation':0,'rng_state':'fixed-fixture'})
 durable_append(p/'candidates.jsonl',cs)
 (p/'evaluations.jsonl').touch()
 w=p/'worker.py';w.write_text(WORKER)
 env=os.environ.copy();env['PYTHONPATH']=str(ROOT)
 cmd=[sys.executable,str(w),str(p),'0.15']
 proc=subprocess.Popen(cmd,env=env)
 try:
  deadline=time.monotonic()+8
  while time.monotonic()<deadline:
   done=recover_jsonl(p/'evaluations.jsonl')
   if 2<=len(done)<len(cs):break
   time.sleep(.04)
  else:raise RuntimeError('interruption checkpoint not reached')
  proc.kill();proc.wait(timeout=5)
  interrupted=recover_jsonl(p/'evaluations.jsonl')
  assert 1<len(interrupted)<len(cs)
  subprocess.run([sys.executable,str(w),str(p),'0'],env=env,check=True,timeout=20)
  resumed=recover_jsonl(p/'evaluations.jsonl')
  expected=[{'genome_hash':c['genome_hash'],'value':hashlib.sha256(c['genome_hash'].encode()).hexdigest()} for c in cs]
  assert len(resumed)==len(cs) and len({r['genome_hash'] for r in resumed})==len(cs)
  assert resumed==expected
  print(json.dumps({'status':'PASS_REAL_PROCESS_KILL_RESTART_FIXTURE','completed_before_kill':len(interrupted),'completed_after_restart':len(resumed),'production_evaluator_recovery_certified':False}))
 finally:
  if proc.poll() is None:proc.kill();proc.wait()
