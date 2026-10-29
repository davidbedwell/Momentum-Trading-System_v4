#!/usr/bin/env python3
from pathlib import Path
import json, numpy as np, pandas as pd, yfinance as yf, runpy
ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
OUTCSV=ROOT/'Research/State/MTS_ABC_DEFENSIVE_R1_STATE_TAPE_20261005.csv'
OUTJSON=ROOT/'Research/Reports/MTS_ABC_DEFENSIVE_R1_STATE_TAPE_AUDIT_20261005.json'
OUTCSV.parent.mkdir(parents=True,exist_ok=True)

ns=runpy.run_path(str(ROOT/'scripts/run_path_a_2020_failure_autopsy_20261004.py'))
g=ns['g'].copy(); rp=ns['rolling_pct']
# Add SPY causal price-path features used by surviving B/C specifications.
spy=yf.download('SPY',start=str(g.index.min().date()),end='2026-09-16',auto_adjust=True,progress=False)
if isinstance(spy.columns,pd.MultiIndex): spy.columns=spy.columns.get_level_values(0)
c=spy['Close'].reindex(g.index).ffill()
r1=c.pct_change(); r5=c.pct_change(5)
g['negfrac20']=(r1<0).rolling(20,min_periods=20).mean()
g['negfrac40']=(r1<0).rolling(40,min_periods=40).mean()
g['failed30']=((r5<=0)&(g.dd<-0.05)).rolling(30,min_periods=30).mean()
g['fundingchg20']=g.funding-g.funding.shift(20)
g['fundingchg30']=g.funding-g.funding.shift(30)
for col in ['negfrac20','negfrac40','failed30','fundingchg20','fundingchg30']:
    g[col+'_pct']=rp(g[col])

# A: strict rapid systemic concurrence, frozen 95th/4-of-4/5.
Araw=(g.funding_pct>=.95)&(rp(-g.dd)>=.95)&(g.vvix_pct>=.95)&(g.b20_badpct>=.95)
g['A']=Araw.rolling(5,min_periods=5).sum().ge(5)
# B: surviving slow-bear two-domain rule.
Braw=(g.negfrac40_pct>=.85)&(g.fundingchg20_pct>=.85)
g['B']=Braw.rolling(3,min_periods=3).sum().ge(3)
# C: strict 4-domain rule.
Craw=(g.negfrac20_pct>=.90)&(g.failed30_pct>=.90)&(g.negfrac40_pct>=.90)&(g.fundingchg30_pct>=.90)
g['C']=Craw.rolling(3,min_periods=3).sum().ge(3)
# conservative R1 recovery evidence.
Rraw=(g.negfrac20_pct<.50)&(g.failed30_pct<.50)&(g.negfrac40_pct<.50)&(g.fundingchg30_pct<.50)
g['R1_evidence']=Rraw.rolling(3,min_periods=3).sum().ge(3)

state=[]; entered_by=[]; current='NORMAL'; src=''
for d,row in g.iterrows():
    if current=='NORMAL':
        hits=[k for k in ['A','B','C'] if bool(row[k])]
        if hits:
            current='DEFENSIVE'; src='+'.join(hits)
    elif current=='DEFENSIVE':
        if bool(row.R1_evidence):
            current='NORMAL'; src=''
    state.append(current); entered_by.append(src)
g['state']=state; g['defensive_source']=entered_by
# transition markers
g['entry']=(g.state.eq('DEFENSIVE')&g.state.shift(1).ne('DEFENSIVE'))
g['r1']=(g.state.eq('NORMAL')&g.state.shift(1).eq('DEFENSIVE'))

cols=['A','B','C','R1_evidence','state','defensive_source','entry','r1','negfrac20_pct','failed30_pct','negfrac40_pct','fundingchg30_pct','funding_pct','vvix_pct','b20_badpct']
g[cols].to_csv(OUTCSV,index_label='date')
entries=[{'date':str(d.date()),'source':g.loc[d,'defensive_source']} for d in g.index[g.entry]]
exits=[str(d.date()) for d in g.index[g.r1]]
audit={'format':'MTS_ABC_DEFENSIVE_R1_STATE_TAPE_AUDIT_V1','entries':entries,'r1_exits':exits,'defensive_sessions':int(g.state.eq('DEFENSIVE').sum()),'normal_sessions':int(g.state.eq('NORMAL').sum()),'date_start':str(g.index.min().date()),'date_end':str(g.index.max().date()),'protected_accessed':False,'preserved50_accessed':False,'test17_accessed':False}
OUTJSON.write_text(json.dumps(audit,indent=2)+'\n')
print('STATE_TAPE',OUTCSV)
print('AUDIT',OUTJSON)
print('ENTRIES',entries)
print('R1_EXITS',exits)
print('DEFENSIVE_SESSIONS',audit['defensive_sessions'])
