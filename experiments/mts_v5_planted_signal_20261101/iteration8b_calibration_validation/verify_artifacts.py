"""Post-run independent artifact audit; never changes candidate or outputs."""
import json,gzip,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parent
rows=[json.loads(l) for l in (O/'per_seed.jsonl').open()];by={(x['seed'],x['scenario'],x['arm']):x for x in rows}
assert len(by)==len(rows)==480
cal=json.loads((O/'calibration.json').read_text());mx=[max(x['maxima'][j] for x in cal['logs']) for j in range(2)]
assert cal['thresholds']==[max(.018,1.1*x) for x in mx]
assert len(cal['logs'])==96
seeds=json.loads((O/'seeds.json').read_text());assert len(set(seeds['holdout']+seeds['calibration']))==56
for seed in seeds['holdout']:
 for sc in ('learnable','reversal','random_reversal','outer_noise','null'):
  a=by[seed,sc,'8B-D'];b=by[seed,sc,'8B-Cal'];assert a['models']==b['models']
  for r in (a,b):
   for event in r['events']:
    assert event['last_signal']==event['index']-3
    assert event['thresholds']==(cal['thresholds'] if r['arm']=='8B-Cal' else cal['original_thresholds'])
n=0
with gzip.open(O/'replays.jsonl.gz','rt') as f:
 for l in f:
  r=json.loads(l);n+=1
  if r['arm'] not in ('8B-D','8B-Cal'):continue
  latched=False;prev=[0.,0.];threshold=cal['thresholds'] if r['arm']=='8B-Cal' else cal['original_thresholds'];model=by[r['seed'],r['scenario'],r['arm']]['models']
  # Baseline mu is date contrast from FIT (not model contrast); recover from first nonzero update only if needed. Audit threshold/latch timing without estimating it.
  for t in r['trace']:
   if not latched:
    expected=any(a>=h for a,h in zip(t['statistics'],threshold));assert t['latched']==expected
   else:assert t['latched'] and t['statistics']==prev
   latched=t['latched'];prev=t['statistics']
assert n==480
count=0
with gzip.open(O/'opportunities.jsonl.gz','rt') as f:
 for l in f:
  r=json.loads(l);count+=1
  event=by[r['seed'],r['scenario'],r['arm']]['first_alarm']
  if event is not None and r['index']>=event:assert r['label']=='UNKNOWN' and not r['funded']
assert count==480*126*24
result=dict(status='PASS',portfolios=n,opportunities=count,calibration_maxima_recomputed=True,threshold_only_shared_models=True,latch_and_clock=True,seeds_disjoint=True)
(O/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
