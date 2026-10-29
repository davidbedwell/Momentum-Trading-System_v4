from pathlib import Path
import json, pandas as pd, numpy as np

ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
PRED=Path('/home/ubuntu/mts-v4-nexus-derived-market-current-sp500-calibration-20260915-RECONSTRUCTED-CLEAN/data/sp500-current-calibration-20260915__a0dd6a1a76bb/mts_market_predictors_v2__3e9bdc71246a/predictor-v2-initial-20260929-predictors-2005-09-14-2026-09-14.parquet')
OUT=ROOT/'Research/Reports/MTS_PATH_A_2020_FAILURE_AUTOPSY_20261004.json'
TRACE=ROOT/'Research/Reports/MTS_PATH_A_2020_DAILY_TRACE_RECONSTRUCTED_20261004.csv'

def rolling_pct(s,w=252,minp=126):
    return s.rolling(w,min_periods=minp).rank(pct=True)

# Reconstructed market-wide daily tape from reconstructed predictor-v2 panel.
cols=['effective_date','eligible','breadth_above_sma_200__v1','breadth_positive_20__v1',
      'advance_decline_breadth__v1','drawdown_252__v1','return_5__v1']
x=pd.read_parquet(PRED,columns=cols)
x['date']=pd.to_datetime(x.effective_date)
x=x[x.eligible].copy()
g=x.groupby('date').agg(
    n=('eligible','size'),
    b200=('breadth_above_sma_200__v1','median'),
    b20=('breadth_positive_20__v1','median'),
    adv=('advance_decline_breadth__v1','median'),
    dd=('drawdown_252__v1','median'),
    shock5=('return_5__v1','median')).sort_index()

# VIX/VVIX originals recovered.
v=pd.read_csv(ROOT/'Research/Data/CrashMultiMarketV1/VIX_History.csv')
v['date']=pd.to_datetime(v.DATE); v=v.set_index('date').sort_index()
g['vix']=v['CLOSE']
vv=pd.read_csv(ROOT/'Research/Data/CrashMultiMarketV1/VVIX_History.csv')
vv['date']=pd.to_datetime(vv.DATE); vv=vv.set_index('date').sort_index()
g['vvix']=vv['VVIX']

# OFR raw original recovered; apply frozen 2-observation/business-day lag.
o=pd.read_csv(ROOT/'Research/Data/CrashCausalPackV1/ofr_fsi_raw_20261004.csv')
datecol=[c for c in o.columns if c.lower() in ('date','datetime')][0]
o['date']=pd.to_datetime(o[datecol]); o=o.set_index('date').sort_index()
for c,nm in [('Funding','funding'),('Credit','credit')]:
    raw=o[c].astype(float)
    g[nm]=raw.reindex(g.index).ffill().shift(2)
    g[nm+'_d20']=g[nm]-g[nm].shift(20)
    g[nm+'_accel']=((g[nm]-g[nm].shift(5))/5)-((g[nm].shift(5)-g[nm].shift(20))/15)

# Causal percentiles. Bad breadth / negative shock / negative drawdown are sign-inverted.
features=['vix','vvix','funding','funding_d20','funding_accel','credit','credit_d20','credit_accel']
for c in features: g[c+'_pct']=rolling_pct(g[c])
for c in ['b20','b200','adv','dd','shock5']: g[c+'_badpct']=rolling_pct(-g[c])

# Mechanistic components: shock evidence and later systemic confirmation.
g['shock_extreme']=((g.vix_pct>=.95)|(g.vvix_pct>=.95)|(g.b20_badpct>=.95)|(g.shock5_badpct>=.95))
g['systemic_confirm']=((g.funding_d20_pct>=.90)|(g.funding_accel_pct>=.90)|(g.credit_d20_pct>=.90)|(g.credit_accel_pct>=.90))

episodes={'2008':(pd.Timestamp('2007-10-09'),pd.Timestamp('2009-03-09')),'2020':(pd.Timestamp('2020-02-19'),pd.Timestamp('2020-03-23')),'2022':(pd.Timestamp('2022-01-03'),pd.Timestamp('2022-10-12'))}
control=(pd.Timestamp('2015-05-21'),pd.Timestamp('2016-02-11'))

def declarations(memory,confirm):
    armed=g.shock_extreme.rolling(memory,min_periods=1).max().astype(bool)
    raw=armed & g.systemic_confirm
    return raw.rolling(confirm,min_periods=confirm).sum().ge(confirm)

def first_in(s,a,b):
    z=s.loc[a:b]; z=z[z]
    return None if z.empty else z.index[0]

def false_episodes(s):
    mask=s.copy()
    for a,b in list(episodes.values())+[control]: mask.loc[a:b]=False
    starts=mask & ~mask.shift(1,fill_value=False)
    return [str(x.date()) for x in starts.index[starts]]

rows=[]
for memory in [1,2,3,5,8,10]:
  for confirm in [1,2,3,5]:
    s=declarations(memory,confirm)
    r={'memory':memory,'confirm':confirm,'false_episode_count':len(false_episodes(s)),'false_episode_starts':false_episodes(s)}
    mask=s.copy()
    for a,b in list(episodes.values())+[control]: mask.loc[a:b]=False
    r['alert_days_outside']=int(mask.sum())
    for ep,(a,b) in episodes.items():
        dt=first_in(s,a,b)
        r[ep+'_date']=None if dt is None else str(dt.date())
        r[ep+'_delay']=None if dt is None else int(g.loc[a:dt].shape[0]-1)
    dt=first_in(s,*control)
    r['control2015_date']=None if dt is None else str(dt.date())
    rows.append(r)

ranked=sorted(rows,key=lambda r:(r['false_episode_count'],sum(r[e+'_date'] is None for e in episodes),r['2020_delay'] if r['2020_delay'] is not None else 999,r['memory'],r['confirm']))
tracecols=['n','b200','b20','adv','dd','shock5','vix','vvix','funding','funding_d20','funding_accel','credit','credit_d20','credit_accel','vix_pct','vvix_pct','b20_badpct','shock5_badpct','funding_d20_pct','funding_accel_pct','credit_d20_pct','credit_accel_pct','shock_extreme','systemic_confirm']
g.loc['2020-02-18':'2020-03-16',tracecols].to_csv(TRACE,index_label='date')
report={'format':'MTS_PATH_A_2020_FAILURE_AUTOPSY_V1','provenance':{'predictor_panel':'RECONSTRUCTED_FROM_SURVIVING_SPEC','VIX_VVIX':'ORIGINAL_RECOVERED','OFR_raw':'ORIGINAL_RECOVERED','analysis':'NEW_RESEARCH_POST_RECOVERY'},'optimization':False,'portfolio_fitness':False,'protected_evidence_access':False}
report['mechanism']='extreme fast-shock evidence arms a short causal state; independent funding/credit stress can confirm within memory window'
report['grid']={'memory_sessions':[1,2,3,5,8,10],'confirmation_sessions':[1,2,3,5]}
report['all_results']=rows
report['mechanistic_ranking_top10']=ranked[:10]
report['warning']='Exploratory post-recovery autopsy. No rule is frozen or advanced by this report.'
OUT.write_text(json.dumps(report,indent=2))
print('TRACE',TRACE)
print('REPORT',OUT)

for r in ranked[:12]:
    print(r['memory'],r['confirm'],'false',r['false_episode_count'],'days',r['alert_days_outside'],'2008',r['2008_date'],'2020',r['2020_date'],'delay',r['2020_delay'],'2022',r['2022_date'],'2015',r['control2015_date'])
