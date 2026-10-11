"""Test serial completion, restart, failure stop, and replay without GA compute."""
import json,pathlib,tempfile,subprocess
from unittest.mock import patch
from scripts import run_thirteen_window_serial_20261011 as serial
with tempfile.TemporaryDirectory() as tmp:
 jobs=serial.plan(tmp)[:4]
 calls=[]
 def simulate(cmd,**kwargs):
  lo,hi=int(cmd[cmd.index('--window')+1]),int(cmd[cmd.index('--window')+2])
  calls.append((lo,hi))
  if (lo,hi)==(11,15) and calls.count((11,15))==1:raise subprocess.CalledProcessError(9,cmd)
  out=pathlib.Path(cmd[cmd.index('--output')+1]);out.mkdir(exist_ok=True)
  (out/'state.json').write_text(json.dumps({'completed':True,'generation':175,'stop_reason':'ROLLING_STOP'}))
 with patch.object(serial,'require_launch_authorization',return_value={'status':'READY'}),patch.object(serial.subprocess,'run',side_effect=simulate):
  try:serial.run(jobs,pathlib.Path(tmp)/'token')
  except subprocess.CalledProcessError:pass
  else:raise AssertionError('failure should halt serial controller')
  assert calls==[(2,5),(6,10),(11,15)],calls
  assert [x['window'] for x in serial.remaining(jobs)]==[[11,15],[16,20]]
  serial.run(jobs,pathlib.Path(tmp)/'token')
  assert calls==[(2,5),(6,10),(11,15),(11,15),(16,20)],calls
  assert not serial.remaining(jobs)
  serial.run(jobs,pathlib.Path(tmp)/'token')
  assert len(calls)==5
print('SERIAL_FAILURE_RESTART_REPLAY_TEST_PASS')
