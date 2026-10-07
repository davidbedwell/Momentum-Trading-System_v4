#!/usr/bin/env python3
from layered_stage_common_20261007 import *
rows=[]
for c in load_bank()[:12]:
 imm=[];wait=[];mae=[]
 for p in ROOT.glob('*.parquet'):
  d=frame(p.stem);m=mask(d,c);sg=1 if c['direction']=='LONG' else -1
  imm+=signed(d.loc[m,f"f{c['horizon']}"],c).dropna().tolist()
  confirm=(sg*d.ret1.shift(-1)>0); idx=np.where((m&confirm).fillna(False))[0]
  for i in idx:
   h=c['horizon'];j=min(i+1+h,len(d)-1)
   if i+1<j:
    px=d.adj_close.to_numpy();wait.append(sg*(px[j]/px[i+1]-1));mae.append(float(np.min(sg*(px[i+1:j+1]/px[i+1]-1))))
 rows.append({'candidate':c,'immediate_ev':float(np.mean(imm)) if imm else None,'confirm_next_session_ev':float(np.mean(wait)) if wait else None,'confirm_n':len(wait),'confirm_mae_mean':float(np.mean(mae)) if mae else None})
write(4,'entry-mae',{'entry_comparisons':rows,'interpretation':'Confirmation uses only the next completed session then enters; no fixed wait is imposed as policy.'})
