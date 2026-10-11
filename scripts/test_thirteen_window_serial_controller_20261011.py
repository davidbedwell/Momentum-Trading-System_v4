"""Synthetic controller orchestration tests. No live GA, no authorization bypass."""
import json,pathlib,tempfile
from unittest.mock import patch
from scripts import run_thirteen_window_serial_20261011 as serial
jobs=serial.plan('/tmp/not-executed')
assert len(jobs)==13 and [j['window'] for j in jobs]==[[2,5],[6,10],[11,15],[16,20],[21,25],[26,30],[31,35],[36,40],[41,45],[46,50],[51,55],[56,60],[61,65]]
assert len({j['output'] for j in jobs})==13 and len({j['seed'] for j in jobs})==13
with tempfile.TemporaryDirectory() as tmp:
 jobs=serial.plan(tmp)
 for job in jobs[:3]:
  path=pathlib.Path(job['output']);path.mkdir();(path/'state.json').write_text(json.dumps({'completed':True}))
 assert serial.is_complete(jobs[0]) and not serial.is_complete(jobs[3])
 assert [j['window'] for j in serial.remaining(jobs)]==[j['window'] for j in jobs[3:]]
 path=pathlib.Path(jobs[3]['output']);path.mkdir();(path/'state.json').write_text(json.dumps({'completed':False}))
 assert not serial.is_complete(jobs[3])
 with patch.object(serial,'require_launch_authorization',side_effect=PermissionError('NO_AUTH')):
  try:serial.run(jobs,None)
  except PermissionError:pass
  else:raise AssertionError('unauthorized controller ran')
 assert not (path/'pending.json').exists()
 print('SERIAL_ISOLATION_RESUME_AUTH_TEST_PASS')
