"""Causal cross-sectional ranking diagnostics, NOT a portfolio CAGR backtest.
No trading simulator or historical earnings embargo: only predictive label checks.
"""
import json,time
from pathlib import Path
import numpy as np,pandas as pd
R=Path('/opt/mts/ga6_h');t0=time.monotonic()
# Restrict baseline diagnostic to a pre-declared monthly sample of dates, avoid
# large in-memory wide 10m-row concatenation while GA6 remains active.
frames=[]
for path in sorted((R/'derived_v1').glob('*.parquet')):
    d=pd.read_parquet(path,columns=['date','symbol','eligible_signal','return_20','return_60','volatility_20','forward_adj_return_20'])
    dates=pd.to_datetime(d.date)
    # Monthly fixed calendar-day window: first five sessions in each month.
    month=dates.dt.to_period('M')
    take=month.ne(month.shift(1))
    d=d.loc[take & d.eligible_signal].copy()
    if len(d): frames.append(d)
print('LOADED',len(frames),'elapsed',round(time.monotonic()-t0,1),flush=True)
all_=pd.concat(frames,ignore_index=True)
all_['date']=pd.to_datetime(all_['date'])
all_=all_[(all_.date>='2018-01-01')&(all_.date<'2025-01-01')].dropna(subset=['return_20','forward_adj_return_20'])
all_['rank']=all_.groupby('date')['return_20'].rank(pct=True)
all_['rank60']=all_.groupby('date')['return_60'].rank(pct=True)
results={}
for year,g in all_.groupby(all_.date.dt.year):
    by_date=[]
    for day,h in g.groupby('date'):
        if len(h)<100:continue
        top=h.nlargest(max(1,int(len(h)*0.05)),'return_20')
        bottom=h.nsmallest(max(1,int(len(h)*0.05)),'return_20')
        by_date.append({'date':str(day.date()),'universe':len(h),'top_mean':float(top.forward_adj_return_20.mean()),
          'bottom_mean':float(bottom.forward_adj_return_20.mean()),'all_mean':float(h.forward_adj_return_20.mean()),
          'spearman':float(h['rank'].corr(h['forward_adj_return_20'],method='spearman'))})
    if by_date:
        b=pd.DataFrame(by_date)
        results[str(year)]={'months':len(b),'mean_universe':round(float(b.universe.mean()),1),
          'top_5pct_forward_20d':round(float(b.top_mean.mean()),5),
          'bottom_5pct_forward_20d':round(float(b.bottom_mean.mean()),5),
          'top_minus_bottom':round(float((b.top_mean-b.bottom_mean).mean()),5),
          'mean_rank_ic':round(float(b.spearman.mean()),5)}
report={'name':'DIAGNOSTIC_ONLY_20D_MOMENTUM','data_rows':len(all_),'years':results,'elapsed_seconds':round(time.monotonic()-t0,1),
 'limitations':['Survivor-only 2026 current-listed universe','Unadjusted for transaction costs, earnings embargo, liquidity, and portfolio constraints','Forward 20-session adjusted close returns are labels, not executable next-open returns','Monthly first-session sampling, not an evolutionary GA or full walk-forward test']}
(R/'audits/ranking_baseline_v1.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
