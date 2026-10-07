#!/usr/bin/env python3
from layered_stage_common_20261007 import *
bank=load_bank();c=max(bank,key=lambda x:x['transport_ev']);daily=[]
for p in ROOT.glob('*.parquet'):
 d=frame(p.stem);m=mask(d,c);sg=1 if c['direction']=='LONG' else -1
 z=pd.DataFrame({'date':d.date,'r':sg*d.ret1.shift(-1),'m':m});daily.append(z[z.m][['date','r']])
z=pd.concat(daily).dropna();r=z.groupby('date').r.mean().sort_index().clip(lower=-.25,upper=.25);eq=(1+r).cumprod();yrs=max(1,(r.index.max()-r.index.min()).days/365.25);cagr=float(eq.iloc[-1]**(1/yrs)-1);dd=eq/eq.cummax()-1
write(10,'report-card',{'representative_frozen_opportunity':c,'diagnostic_equal_event_daily_cagr':cagr,'diagnostic_mdd':float(dd.min()),'terminal_multiple':float(eq.iloc[-1]),'worst_day':float(r.min()),'days':len(r),'warning':'Diagnostic report-card projection, not a deployable portfolio claim; full lifecycle/capital/cost assembly remains governed by frozen layer findings.'})
