from __future__ import annotations
import json
from pathlib import Path
from Core.g3.earnings_evidence import build_earnings_index,aligned_evidence_with_earnings
from Core.g3.search_v3 import structural_screen
from Core.g3.starter import evaluate_one,quality,aggregate_quality_summaries
from scripts.run_g3_preregistered_replicated_gate_v2_20261007 import TICKERS

def q(g,d):
    return aggregate_quality_summaries([quality(evaluate_one(g,*d[t],10)) for t in d])
if __name__=='__main__':
    ev=build_earnings_index(TICKERS);dates,X,Y,cols=aligned_evidence_with_earnings(TICKERS,ev);X=X[-2500:];Y=Y[-2500:]
    cut=1250
    train={t:(X[:cut,i,:],Y[:cut,i,:]) for i,t in enumerate(TICKERS)}
    test={t:(X[cut:,i,:],Y[cut:,i,:]) for i,t in enumerate(TICKERS)}
    rows=[]
    # pooled structure selected strictly on first half
    pg=structural_screen(train,1)[0]
    rows.append({'scope':'POOLED','train':q(pg,train),'test_pooled':q(pg,test),'test_by_stock':{t:q(pg,{t:test[t]}) for t in TICKERS},'genome':repr(pg)})
    # each local structure selected strictly on that stock's first half; evaluate frozen on all second-half stocks
    for t in TICKERS:
        g=structural_screen({t:train[t]},1)[0]
        rows.append({'scope':t,'train_local':q(g,{t:train[t]}),'test_local':q(g,{t:test[t]}),'test_other_pooled':q(g,{u:test[u] for u in TICKERS if u!=t}),'test_by_stock':{u:q(g,{u:test[u]}) for u in TICKERS},'genome':repr(g)})
    out={'format':'MTS_G3_LOCALITY_TIME_SPLIT_DIAGNOSTIC_V1','train_dates':[str(dates[-2500]),str(dates[-1251])],'test_dates':[str(dates[-1250]),str(dates[-1])],'rows':rows}
    Path('Research/G3/MTS_G3_LOCALITY_TIME_SPLIT_DIAGNOSTIC_20261007.json').write_text(json.dumps(out,indent=2)+'\n')
    for r in rows:
        if r['scope']=='POOLED': print('POOLED',r['train']['mean'],r['test_pooled']['mean'])
        else: print(r['scope'],'train',r['train_local']['mean'],'test_local',r['test_local']['mean'],'test_other',r['test_other_pooled']['mean'])
