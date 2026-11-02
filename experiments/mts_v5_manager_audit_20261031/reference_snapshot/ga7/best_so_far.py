import json
from pathlib import Path
p=Path('/opt/mts/ga7-deploy/current/ga7/runs/dev32_ga7_production')
best={}
for f in sorted(p.glob('generation_*.jsonl')):
 for line in f.open():
  r=json.loads(line); m=r['metrics']; g=r['genome']
  for k in ('fitness','cagr','return_per_session'):
   v=m.get(k)
   if v is not None and (k not in best or v>best[k]['metrics'][k]):
    best[k]=r
for k,r in best.items():
 print('BEST',k,'generation',r['generation'])
 print('GENOME',json.dumps(r['genome'],sort_keys=True))
 print('METRICS',json.dumps(r['metrics'],sort_keys=True))
print('GENERATIONS',len(list(p.glob('generation_*.jsonl'))))
