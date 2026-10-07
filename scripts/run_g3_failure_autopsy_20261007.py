from __future__ import annotations
import json,random
from pathlib import Path
import numpy as np
from Core.g3.earnings_evidence import build_earnings_index,aligned_evidence_with_earnings
from Core.g3.starter import planted_dataset,Specialist,Rule,evaluate_one,quality
from scripts.run_g3_preregistered_replicated_gate_20261007 import TICKERS,run_arm

def simple_separation(X,Y,cols):
    # causal feature already standardized; test fixed tails, no optimization by GA.
    rows=[]
    target=np.prod(1+Y,axis=1)-1
    for j,c in enumerate(cols):
        for direction,label in [(1,'high'),(-1,'low')]:
            mask=X[:,j]>=1 if direction>0 else X[:,j]<=-1
            if mask.sum()>=50:
                rows.append((float(target[mask].mean()-target.mean()),int(mask.sum()),c,label,float(target[mask].mean()),float(target.mean())))
    return sorted(rows,reverse=True)
if __name__=='__main__':
    events=build_earnings_index(TICKERS);dates,X,Y,cols=aligned_evidence_with_earnings(TICKERS,events);X=X[-2500:];Y=Y[-2500:]
    # Cross-stock simple tail separation without GA.
    sep=[]
    for i,t in enumerate(TICKERS):
        s=simple_separation(X[:,i,:],Y[:,i,:],cols)
        sep.append({'ticker':t,'top':s[:5],'bottom':s[-5:]})
    # Production GA's ability to recover a deliberately strong planted specialist, replicated.
    planted=[]
    for rep in range(10):
        data={}
        for i,t in enumerate(TICKERS):
            x,y,_=planted_dataset(seed=1000+rep*20+i,n=2500,p=len(cols),h=10,effect=.01)
            data[t]=(x,y)
        rr=run_arm(data,6,48,60,1776000+rep)
        # oracle uses known planted rule and same costs/lifecycle family
        oracle=Specialist(Rule(0,.7,1),Rule(1,-.3,-1),1,.2,.2,3,.2,.2)
        oq=[quality(evaluate_one(oracle,*data[t],10)) for t in TICKERS]
        oracle_mean=sum(q['mean']*q['n'] for q in oq)/sum(q['n'] for q in oq)
        planted.append({'rep':rep,'ga_primary':rr['primary'],'ga_best_final':rr['ledger'][-1]['best']['mean'],'oracle_mean':oracle_mean})
    out={'format':'MTS_G3_FAILURE_AUTOPSY_V1','simple_real_separation':sep,'planted_production_search':planted}
    Path('Research/G3/MTS_G3_FAILURE_AUTOPSY_20261007.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PLANTED')
    for z in planted: print(z)
    print('TOP_REAL')
    for z in sep: print(z['ticker'],z['top'][:2])
