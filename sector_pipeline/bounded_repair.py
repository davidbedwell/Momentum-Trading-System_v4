"""One bounded repair audit; controls use artificial data, historical diagnostics are not gates."""
import json, hashlib, statistics as st
from pathlib import Path
import numpy as np
import pandas as pd
from . import core
OUT=Path('reports/bounded-repair')
def run():
    OUT.mkdir(exist_ok=True)
    rng=np.random.default_rng(731)
    dates=pd.date_range('2006-01-31',periods=120,freq='ME').strftime('%Y-%m-%d').tolist()
    x=rng.normal(size=(121,80)); rows=[]
    for t,date in enumerate(dates):
        for i in range(80):
            rows.append(dict(asof=date,symbol=str(i),sector=str(i//20),horizon=1,H1_rank=float(x[t,i]),excess=float(x[t,i]),rebalance_return=0))
    _,positive=core.metrics(rows,allowed={'H1_1'})
    delayed=[dict(r,H1_rank=float(x[t-1,i])) for t in range(120) for i,r in enumerate(rows[t*80:(t+1)*80]) if t>0]
    _,negative=core.metrics(delayed,allowed={'H1_1'})
    assert positive['H1_1']['mean']>.999
    assert abs(negative['H1_1']['mean'])<.05
    # Independent execution-date check through the actual row builder.
    sessions=pd.bdate_range('2004-01-01','2006-05-31').strftime('%Y-%m-%d').tolist()
    prices={str(i):[dict(date=d,adj_close=100+j*(i+1)*.01,adj_open=90+j*(i+1)*.01) for j,d in enumerate(sessions)] for i in range(4)}
    members=[dict(symbol=str(i),sector='A',start='2006-01-01',end='2006-06-01') for i in range(4)]
    formed=core.form_rows(prices,members,[2006],{}, {},sessions=sessions)
    for r in formed:
        assert r['entry']==next(d for d in sessions if d>r['asof'])
        assert r['exit']==max(d for d in sessions if d<=core.add_months(r['asof'],r['horizon']))
        p=prices[r['symbol']]; entry=next(v for v in p if v['date']==r['entry']); exit=next(v for v in p if v['date']==r['exit'])
        assert abs(r['forward_return']-(exit['adj_close']/entry['adj_open']-1))<1e-12
    df=pd.read_parquet('reports/expanded-stage1/dated_holdings_available/observations.parquet')
    historical={}
    for h in (1,3):
        a=df[df.horizon==h].copy(); a['month']=a['asof'].str[:7]
        for sig in ('H1','H2','H5'):
            results={}
            for shift in (0,1,-1):
                # shift +1: past month's signal against present return; -1: future signal warning.
                s=a[['symbol','sector','month',sig+'_rank']].copy()
                s['month']=(pd.PeriodIndex(s.month,freq='M')+shift).astype(str)
                b=a.drop(columns=[sig+'_rank']).merge(s,on=['symbol','sector','month'])
                vals=[]
                for _,g in b.groupby(['asof','sector']):
                    g=g.dropna(subset=[sig+'_rank','excess']); v=core.ic(g[sig+'_rank'].tolist(),g.excess.tolist())
                    if v is not None: vals.append(dict(asof=g['asof'].iloc[0],ic=v))
                v=pd.DataFrame(vals).groupby('asof').ic.mean()
                results[str(shift)]=dict(core.calendar_hac(v.index.tolist(),v.tolist(),3 if h==1 else 5),oriented_mean=float(v.mean())*(-1 if sig=='H5' else 1))
            # Reversal diagnostic: prior realized stock return vs next return, independent of frozen signals.
            historical[f'{sig}_{h}']=results
        b=a[['symbol','sector','asof','forward_return','excess']].copy(); b['month']=a.month
        prev=b[['symbol','sector','month','forward_return']].copy(); prev['month']=(pd.PeriodIndex(prev.month,freq='M')+h).astype(str)
        b=b.merge(prev.rename(columns={'forward_return':'past_return'}),on=['symbol','sector','month'])
        vals=[]
        for _,g in b.groupby(['asof','sector']):
            v=core.ic(g.past_return.tolist(),g.excess.tolist())
            if v is not None: vals.append(dict(asof=g['asof'].iloc[0],ic=v))
        v=pd.DataFrame(vals).groupby('asof').ic.mean()
        historical[f'nonoverlapping_return_reversal_{h}']=core.calendar_hac(v.index.tolist(),v.tolist(),3 if h==1 else 5)
    result=dict(seed=731,synthetic_positive=positive,synthetic_one_month_lag_negative=negative,execution_alignment_rows_checked=len(formed),historical=historical,alignment_defects_proven=False,notes=['Synthetic controls are not research results.','Historical lead/lag and reversal are diagnostics only; persistence can correlate future signals with current returns.','No frozen definitions, gates, or core files changed.'])
    (OUT/'diagnostics.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__': run()
