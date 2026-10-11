#!/usr/bin/env python3
"""Isolated controller tests, no live GA mutation."""
import pathlib,tempfile,subprocess,sys,time,os,signal,json
from unittest.mock import patch
from scripts import checkpoint_transition_controller_20261011 as c
def test():
 assert c.dest(c.WINDOWS[0])==c.BASE
 assert c.dest(c.WINDOWS[1])!=c.BASE
 assert c.memory()['swap_used_gib']<=4
 with tempfile.TemporaryDirectory() as tmp:
  root=pathlib.Path(tmp);w=(31,35);d=root/'window_31_35';d.mkdir()
  config={'window':[31,35],'initial_population_count':2,'batch':2}
  (d/'state.json').write_text(json.dumps({'generation':0,'config':config,'completed':False}))
  candidates=[{'generation':0,'genome_hash':'a'},{'generation':0,'genome_hash':'b'}]
  (d/'candidates.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in candidates))
  (d/'evaluations.jsonl').write_text(''.join(json.dumps({'genome_hash':x['genome_hash']})+'\n' for x in candidates))
  with patch.object(c,'dest',return_value=d):
   assert c.integrity(w)['status']=='RESUMABLE'
   (d/'pending.json').write_text(json.dumps({'generation':1}))
   with (d/'candidates.jsonl').open('a') as f:
    for k in ('c','d'):f.write(json.dumps({'generation':1,'genome_hash':k})+'\n')
   assert c.integrity(w)['pending_evaluations']==2
   (d/'pending.json').unlink()
   try:c.integrity(w)
   except RuntimeError as e:assert 'MISSING_PENDING' in str(e)
   else:raise AssertionError('missing pending journal accepted')
  sleeper=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
  try:
   assert sleeper.poll() is None
   os.kill(sleeper.pid,signal.SIGTERM)
   assert sleeper.wait(timeout=5)==-signal.SIGTERM
  finally:
   if sleeper.poll() is None:sleeper.kill();sleeper.wait()
 try:c.run(3,9)
 except RuntimeError as e:assert 'LEGACY_CONTROLLER_RUNNING' in str(e),str(e)
 else:raise AssertionError('Legacy-controller collision was not rejected')
 print('PASS: resumable checkpoint, pending generation, missing pending rejection, termination, legacy collision guard',flush=True)
if __name__=='__main__':test()
