#!/usr/bin/env python3
"""Read-only journal rate sampler. Reports raw counts and caveats."""
import json,pathlib,datetime,time
from scripts.stage2_window_conveyor_20261011 import BASE,WINDOWS,state
def snapshot():
 r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'monotonic':time.monotonic(),'windows':{}}
 for w in WINDOWS:
  d=BASE if w==WINDOWS[0] else BASE/f'window_{w[0]:02d}_{w[1]:02d}'
  s=state(d);p=d/'evaluations.jsonl'
  if not p.exists():continue
  # Count newline-terminated evaluation records; do not parse partially appended lines.
  with p.open('rb') as f: count=sum(chunk.count(b'\n') for chunk in iter(lambda:f.read(1024*1024),b''))
  r['windows'][f'{w[0]}-{w[1]}']={'evaluations':count,'generation':s.get('generation'),'completed':s.get('completed')}
 return r
def main():
 p=BASE/'throughput_comparison_samples.jsonl'
 s=snapshot()
 with p.open('a') as f:f.write(json.dumps(s)+'\n')
 old=[json.loads(x) for x in p.read_text().splitlines() if x.strip()]
 print(json.dumps({'current':s,'samples':len(old)},indent=2))
 if len(old)>1:
  prev=old[-2];dt=s['monotonic']-prev['monotonic']
  deltas={k:v['evaluations']-prev['windows'][k]['evaluations'] for k,v in s['windows'].items() if k in prev['windows']}
  print(json.dumps({'seconds':dt,'evaluations_per_hour':sum(deltas.values())*3600/dt if dt>0 else None,'window_deltas':deltas}))
if __name__=='__main__':main()
