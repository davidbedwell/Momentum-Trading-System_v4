"""Frozen development diagnostic, no GA, no sealed forward data."""
import json
from pathlib import Path
from dataclasses import replace
import numpy as np
import pandas as pd
from .exploratory import inputs
from .execution import Gene,Manager,replay,metrics

def ranking(p,a,b,h=20):
    top=[];bottom=[]
    for t in range(a,b-h-1):
        valid=p.eligible[t]&np.isfinite(p.screen_score[t])&np.isfinite(p.open[t+1])&np.isfinite(p.open[t+h+1])
        js=np.flatnonzero(valid)
        if len(js)<10: continue
        js=js[np.argsort(p.screen_score[t,js],kind='stable')]
        y=p.open[t+h+1,js]*.99940005/(p.open[t+1,js]*1.00060005)-1
        bottom.append(float(np.mean(y[:5])));top.append(float(np.mean(y[-5:])))
    return dict(sessions=len(top),top_net_20d=float(np.mean(top)) if top else None,bottom_net_20d=float(np.mean(bottom)) if bottom else None,spread=float(np.mean(np.array(top)-bottom)) if top else None)

def run(out):
    out=Path(out);out.mkdir(exist_ok=True)
    p,prov,refs=inputs('real')
    # Freeze Nasdaq QQQ, top ten, 20/60/120 ranks, 2% price stop, 9% weights BEFORE outcomes.
    policy=dict(primary_benchmark='QQQ',top_n=10,weight=.09,stop_distance=.02,stop_policy='daily close ratchet, next-open execution',risk_cap=.02,reserve=.1,cost_bps_per_side=6,train='2022',development_test='2023-2024 previously exposed',sealed_data_access=False)
    (out/'policy.json').write_text(json.dumps(policy,indent=2))
    train=np.flatnonzero(p.dates<'2023');test=np.flatnonzero(p.dates>='2023')
    rank_train=ranking(p,int(train[0]),int(train[-1])+1)
    # Simple mechanical benchmark has no learned expected edge: explicitly diagnostic.
    mask=np.zeros_like(p.screen_mask)
    for t in range(len(p.dates)):
        js=np.flatnonzero(p.screen_mask[t]);js=js[np.argsort(-p.screen_score[t,js],kind='stable')[:10]];mask[t,js]=True
    p=replace(p,screen_mask=mask)
    signal=np.where(mask,p.screen_score,-np.inf)[None]
    g=Gene('momentum',threshold=0,weight=.09,stop_distance=.02,hold_sessions=20,add=100,reduce=-100,exit_threshold=-100,trailing=1)
    m=Manager(slots=10,reserve=.1,risk_cap=.02,position_cap=.10,correlation=1.1,sector_cap=1,allow_add=False,replacement=2)
    result=replay(p,[g],m,'2023','2025',True,signal,True,hold_signal=np.ones_like(signal))
    (out/'daily.json').write_text(json.dumps(result,allow_nan=False))
    ref=refs.get('QQQ');bench=None
    if ref is not None:
        d=ref.loc[p.dates[test]]
        if np.isfinite(d[['open','close']]).all().all():
            nav=np.r_[100000,100000*d.close.to_numpy()[1:]/(d.open.iloc[1]*1.00060005)]
            bench=metrics(nav.tolist(),[],[1]*len(nav),len(nav))
    metric=result['metrics'];excess=metric['cagr']-bench['cagr'] if bench else None
    report=dict(policy=policy,provenance=prov,symbol_count=len(p.symbols),train_ranking=rank_train,development_ranking=ranking(p,int(test[0]),int(test[-1])+1),momentum_diagnostic=metric,risk_audit=result['audit'],QQQ=bench,excess_cagr=excess,pareto=[dict(cagr=metric['cagr'],mdd=metric['max_drawdown'],calmar=metric['calmar'],excess_cagr=excess)],status='NO_VALID_PROOF_NO_TRADE',long_ga_started=False,limitations=['observed-bar eligibility is not verified historical membership','survivorship bias and missing delisting outcomes','archive distributions and split normalization unverified','QQQ completeness required for economic proof','fixed development diagnostic is not a positive expected net-edge model','close-observed stops execute next open; gaps can exceed 2% planned risk','close marked risk can drift above cap; admission constraint is not a guarantee'])
    (out/'baseline_report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps({k:v for k,v in report.items() if k!='provenance'},indent=2))
if __name__=='__main__':
    import sys
    run(sys.argv[1])
