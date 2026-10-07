#!/usr/bin/env python3
from layered_stage_common_20261007 import *
rows=[]
for c in load_bank()[:12]:
 acts={'ADD':[],'HOLD':[],'REDUCE':[],'EXIT':[]}
 for p in ROOT.glob('*.parquet'):
  d=frame(p.stem);m=mask(d,c);sg=1 if c['direction']=='LONG' else -1;strength=d[c['feature']].rank(pct=True)
  for act,am in [('ADD',m&(strength>.9)),('HOLD',m&(strength.between(.5,.9))),('REDUCE',m&(strength.between(.2,.5))),('EXIT',~m)]:
   acts[act]+=signed(d.loc[am,'f5'],c).dropna().tolist()
 rows.append({'candidate':c,'actions':{a:{'n':len(v),'next5_ev':float(np.mean(v)) if v else None} for a,v in acts.items()}})
write(6,'lifecycle',{'action_studies':rows,'note':'Action questions remain separately measured; no monster combined policy.'})
