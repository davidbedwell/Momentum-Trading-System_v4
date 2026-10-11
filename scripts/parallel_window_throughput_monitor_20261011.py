#!/usr/bin/env python3
"""Passive two-window throughput sampler; never modifies research state."""
import json,time,pathlib,datetime,os
base=pathlib.Path(__file__).resolve().parents[1]/'Research/Runs/thirteen-window-normal-20261011'
output=base/'parallel_throughput_samples.jsonl'
def sample():
 d={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'unix':time.time(),'windows':{}}
 for w in ('11_15','16_20'):
  p=base/f'window_{w}'/'state.json'
  try:
   s=json.loads(p.read_text())
   d['windows'][w]={'generation':s['generation'],'completed':s.get('completed',False),'mtime':p.stat().st_mtime}
  except (FileNotFoundError,ValueError,KeyError) as e:d['windows'][w]={'error':str(e)}
 return d
with output.open('a') as f:
 for i in range(31):
  f.write(json.dumps(sample())+'\n');f.flush();os.fsync(f.fileno())
  if i<30:time.sleep(60)
