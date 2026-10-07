#!/usr/bin/env python3
from layered_stage_common_20261007 import *
bank=load_bank()[:12]
def task(t):
 d=frame(t);out=[]
 for ci,c in enumerate(bank):
  m=mask(d,c);sg=1 if c['direction']=='LONG' else -1;imm=signed(d.loc[m,f"f{c['horizon']}"],c).dropna().tolist();wait=[];mae=[];confirm=(sg*d.ret1.shift(-1)>0);idx=np.where((m&confirm).fillna(False))[0];px=d.adj_close.to_numpy()
  for i in idx:
   j=min(i+1+c['horizon'],len(d)-1)
   if i+1<j:wait.append(sg*(px[j]/px[i+1]-1));mae.append(float(np.min(sg*(px[i+1:j+1]/px[i+1]-1))))
  out.append((ci,imm,wait,mae))
 return out
agg=[[[],[],[]] for _ in bank]
for batch in pmap(task,[p.stem for p in sorted(ROOT.glob('*.parquet'))]):
 for ci,a,b,c in batch:agg[ci][0]+=a;agg[ci][1]+=b;agg[ci][2]+=c
rows=[]
for i,c in enumerate(bank):
 imm,wait,mae=agg[i];rows.append({'candidate':c,'immediate_ev':float(np.mean(imm)) if imm else None,'confirm_next_session_ev':float(np.mean(wait)) if wait else None,'confirm_n':len(wait),'confirm_mae_mean':float(np.mean(mae)) if mae else None})
write(4,'entry-mae',{'workers':WORKERS,'entry_comparisons':rows,'interpretation':'Confirmation uses only the next completed session then enters; no fixed wait is imposed as policy.'})
