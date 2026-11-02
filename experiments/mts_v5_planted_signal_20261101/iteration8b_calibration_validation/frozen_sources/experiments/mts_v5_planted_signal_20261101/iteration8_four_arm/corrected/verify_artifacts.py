"""Read-only post-run archive validation, no portfolio replay or parameter fitting."""
import gzip,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent
r=json.loads((O/'results.json').read_text());rows=r['rows'];keys=lambda x:(x['seed'],x['scenario'],x['arm'])
lookup={keys(x):x for x in rows};assert len(lookup)==640
count=0
with gzip.open(O/'replays.jsonl.gz','rt') as f:
 for line in f:
  x=json.loads(line);row=lookup[keys(x)];count+=1
  start=906 if row['stratum']=='stage2_confirmation' else 606
  assert [d['index'] for d in x['daily']]==list(range(start,start+126))
  assert len(x['trace'])==126
  assert all(t.get('last_available',t['index']-3)<=t['index']-3 for t in x['trace'])
  if row['first_alarm'] is not None:assert all(t['signal']<row['first_alarm'] for t in x['trades'])
  assert len(x['trades'])==row['trades']
assert count==640
opcount=0
with gzip.open(O/'opportunities.jsonl.gz','rt') as f:
 for line in f:
  x=json.loads(line);assert keys(x) in lookup;opcount+=1
assert opcount==640*126*24
s=json.loads((O/'seeds.json').read_text());assert len(set(s['stage1']+s['stage2']))==32
assert not set(s['stage1']+s['stage2'])&set(json.loads((O/'calibration.json').read_text())['seeds'])
c=json.loads((O/'commitment.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in c['sources'].items())
result=dict(status='PASS',replay_records=count,opportunity_records=opcount,trace_clock='all 640 x126 chronological decisions',seed_disjointness=True,frozen_hashes_match=True)
(O/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
