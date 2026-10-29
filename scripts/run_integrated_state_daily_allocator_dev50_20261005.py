#!/usr/bin/env python3
import json, math
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq, yfinance as yf

ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
PRED=Path('/home/ubuntu/mts-v4-nexus-derived-market-current-sp500-calibration-20260915-RECONSTRUCTED-CLEAN/data/sp500-current-sp500-calibration-20260915__a0dd6a1a76bb/mts_market_predictors_v2__3e9bdc71246a/predictor-v2-initial-20260929-predictors-2005-09-14-2026-09-14.parquet')
# tolerate actual reconstructed path
if not PRED.exists():
 PRED=Path('/home/ubuntu/mts-v4-nexus-derived-market-current-sp500-calibration-20260915-RECONSTRUCTED-CLEAN/data/sp500-current-calibration-20260915__a0dd6a1a76bb/mts_market_predictors_v2__3e9bdc71246a/predictor-v2-initial-20260929-predictors-2005-09-14-2026-09-14.parquet')
RF=ROOT/'Research/Data/RiskFree/FRED_DGS3MO_20261005.csv'
OUT=ROOT/'Research/Reports/MTS_DAILY_COMPETITIVE_CAPITAL_ALLOCATION_DEV50_INTEGRATED_STATE_20261005.json'
DEV=sorted("AMGN CI MPC STLD EXC CFG AJG NUE KKR TDG PPG TRV RL CTSH T FIS NOW SBAC SMCI KDP COST OMC NKE RSG ROK SO XEL DECK TRGP WELL CDW ITW DHI IRM COIN TPL FANG HWM NFLX BEN BNY BLDR EVRG GILD MCO TECH CLX PCAR COO FITB".split())
W=[('GFC','2007-11-20','2009-03-30'),('2011','2011-06-13','2011-10-24'),('2015_16','2015-07-06','2016-03-04'),('2018','2018-11-14','2019-01-16'),('COVID','2020-04-01','2020-04-14'),('2022','2022-02-15','2022-11-02')]
SF=['stock_ret5','stock_ret20','stock_close_sma20','stock_range20','stock_rsi14','stock_relvol_pct','stock_drawdown252','stock_rv_pct']
cols=['security_id','effective_date','eligible','return_5__v1','return_20__v1','close_to_sma_20__v1','range_position_20__v1','rsi_14__v1','relative_volume_20_percentile__v1','drawdown_252__v1','realized_vol_20_percentile__v1']
ren={'return_5__v1':'stock_ret5','return_20__v1':'stock_ret20','close_to_sma_20__v1':'stock_close_sma20','range_position_20__v1':'stock_range20','rsi_14__v1':'stock_rsi14','relative_volume_20_percentile__v1':'stock_relvol_pct','drawdown_252__v1':'stock_drawdown252','realized_vol_20_percentile__v1':'stock_rv_pct'}
print('LOAD_PREDICTORS',flush=True)
p=pq.read_table(PRED,columns=cols).to_pandas().rename(columns=ren)
p['date']=pd.to_datetime(p.effective_date).dt.tz_localize(None); p['ticker']=p.security_id.astype(str).str.rsplit('_',n=1).str[-1]
p=p[p.eligible.fillna(False)&p.ticker.isin(DEV)][['ticker','date']+SF].replace([np.inf,-np.inf],np.nan)
print('DOWNLOAD_PRICES',flush=True)
px=yf.download(DEV,start='2007-01-01',end='2023-02-01',auto_adjust=True,progress=False,threads=True)
O=px['Open']; dates=O.index
# decision at close t -> next open t+1 entry; daily holding return open t+1 -> open t+2
nextret=O.shift(-2)/O.shift(-1)-1
long=[]
for t in DEV:
 if t not in nextret: continue
 q=pd.DataFrame({'date':nextret.index,'ticker':t,'y':nextret[t].values})
 long.append(q)
y=pd.concat(long,ignore_index=True)
p=p.merge(y,on=['ticker','date'],how='left').dropna(subset=SF+['y']).sort_values(['date','ticker'])
# Integrated causal state tape replaces hand-cut crash windows.
st=pd.read_csv(ROOT/'Research/State/MTS_ABC_DEFENSIVE_R1_STATE_TAPE_20261005.csv')
st['date']=pd.to_datetime(st.date)
st=st[st.state.eq('DEFENSIVE')][['date','defensive_source']]
p=p.merge(st,on='date',how='inner')
# each causal Defensive entry-to-R1 interval is an episode
fullst=pd.read_csv(ROOT/'Research/State/MTS_ABC_DEFENSIVE_R1_STATE_TAPE_20261005.csv')
fullst['date']=pd.to_datetime(fullst.date)
fullst['episode']=(fullst.entry.fillna(False).astype(bool)).cumsum()-1
p=p.merge(fullst[['date','episode']],on='date',how='left')
W=[]
rf=pd.read_csv(RF); rf['observation_date']=pd.to_datetime(rf.observation_date); rf['DGS3MO']=pd.to_numeric(rf.DGS3MO,errors='coerce')
rfs=rf.set_index('observation_date').DGS3MO.sort_index().reindex(pd.date_range('2007-01-01','2023-02-01')).ffill()/100/252
p['safe']=p.date.map(lambda d: float(rfs.asof(d)) if d>=rfs.index.min() else 0.0)
p['excess_y']=p.y-p.safe
fold={t:i%5 for i,t in enumerate(DEV)}
GRID=[(q,m) for q in [0.50,0.60,0.70,0.80] for m in [0.0,0.0005,0.001,0.002]]
FRICTION=.0005
results=[]
for f in range(5):
 print('FOLD',f,flush=True)
 tr=p[p.ticker.map(fold).ne(f)].copy(); te=p[p.ticker.map(fold).eq(f)].copy()
 # strict causal expanding model: monthly refit using only observations whose next-day outcome is already known
 preds=[]
 months=sorted(te.date.dt.to_period('M').unique())
 for mi,mo in enumerate(months):
  start=mo.start_time
  hist=tr[tr.date < start-pd.Timedelta(days=2)]
  cur=te[te.date.dt.to_period('M').eq(mo)]
  if len(hist)<1000 or cur.empty: continue
  mu=hist[SF].mean(); sd=hist[SF].std().replace(0,1); X=((hist[SF]-mu)/sd).to_numpy(float); yy=hist.excess_y.to_numpy(float); beta=np.linalg.solve(X.T@X+10.0*np.eye(X.shape[1]),X.T@yy)
  z=cur.copy(); z['score']=((cur[SF]-mu)/sd).to_numpy(float)@beta; preds.append(z)
  if mi%6==0: print('FOLD',f,'MONTH',str(mo),'TRAIN',len(hist),'TEST',len(cur),flush=True)
 te=pd.concat(preds,ignore_index=True) if preds else te.iloc[0:0].assign(score=[])
 # choose policy on training via causal OOS monthly predictions inside training, using first 80% time for fit->later validation
 cut=tr.date.quantile(.70); fit=tr[tr.date<cut]; val=tr[tr.date>=cut].copy()
 mu=fit[SF].mean(); sd=fit[SF].std().replace(0,1); X=((fit[SF]-mu)/sd).to_numpy(float); yy=fit.excess_y.to_numpy(float); beta=np.linalg.solve(X.T@X+10.0*np.eye(X.shape[1]),X.T@yy); val['score']=((val[SF]-mu)/sd).to_numpy(float)@beta
 best=None
 for q,margin in GRID:
  thresh=float(val.score.quantile(q))
  sel=val[val.score>=max(thresh,margin)]
  if sel.empty: continue
  daily=sel.groupby('date').apply(lambda x:x.nlargest(5,'score').excess_y.mean(),include_groups=False)
  metric=float(daily.mean())-0.25*float(daily[daily<0].std() if (daily<0).any() else 0)
  if best is None or metric>best[0]: best=(metric,q,margin,thresh)
 _,q,margin,_=best
 # heldout daily portfolio: retain/replace is equivalent to daily auction because no hold/cooldown; top 5 positive-EV candidates vs SAFE
 wealth=100000.; peak=wealth; mdd=0.; switches=0; prev=set(); dayrows=[]; ticker_pnl={}
 for d,g in te.groupby('date'):
  th=float(g.score.quantile(q)); chosen=g[g.score>=np.maximum(th,margin)].nlargest(5,'score')
  names=set(chosen.ticker)
  switches += len(names-prev); prev=names
  if len(chosen): r=float(chosen.y.mean())-FRICTION*len(names-prev)/max(1,len(chosen))
  else: r=float(g.safe.iloc[0])
  before=wealth; wealth*=1+r; pnl=wealth-before
  if len(chosen):
   for t in chosen.ticker: ticker_pnl[t]=ticker_pnl.get(t,0)+pnl/len(chosen)
  peak=max(peak,wealth); mdd=min(mdd,wealth/peak-1)
  dayrows.append((d,r,len(chosen)))
 yrs=(max(te.date)-min(te.date)).days/365.25 if len(te) else 0
 cagr=(wealth/100000.)**(1/yrs)-1 if yrs>0 else 0
 byep={}
 for e in sorted(te.episode.dropna().unique()):
  ds=set(te.loc[te.episode.eq(e),'date'])
  rr=[x[1] for x in dayrows if x[0] in ds]
  if rr: byep[str(int(e))]={'sessions':len(rr),'return':float(np.prod(np.array(rr)+1)-1)}
 pos=sum(v for v in ticker_pnl.values() if v>0); conc=max([v/pos for v in ticker_pnl.values() if v>0],default=0)
 results.append({'fold':f,'policy':{'score':'causal_ridge_expected_next_session_excess_return','quantile':q,'minimum_excess_score':margin,'slots':5,'min_hold':0,'max_hold':None,'cooldown':0},'terminal_wealth':wealth,'cagr':cagr,'max_drawdown':mdd,'switch_entries':switches,'positive_pnl_ticker_max_share':conc,'episodes':byep,'sessions':len(dayrows)})
 print('FOLD_RESULT',f,'WEALTH',round(wealth,2),'CAGR',round(cagr,4),'MDD',round(mdd,4),flush=True)
out={'format':'MTS_DAILY_COMPETITIVE_CAPITAL_ALLOCATION_DEV50_INTEGRATED_STATE_V1','status':'DEV50_INTEGRATED_STATE_COMPLETE','provenance':'NEW_RESEARCH_POST_RECOVERY','note':'Integrated causal A/B/C->DEFENSIVE->R1 state-defined replay. Historical six-window baseline preserved separately.','fixed_holding_horizon':False,'friction_one_way':FRICTION,'results':results,'preserved50_accessed':False,'test17_accessed':False,'protected_accessed':False}
OUT.write_text(json.dumps(out,indent=2,default=str)+'\n')
print('WROTE',OUT,flush=True)
