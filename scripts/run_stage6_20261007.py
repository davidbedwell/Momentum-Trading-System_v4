#!/usr/bin/env python3
from layered_stage_common_20261007 import *
bank=load_bank()[:12];names=['ADD','HOLD','REDUCE','EXIT']
def task(t):
 d=frame(t);out=[]
 for ci,c in enumerate(bank):
  m=mask(d,c);strength=d[c['feature']].rank(pct=True);sets=[m&(strength>.9),m&(strength.between(.5,.9)),m&(strength.between(.2,.5)),~m]
  out.append((ci,[signed(d.loc[z,'f5'],c).dropna().tolist() for z in sets]))
 return out
agg=[[[] for _ in names] for _ in bank]
for batch in pmap(task,[p.stem for p in sorted(ROOT.glob('*.parquet'))]):
 for ci,sets in batch:
  for j,v in enumerate(sets):agg[ci][j]+=v
rows=[]
for i,c in enumerate(bank):rows.append({'candidate':c,'actions':{a:{'n':len(agg[i][j]),'next5_ev':float(np.mean(agg[i][j])) if agg[i][j] else None} for j,a in enumerate(names)}})
write(6,'lifecycle',{'workers':WORKERS,'action_studies':rows,'note':'Action questions remain separately measured; no monster combined policy.'})
