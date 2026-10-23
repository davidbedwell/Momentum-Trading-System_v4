import json
from collections import defaultdict
p='/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019/all_evaluations.jsonl'
best=-float('inf'); last=None; prev=None; events=[]; latest=0
for line in open(p):
 x=json.loads(line);g=x['generation'];latest=max(latest,g)
 v=x.get('fitness')
 if v is not None and v>best+1e-10:
  prev=best;best=v;last=g;events.append((g,v,None if prev==-float('inf') else v-prev,x['chromosome_id']))
print('LATEST',latest,'LAST_IMPROVEMENT',last,'GENERATIONS_SINCE',latest-last,'BEST_FITNESS',best)
print('LAST_EVENTS')
for a in events[-10:]:print(a)
print('TOTAL_IMPROVEMENTS',len(events))
