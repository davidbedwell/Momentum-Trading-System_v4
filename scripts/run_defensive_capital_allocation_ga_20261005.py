#!/usr/bin/env python3
import json, random, math
from pathlib import Path
import numpy as np, pandas as pd
import pyarrow.parquet as pq
import yfinance as yf
ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
PRED=Path('/home/ubuntu/mts-v4-nexus-derived-market-current-sp500-calibration-20260915-RECONSTRUCTED-CLEAN/data/sp500-current-calibration-20260915__a0dd6a1a76bb/mts_market_predictors_v2__3e9bdc71246a/predictor-v2-initial-20260929-predictors-2005-09-14-2026-09-14.parquet')
RF=ROOT/'Research/Data/RiskFree/FRED_DGS3MO_20261005.csv'
OUT=ROOT/'Research/Reports/MTS_DEFENSIVE_CAPITAL_ALLOCATION_DEV50_20261005.json'
DEV=sorted("AMGN CI MPC STLD EXC CFG AJG NUE KKR TDG PPG TRV RL CTSH T FIS NOW SBAC SMCI KDP COST OMC NKE RSG ROK SO XEL DECK TRGP WELL CDW ITW DHI IRM COIN TPL FANG HWM NFLX BEN BNY BLDR EVRG GILD MCO TECH CLX PCAR COO FITB".split())
WINDOWS=[('GFC','2007-11-20','2009-03-30'),('2011','2011-06-13','2011-10-24'),('2015_16','2015-07-06','2016-03-04'),('2018','2018-11-14','2019-01-16'),('COVID','2020-04-01','2020-04-14'),('2022','2022-02-15','2022-11-02')]
ACTIONS=['LONG_SECURITY','SHORT_SECURITY','LONG_MARKET','SHORT_MARKET']; HOLDS=[3,5,10,20]; Q=[.2,.35,.65,.8]
SF=['stock_ret5','stock_ret20','stock_close_sma20','stock_range20','stock_rsi14','stock_relvol_pct','stock_drawdown252','stock_rv_pct']
MF=['market_ret5','market_ret20','market_drawdown252','breadth_above_sma200','breadth_positive20','market_rv_pct','vix','vvix','ofr_funding_lag2','ofr_credit_lag2']
ALL=SF+MF
# predictors
cols=['security_id','effective_date','eligible','return_5__v1','return_20__v1','close_to_sma_20__v1','range_position_20__v1','rsi_14__v1','relative_volume_20_percentile__v1','drawdown_252__v1','realized_vol_20_percentile__v1','breadth_above_sma_200__v1','breadth_positive_20__v1']
p=pq.read_table(PRED,columns=cols).to_pandas(); p['date']=pd.to_datetime(p.effective_date).dt.tz_localize(None); p['ticker']=p.security_id.astype(str).str.rsplit('_',n=1).str[-1]; p=p[p.eligible.fillna(False)]
rename={'return_5__v1':'stock_ret5','return_20__v1':'stock_ret20','close_to_sma_20__v1':'stock_close_sma20','range_position_20__v1':'stock_range20','rsi_14__v1':'stock_rsi14','relative_volume_20_percentile__v1':'stock_relvol_pct','drawdown_252__v1':'stock_drawdown252','realized_vol_20_percentile__v1':'stock_rv_pct'}; p=p.rename(columns=rename)
m=p.groupby('date').agg(market_ret5=('stock_ret5','median'),market_ret20=('stock_ret20','median'),market_drawdown252=('stock_drawdown252','median'),breadth_above_sma200=('breadth_above_sma_200__v1','median'),breadth_positive20=('breadth_positive_20__v1','median'),market_rv_pct=('stock_rv_pct','median')).sort_index()
# external causal features
v=pd.read_csv(ROOT/'Research/Data/CrashMultiMarketV1/VIX_History.csv'); v['date']=pd.to_datetime(v.DATE,format='%m/%d/%Y'); m['vix']=v.set_index('date').CLOSE.astype(float).reindex(m.index).ffill()
vv=pd.read_csv(ROOT/'Research/Data/CrashMultiMarketV1/VVIX_History.csv'); vv['date']=pd.to_datetime(vv.DATE,format='%m/%d/%Y'); m['vvix']=vv.set_index('date').VVIX.astype(float).reindex(m.index).ffill()
ofr=pd.read_csv(ROOT/'Research/Data/CrashCausalPackV1/ofr_fsi_raw_20261004.csv'); ofr['date']=pd.to_datetime(ofr.Date); ofr=ofr.set_index('date')[['Funding','Credit']].astype(float).sort_index().shift(2).reindex(m.index).ffill(); m['ofr_funding_lag2']=ofr.Funding; m['ofr_credit_lag2']=ofr.Credit
p=p[p.ticker.isin(DEV)][['ticker','date']+SF].merge(m.reset_index()[['date']+MF],on='date',how='left')
# only research windows
def ep(d):
 for i,(n,a,b) in enumerate(WINDOWS):
  if pd.Timestamp(a)<=d<=pd.Timestamp(b): return i
 return -1
p['episode']=p.date.map(ep); p=p[p.episode>=0].copy()
# prices direct from Yahoo, not optimized candidate cache
px=yf.download(DEV+['SPY'],start='2007-11-01',end='2023-01-01',auto_adjust=True,progress=False,threads=True)
O=px['Open']; C=px['Close']; dates=list(C.index); pos={d:i for i,d in enumerate(dates)}
rf=pd.read_csv(RF); rf['observation_date']=pd.to_datetime(rf.observation_date); rf['DGS3MO']=pd.to_numeric(rf.DGS3MO,errors='coerce'); rfs=rf.set_index('observation_date').DGS3MO.reindex(pd.date_range(dates[0],dates[-1],freq='D')).ffill()
# build rows with forward economics for each hold/action
rows=[]
for r in p.itertuples(index=False):
 d=r.date
 if d not in pos: continue
 i=pos[d]
 for h in HOLDS:
  if i+1>=len(dates) or i+h>=len(dates): continue
  en=dates[i+1]; ex=dates[i+h]
  vals={k:getattr(r,k) for k in ALL}; base={'ticker':r.ticker,'date':d,'episode':int(r.episode),'hold':h,**vals}
  for market,tick in [(False,r.ticker),(True,'SPY')]:
   try: entry=float(O.loc[en,tick]); exit=float(C.loc[ex,tick])
   except: continue
   if not(np.isfinite(entry) and np.isfinite(exit) and entry>0): continue
   days=(ex-en).days+1; rate=float(rfs.loc[en])/100; safe=rate*days/365.0
   lr=exit/entry-1-.001; sr=(entry-exit)/entry-.001
   if not market: rows += [{**base,'action':'LONG_SECURITY','excess':lr-safe},{**base,'action':'SHORT_SECURITY','excess':sr-safe}]
   elif r.ticker==DEV[0]: rows += [{**base,'ticker':'SPY','action':'LONG_MARKET','excess':lr-safe},{**base,'ticker':'SPY','action':'SHORT_MARKET','excess':sr-safe}]
df=pd.DataFrame(rows).replace([np.inf,-np.inf],np.nan)
print('ROWS',len(df),'DATES',df.date.nunique(),'TICKERS',df[df.action.str.contains('SECURITY')].ticker.nunique(),flush=True)
fold={t:i%5 for i,t in enumerate(DEV)}
POP=140; GEN=14; ELITE=28

def search(action,train,test,seed):
 R=random.Random(seed); feats=ALL if 'SECURITY' in action else MF; tr=df[(df.action==action)&train(df)].copy(); te=df[(df.action==action)&test(df)].copy()
 thresholds={f:{q:float(tr[f].quantile(q)) for q in Q} for f in feats}
 def randg():
  n=R.choice([1,1,2,2,3]); fs=R.sample(feats,n); return {'hold':R.choice(HOLDS),'conds':[(f,R.choice(Q),R.choice(['>=','<='])) for f in fs]}
 def mut(g):
  z={'hold':g['hold'],'conds':list(g['conds'])}; k=R.randrange(4)
  if k==0:z['hold']=R.choice(HOLDS)
  elif k==1:
   j=R.randrange(len(z['conds'])); f,q,di=z['conds'][j]; z['conds'][j]=(R.choice(feats),q,di)
  elif k==2:
   j=R.randrange(len(z['conds'])); f,q,di=z['conds'][j]; z['conds'][j]=(f,R.choice(Q),di)
  else:
   if len(z['conds'])<3 and R.random()<.5:z['conds'].append((R.choice(feats),R.choice(Q),R.choice(['>=','<='])))
   elif len(z['conds'])>1:z['conds'].pop(R.randrange(len(z['conds'])))
   else:
    j=0; f,q,di=z['conds'][j]; z['conds'][j]=(f,q,'<=' if di=='>=' else '>=')
  # dedupe feature conditions to avoid gratuitous degrees
  seen=set(); z['conds']=[c for c in z['conds'] if not(c[0] in seen or seen.add(c[0]))]; return z
 def select(x,g):
  y=x[x.hold==g['hold']]
  for f,q,di in g['conds']:
   th=thresholds[f][q]; y=y[y[f]>=th] if di=='>=' else y[y[f]<=th]
  return y
 def metrics(y):
  if y.empty:return None
  dd=y.groupby('date').excess.mean(); ee=y.groupby('episode').excess.mean()
  return {'date_mean':float(dd.mean()),'date_win':float((dd>0).mean()),'date_downside':float(dd[dd<0].mean()) if (dd<0).any() else 0.0,'worst_date':float(dd.min()),'episode_mean':float(ee.mean()),'worst_episode':float(ee.min()),'dates':int(len(dd)),'episodes':int(len(ee)),'rows':int(len(y)),'tickers':int(y.ticker.nunique())}
 def ev(g):
  y=select(tr,g); z=metrics(y)
  if z is None or z['dates']<20 or z['episodes']<3:return -999,None
  # date/episode evidence; complexity and downside penalties; row count absent.
  score=5*z['date_mean']+5*z['episode_mean']+2*min(0,z['worst_episode'])+1*min(0,z['date_downside'])-.003*(len(g['conds'])-1)
  return score,z
 pop=[randg() for _ in range(POP)]; best=None
 for ge in range(GEN):
  vals=[]
  for g in pop:
   sc,me=ev(g); vals.append((sc,g,me))
  vals.sort(key=lambda x:x[0],reverse=True)
  if best is None or vals[0][0]>best[0]:best=vals[0]
  print(action,'GEN',ge,'SCORE',round(best[0],6),'DATES',best[2]['dates'] if best[2] else 0,flush=True)
  elites=[x[1] for x in vals[:ELITE]]; pop=list(elites)
  while len(pop)<POP:pop.append(mut(R.choice(elites[:14])))
 g=best[1]; held=metrics(select(te,g)); return {'action':action,'genome':g,'thresholds_used':[{**{'feature':f,'quantile':q,'direction':di},'threshold':thresholds[f][q]} for f,q,di in g['conds']],'train':best[2],'heldout':held}
results=[]; seed=2026100500
for f in range(5):
 for ai,a in enumerate(ACTIONS):
  results.append({'outer':'STOCK_'+str(f),**search(a,lambda x,f=f:~x.ticker.map(fold).eq(f),lambda x,f=f:x.ticker.map(fold).eq(f),seed+f*10+ai)})
for e,(name,_,_) in enumerate(WINDOWS):
 for ai,a in enumerate(ACTIONS):
  results.append({'outer':'EPISODE_'+name,**search(a,lambda x,e=e:x.episode.ne(e),lambda x,e=e:x.episode.eq(e),seed+100+e*10+ai)})
out={'format':'MTS_DEFENSIVE_CAPITAL_ALLOCATION_DEV50_V1','status':'DEV50_NESTED_COMPLETE','safe_proxy':'DGS3MO','actions':ACTIONS+['SAFE'],'results':results,'preserved50_accessed':False,'test17_accessed':False,'protected_accessed':False}
OUT.write_text(json.dumps(out,indent=2)); print('WROTE',OUT,flush=True)
for z in results:
 h=z['heldout']; print('FINAL',z['outer'],z['action'],'HELD',None if h is None else (round(100*h['date_mean'],3),h['dates'],round(100*h['date_win'],1),h['episodes']),flush=True)
