#!/usr/bin/env python3
import argparse, json, math, os, random, time, hashlib, gzip, pickle
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
PRED=Path('/home/ubuntu/mts-v4-nexus-derived-market-current-sp500-calibration-20260915-RECONSTRUCTED-CLEAN/data/sp500-current-calibration-20260915__a0dd6a1a76bb/mts_market_predictors_v2__3e9bdc71246a/predictor-v2-initial-20260929-predictors-2005-09-14-2026-09-14.parquet')
PXDIR=Path('/home/ubuntu/mts-v4-market-store-RECONSTRUCTED-20261004/raw_yfinance')
CACHE67=Path('/home/ubuntu/mts-v4-cache/discovery_research_population_v1.RECONSTRUCTED.pkl.gz')
H50=ROOT/'Research/Protocols/MTS_HELDOUT_TICKER_WALKFORWARD_COHORT_20261002.json'
RF=ROOT/'Research/Data/RiskFree/FRED_DGS3MO_20261005.csv'
FREEZE=ROOT/'Research/Protocols/MTS_HORIZON_FREE_GA_FINAL_STUDY_FREEZE_20261005.json'
OUT=ROOT/'Research/Reports/MTS_FROZEN_ARCH_GA_V2_20261005.json'
CHECK=ROOT/'Research/Reports/MTS_FROZEN_ARCH_GA_V2_CHECKPOINT_20261005.json'
LOG=ROOT/'Research/Logs/MTS_FROZEN_ARCH_GA_V2_20261005.log'
STATE=ROOT/'Research/State/MTS_FROZEN_ARCH_GA_V2_INPUT_MANIFEST_20261005.json'
SEED=20261005
ERAS=[('E1','2006-09-15','2011-09-14'),('E2','2011-09-15','2016-09-14'),('E3','2016-09-15','2021-09-14'),('E4','2021-09-15','2026-09-14')]
DD_BANDS=[.10,.15,.20,.25,.30,.35,.40]

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()

def load_dev117():
 with gzip.open(CACHE67,'rb') as f: x=pickle.load(f)
 d67=sorted({r['ticker'] for r in x['rows']})
 h=json.load(open(H50)); d50=sorted({r['ticker'] for r in h['primary']})
 assert len(d67)==67 and len(d50)==50 and not(set(d67)&set(d50))
 return d67,d50,sorted(d67+d50)

def load_prices(tickers):
 frames={}
 missing=[]
 for t in tickers:
  p=PXDIR/f'{t}.parquet'
  if not p.exists(): missing.append(t); continue
  d=pd.read_parquet(p)
  d.columns=[str(c).lower() for c in d.columns]
  dc='date' if 'date' in d.columns else d.columns[0]
  d[dc]=pd.to_datetime(d[dc]).dt.tz_localize(None)
  d=d.set_index(dc).sort_index()
  cc='close' if 'close' in d.columns else 'adj close'
  frames[t]=pd.to_numeric(d[cc],errors='coerce')
 if missing: raise RuntimeError('missing local price files '+str(missing))
 px=pd.concat(frames,axis=1).sort_index()
 px=px.loc[(px.index>=pd.Timestamp('2005-09-14'))&(px.index<=pd.Timestamp('2026-09-14'))]
 return px

def load_panel(dev):
    # Frozen architecture V2: preserve distinct stock, sector and market information layers.
    cols=['security_id','effective_date','eligible',
          'return_5__v1','return_20__v1','return_63__v1','return_126__v1',
          'close_to_sma_20__v1','close_to_sma_50__v1','close_to_sma_200__v1',
          'sma20_slope_5__v1','sma50_slope_10__v1','range_position_20__v1',
          'rsi_14__v1','relative_volume_20_percentile__v1','drawdown_252__v1',
          'realized_vol_20_percentile__v1','relative_strength_change_20__v1',
          'volatility_ratio_20_63__v1','up_down_volume_balance_20__v1',
          'sector_vs_universe_return_63__v1','sector_return_252_percentile__v1',
          'breadth_above_sma_200__v1','breadth_positive_20__v1']
    p=pq.read_table(PRED,columns=cols).to_pandas()
    p['date']=pd.to_datetime(p.effective_date).dt.tz_localize(None)
    p['ticker']=p.security_id.astype(str).str.rsplit('_',n=1).str[-1]
    p=p[p.eligible.fillna(False)]
    ren={'return_5__v1':'ret5','return_20__v1':'ret20','return_63__v1':'ret63','return_126__v1':'ret126',
         'close_to_sma_20__v1':'sma20','close_to_sma_50__v1':'sma50','close_to_sma_200__v1':'sma200',
         'sma20_slope_5__v1':'sma20slope','sma50_slope_10__v1':'sma50slope','range_position_20__v1':'range20',
         'rsi_14__v1':'rsi14','relative_volume_20_percentile__v1':'relvol','drawdown_252__v1':'dd252',
         'realized_vol_20_percentile__v1':'rvpct','relative_strength_change_20__v1':'rschange',
         'volatility_ratio_20_63__v1':'volratio','up_down_volume_balance_20__v1':'uvbal',
         'sector_vs_universe_return_63__v1':'sector_rel63','sector_return_252_percentile__v1':'sector_ret252pct'}
    p=p.rename(columns=ren)
    market=p.groupby('date').agg(mret5=('ret5','median'),mret20=('ret20','median'),mdd=('dd252','median'),
        breadth200=('breadth_above_sma_200__v1','median'),breadth20=('breadth_positive_20__v1','median'),
        mrv=('rvpct','median')).sort_index()
    market['breadth_vel5']=market.breadth20-market.breadth20.shift(5)
    market['breadth_vel10']=market.breadth20-market.breadth20.shift(10)
    market['breadth_accel']=market.breadth_vel5-market.breadth_vel5.shift(5)
    market['breadth_persist']=market.breadth20.rolling(5,min_periods=3).mean()
    market['prior_destruction']=-market.mdd
    market['price_impulse']=market.mret5
    market['failed_rebound_reduction']=market.mret20-market.mret20.shift(5)
    market['short_trend_repair']=market.mret20-market.mret20.shift(10)
    v=pd.read_csv(ROOT/'Research/Data/CrashMultiMarketV1/VIX_History.csv'); v['date']=pd.to_datetime(v.DATE,format='%m/%d/%Y'); market['vix']=pd.to_numeric(v.set_index('date').CLOSE,errors='coerce').reindex(market.index).ffill()
    vv=pd.read_csv(ROOT/'Research/Data/CrashMultiMarketV1/VVIX_History.csv'); vv['date']=pd.to_datetime(vv.DATE,format='%m/%d/%Y'); market['vvix']=pd.to_numeric(vv.set_index('date').VVIX,errors='coerce').reindex(market.index).ffill()
    ofr=pd.read_csv(ROOT/'Research/Data/CrashCausalPackV1/ofr_fsi_raw_20261004.csv'); ofr['date']=pd.to_datetime(ofr.Date); ofr=ofr.set_index('date')[['Funding','Credit']].apply(pd.to_numeric,errors='coerce').sort_index().shift(2).reindex(market.index).ffill()
    market['funding']=ofr.Funding; market['credit']=ofr.Credit
    market['stress_norm']=-(market.vix.pct_change(5).replace([np.inf,-np.inf],np.nan).fillna(0)+market.vvix.pct_change(5).replace([np.inf,-np.inf],np.nan).fillna(0))/2
    market['recovery_retention']=market.mret20-market.mret20.rolling(20,min_periods=5).min()
    sf=['ret5','ret20','ret63','ret126','sma20','sma50','sma200','sma20slope','sma50slope','range20','rsi14','relvol','dd252','rvpct','rschange','volratio','uvbal']
    secf=['sector_rel63','sector_ret252pct']
    mf=['mret5','mret20','mdd','breadth200','breadth20','mrv','breadth_vel5','breadth_vel10','breadth_accel','breadth_persist','prior_destruction','price_impulse','failed_rebound_reduction','short_trend_repair','vix','vvix','funding','credit','stress_norm','recovery_retention']
    q=p[p.ticker.isin(dev)][['ticker','date']+sf+secf].merge(market.reset_index()[['date']+mf],on='date',how='left')
    return q,sf,secf,mf,market

def make_arrays(dev):
    px=load_prices(dev); panel,sf,secf,mf,market=load_panel(dev)
    dates=px.index.intersection(pd.Index(sorted(panel.date.unique())))
    dates=dates[(dates>=pd.Timestamp('2006-09-15'))&(dates<=pd.Timestamp('2026-09-14'))]
    T=len(dates); N=len(dev)
    ret=px[dev].reindex(dates).pct_change().shift(-1).to_numpy(dtype=np.float32)
    actual_ew=np.nanmean(ret,axis=1).astype(np.float32)  # explicitly NOT SPY
    p2=panel.set_index(['date','ticker'])
    raw_stock=np.full((T,N,len(sf)),np.nan,np.float32)
    raw_sec=np.full((T,N,len(secf)),np.nan,np.float32)
    raw_market=np.full((T,N,len(mf)),np.nan,np.float32)
    for j,t in enumerate(dev):
        z=p2.xs(t,level='ticker').reindex(dates)
        raw_stock[:,j,:]=z[sf].to_numpy(dtype=np.float32)
        raw_sec[:,j,:]=z[secf].to_numpy(dtype=np.float32)
        raw_market[:,j,:]=z[mf].to_numpy(dtype=np.float32)
    # Stock layer exposes BOTH cross-sectional and causal time-series state.
    xsr=np.full_like(raw_stock,np.nan)
    xts=np.full_like(raw_stock,np.nan)
    for k in range(len(sf)):
        a=raw_stock[:,:,k]; order=np.argsort(np.argsort(np.nan_to_num(a,nan=-1e30),axis=1),axis=1).astype(np.float32)
        valid=np.isfinite(a); den=np.maximum(valid.sum(1,keepdims=True)-1,1); rr=order/den; rr[~valid]=np.nan; xsr[:,:,k]=rr
        # Causal rolling z-normalization uses prior observations only; tanh maps to a stable 0..1 state.
        for j in range(N):
            ss=pd.Series(a[:,j],index=dates)
            mu=ss.shift(1).rolling(1260,min_periods=60).mean()
            sd=ss.shift(1).rolling(1260,min_periods=60).std().replace(0,np.nan)
            z=((ss-mu)/sd).clip(-6,6).fillna(0)
            xts[:,j,k]=(0.5+0.5*np.tanh(z.to_numpy()/2)).astype(np.float32)
    # Sector and market layers retain absolute time-varying causal state; they are NEVER cross-sectional-ranked away.
    def causal_norm(a):
        out=np.full_like(a,.5)
        for j in range(a.shape[1]):
            for k in range(a.shape[2]):
                ss=pd.Series(a[:,j,k],index=dates)
                mu=ss.shift(1).rolling(1260,min_periods=60).mean()
                sd=ss.shift(1).rolling(1260,min_periods=60).std().replace(0,np.nan)
                z=((ss-mu)/sd).clip(-6,6).fillna(0)
                out[:,j,k]=(0.5+0.5*np.tanh(z.to_numpy()/2)).astype(np.float32)
        return out
    sec=causal_norm(raw_sec)
    mkt=np.full_like(raw_market,.5)
    for k in range(len(mf)):
        ss=pd.Series(raw_market[:,0,k],index=dates)
        mu=ss.shift(1).rolling(1260,min_periods=60).mean()
        sd=ss.shift(1).rolling(1260,min_periods=60).std().replace(0,np.nan)
        z=((ss-mu)/sd).clip(-6,6).fillna(0)
        q=(0.5+0.5*np.tanh(z.to_numpy()/2)).astype(np.float32)
        mkt[:,:,k]=q[:,None]
    X=np.concatenate([xsr,xts,sec,mkt],axis=2)
    names=['xs:'+x for x in sf]+['ts:'+x for x in sf]+['sector:'+x for x in secf]+['market:'+x for x in mf]
    groups={'stock':list(range(0,2*len(sf))),
            'sector':list(range(2*len(sf),2*len(sf)+len(secf))),
            'market':list(range(2*len(sf)+len(secf),len(names)))}
    rf=pd.read_csv(RF); rf['observation_date']=pd.to_datetime(rf.observation_date); rf['DGS3MO']=pd.to_numeric(rf.DGS3MO,errors='coerce')
    rfd=rf.set_index('observation_date').DGS3MO.reindex(dates).ffill().fillna(0).to_numpy(dtype=np.float32)/100/252
    return dates,np.asarray(dev),X,ret,actual_ew,rfd,names,groups

def folds(dev):
 # four predetermined rotations; each has 37 blind and 80 discovery. Rotation covers every ticker at least once.
 n=len(dev); out=[]
 for f in range(4):
  blind={dev[(f*29+i)%n] for i in range(37)}
  out.append((sorted(set(dev)-blind),sorted(blind)))
 assert set().union(*[set(b) for _,b in out])==set(dev)
 return out

# Frozen architecture V2 genome: conditional strategy modules + explicit market/sector/stock context.
FAMILIES=['momentum','breakout','trend','mean_reversion','volatility','volume_liquidity','relative_strength','earnings','market_structure','reversal','pullback','volatility_breakout','composite_breadth']
ALLOCS=['equal','strength','uncertainty','downside']

def random_module(R,groups):
    sig_pool=groups['stock']+groups['sector']
    gate_pool=groups['market']+groups['sector']+groups['stock']
    ns=R.randint(2,min(5,len(sig_pool))); ng=R.randint(1,3)
    return {'family':R.choice(FAMILIES),
            'signal_ids':R.sample(sig_pool,ns),'signal_w':[R.uniform(-2,2) for _ in range(ns)],
            'gate_ids':R.sample(gate_pool,ng),'gate_w':[R.uniform(-3,3) for _ in range(ng)],
            'gate_bias':R.uniform(-1.5,1.5),'module_w':R.uniform(.25,2.0)}

def random_genome(R,F,groups):
    nm=R.randint(2,5)
    return {'modules':[random_module(R,groups) for _ in range(nm)],
            'opportunity_scale':10**R.uniform(-3.2,-1.2),
            'risk_appetite_id':R.choice(groups['market']),
            'risk_appetite_w':R.uniform(-3,3),'risk_appetite_bias':R.uniform(-1,1),
            'safe_margin':R.uniform(0,.00025),'replace_margin':R.uniform(0,.002),
            'short':R.random()<.45,'alloc':R.choice(ALLOCS)}

def mutate(R,g,F,groups):
    z=json.loads(json.dumps(g)); k=R.randrange(10)
    if k==0 and len(z['modules'])<8:z['modules'].append(random_module(R,groups))
    elif k==1 and len(z['modules'])>1:z['modules'].pop(R.randrange(len(z['modules'])))
    elif k in (2,3,4):
        m=R.choice(z['modules'])
        if k==2:
            j=R.randrange(len(m['signal_w'])); m['signal_w'][j]=max(-4,min(4,m['signal_w'][j]+R.gauss(0,.35)))
        elif k==3:
            j=R.randrange(len(m['gate_w'])); m['gate_w'][j]=max(-5,min(5,m['gate_w'][j]+R.gauss(0,.45)))
        else:m['gate_bias']=max(-3,min(3,m['gate_bias']+R.gauss(0,.25)))
    elif k==5:z['risk_appetite_w']=max(-5,min(5,z['risk_appetite_w']+R.gauss(0,.4)))
    elif k==6:z['risk_appetite_bias']=max(-2,min(2,z['risk_appetite_bias']+R.gauss(0,.2)))
    elif k==7:z['safe_margin']=min(.001,max(0,z['safe_margin']+R.gauss(0,.00004)))
    elif k==8:z['replace_margin']=min(.01,max(0,z['replace_margin']+R.gauss(0,.0004)))
    else:
        if R.random()<.5:z['alloc']=R.choice(ALLOCS)
        else:z['short']=not z['short']
    return z

def key(g): return json.dumps(g,sort_keys=True,separators=(',',':'))

def _sigmoid(x):
    return 1/(1+np.exp(-np.clip(x,-20,20)))

def opportunity(g,X):
    # Absolute opportunity: conditional modules; no cross-sectional rank transform.
    E=np.zeros(X.shape[:2],float); U=np.zeros_like(E); D=np.zeros_like(E)
    for m in g['modules']:
        sig=np.nan_to_num(X[:,:,m['signal_ids']],nan=.5)@np.asarray(m['signal_w'],float)
        gate=np.nan_to_num(X[:,:,m['gate_ids']],nan=.5)@np.asarray(m['gate_w'],float)+m['gate_bias']
        a=_sigmoid(gate)
        z=np.tanh(sig)*a*m['module_w']
        E+=z
        U+=a*(1-a)
        D+=a*np.maximum(-np.tanh(sig),0)
    E*=g['opportunity_scale']/max(1,len(g['modules']))
    U/=max(1,len(g['modules'])); D/=max(1,len(g['modules']))
    return E,U,D

def simulate(g,X,RX,rf,cost_bps=5):
    E,U,D=opportunity(g,X)
    # Market context directly controls risky appetite. This path cannot be cancelled by stock ranking.
    rid=g['risk_appetite_id']
    tau=_sigmoid(g['risk_appetite_w']*np.nan_to_num(X[:,:,rid],nan=.5)[:,0]+g['risk_appetite_bias'])
    # SAFE competes in the same daily-return opportunity numeraire.
    hurdle=rf[:,None]+g['safe_margin']
    signed=np.where(E>hurdle,E,0.0)
    if g['short']:
        signed=np.where(E < -hurdle,E,signed)
    else:signed=np.maximum(signed,0)
    W=np.zeros_like(signed); prev=np.zeros(signed.shape[1]); turnover=np.zeros(signed.shape[0])
    for t in range(signed.shape[0]-1):
        s=signed[t].copy()
        if g['alloc']=='equal':
            target=np.sign(s)*(np.abs(s)>0)
        elif g['alloc']=='strength':
            target=s.copy()
        elif g['alloc']=='uncertainty':
            target=s/(U[t]+.10)
        else:
            target=s/(D[t]+.10)
        gross=np.abs(target).sum()
        target=(target/gross)*tau[t] if gross>0 else target
        # Horizon-free lifecycle: incumbents continue unless challenger/SAFE clears an economic hurdle.
        if np.abs(prev).sum()>0:
            improve=np.abs(E[t])-np.abs(prev)*g['replace_margin']
            keep=(np.sign(prev)==np.sign(target)) & (improve>=0)
            target=np.where(keep,np.sign(prev)*np.maximum(np.abs(prev),np.abs(target)),target)
            gg=np.abs(target).sum()
            if gg>tau[t] and gg>0: target*=tau[t]/gg
        turnover[t]=np.abs(target-prev).sum(); W[t]=target; prev=target
    rr=np.nan_to_num(RX,nan=0)
    risky=(W*rr).sum(1); safe=np.maximum(0,1-np.abs(W).sum(1))*rf
    port=risky+safe-turnover*(cost_bps/10000)
    return port,W,turnover

def metrics(port,dates):
 p=np.nan_to_num(port,nan=0); eq=np.cumprod(1+p); peak=np.maximum.accumulate(eq); dd=eq/peak-1
 years=max(len(p)/252,1/252); cagr=float(eq[-2]**(1/years)-1) if len(eq)>1 and eq[-2]>0 else -1
 mdd=float(dd.min()); worst=float(p.min()); cvar=float(np.mean(np.sort(p)[:max(1,int(.05*len(p)))]))
 # drawdown velocity and recovery burden
 dvel=float(np.min(np.diff(dd))) if len(dd)>1 else 0
 underwater=dd<0; maxuw=cur=0
 for b in underwater:
  cur=cur+1 if b else 0; maxuw=max(maxuw,cur)
 def worstn(n):
  if len(p)<n:return 0.0
  lp=np.log1p(np.clip(p,-.999999,None)); cs=np.concatenate([[0.0],np.cumsum(lp)])
  return float(np.expm1(np.min(cs[n:]-cs[:-n])))
 return {'cagr':cagr,'mdd':mdd,'cvar5':cvar,'worst_day':worst,'worst5':worstn(5),'worst10':worstn(10),'worst20':worstn(20),'dd_velocity':dvel,'max_underwater_sessions':int(maxuw),'ending_multiple':float(eq[-2]) if len(eq)>1 else 1}

def evaluate(g,X,RX,rf,dates,idx,cost=5):
 subx=X[:,idx,:]; subr=RX[:,idx]
 p,w,to=simulate(g,subx,subr,rf,cost)
 m=metrics(p,dates)
 m['turnover']=float(to.mean()); m['safe_fraction']=float(np.mean(np.maximum(0,1-np.abs(w).sum(1))))
 # Four independent $100k-reset era views; metrics() starts each slice from 1.0.
 m['eras']={}
 for name,a,b in ERAS:
  mask=(dates>=pd.Timestamp(a))&(dates<=pd.Timestamp(b))
  m['eras'][name]=metrics(p[mask],dates[mask])
 # Distinguish phenomenon, selection, portfolio and effective independent evidence.
 active=np.abs(w)>0
 signed=np.sign(w)*np.nan_to_num(subr,nan=0)
 obs=signed[active]
 m['phenomenon']={'qualifying_stock_sessions':int(active.sum()),'mean_signed_next_return':float(obs.mean()) if len(obs) else 0.0,'positive_fraction':float((obs>0).mean()) if len(obs) else 0.0}
 chosen=np.where(active,signed,np.nan)
 unchosen=np.where(~active,np.nan_to_num(subr,nan=np.nan),np.nan)
 cd=np.nanmean(chosen,axis=1); ud=np.nanmean(unchosen,axis=1)
 spread=cd-ud; spread=spread[np.isfinite(spread)]
 m['selection']={'mean_selected_minus_unselected':float(spread.mean()) if len(spread) else 0.0,'positive_session_fraction':float((spread>0).mean()) if len(spread) else 0.0,'sessions':int(len(spread))}
 # Effective N from lag-1 autocorrelation of daily portfolio returns: conservative time-dependence discount.
 q=p[np.isfinite(p)]; rho=float(np.corrcoef(q[:-1],q[1:])[0,1]) if len(q)>3 and np.std(q[:-1])>0 and np.std(q[1:])>0 else 0.0
 rho=max(-.99,min(.99,rho)); neff=max(1.0,len(q)*(1-rho)/(1+rho))
 m['independent_evidence']={'raw_sessions':int(len(q)),'lag1_return_autocorrelation':rho,'effective_sessions_ar1':float(neff),'stocks':int(len(idx))}
 return m

def dominates(a,b):
 return a['cagr']>=b['cagr'] and a['mdd']>=b['mdd'] and (a['cagr']>b['cagr'] or a['mdd']>b['mdd'])

def pareto(items):
 return [z for z in items if not any(dominates(q['m'],z['m']) for q in items if q is not z)]

def search_fold(fi,train,blind,dev,X,RX,rf,dates,feats,groups,popn,gens,bench=False):
 R=random.Random(SEED+fi); idx={t:i for i,t in enumerate(dev)}; tr=np.array([idx[t] for t in train]); bl=np.array([idx[t] for t in blind])
 log_path=LOG.with_name(f'MTS_HORIZON_FREE_GA_FINAL_STUDY_FOLD{fi}_20261005.log')
 check_path=CHECK.with_name(f'MTS_HORIZON_FREE_GA_FINAL_STUDY_FOLD{fi}_CHECKPOINT_20261005.json')
 log_path.write_text('')
 cache={}; pop=[random_genome(R,len(feats),groups) for _ in range(popn)]; stale=0; lastfront=None; t0=time.time()
 for ge in range(gens):
  vals=[]
  for g in pop:
   k=key(g)
   if k not in cache: cache[k]=evaluate(g,X,RX,rf,dates,tr,5)
   vals.append({'g':g,'m':cache[k]})
  front=pareto(vals)
  sig=sorted((round(z['m']['cagr'],5),round(z['m']['mdd'],5)) for z in front)
  stale=stale+1 if sig==lastfront else 0; lastfront=sig
  # evolutionary ordering only: Pareto members first, then CAGR + drawdown; final claims use frontier.
  vals.sort(key=lambda z:((z in front),z['m']['cagr']+z['m']['mdd']),reverse=True)
  best=vals[0]
  line=f'FOLD={fi} GEN={ge} UNIQUE={len(cache)} FRONT={len(front)} CAGR={best["m"]["cagr"]:.5f} MDD={best["m"]["mdd"]:.5f} STALE={stale}'
  print(line,flush=True); LOG.parent.mkdir(parents=True,exist_ok=True)
  with LOG.open('a') as f:f.write(line+'\n')
  CHECK.write_text(json.dumps({'stage':'GA_RUNNING','fold':fi,'generation':ge,'unique':len(cache),'frontier':len(front),'elapsed_sec':time.time()-t0},indent=2))
  if bench and len(cache)>=1000: break
  if not bench and stale>=20: break
  elite=[z['g'] for z in vals[:max(24,popn//5)]]
  pop=list(elite)
  while len(pop)<popn:
   c=mutate(R,R.choice(elite),len(feats),groups)
   if R.random()<.2:c=mutate(R,c,len(feats),groups)
   pop.append(c)
 # PRE-REGISTERED TRAINING-ONLY FINALISTS: one max-CAGR genome per DD band; blind cannot select.
 allv=[{'g':json.loads(k),'m':v} for k,v in cache.items()]
 selected=[]
 for band in DD_BANDS:
  ok=[z for z in allv if z['m']['mdd']>=-band]
  if ok:
   z=max(ok,key=lambda q:q['m']['cagr'])
   if key(z['g']) not in {key(q['g']) for q in selected}: selected.append(z)
 freeze_path=ROOT/f'Research/State/MTS_FROZEN_ARCH_GA_V2_FOLD{fi}_FINALISTS_FREEZE_20261005.json'
 freeze_payload={'fold':fi,'selection_rule':'training-only max CAGR subject to each frozen DD band','bands':DD_BANDS,
                 'finalists':[{'genome':z['g'],'train':z['m']} for z in selected]}
 freeze_path.write_text(json.dumps(freeze_payload,indent=2))
 scored=[]
 for z in selected:
  bm=evaluate(z['g'],X,RX,rf,dates,bl,5)
  scored.append({'genome':z['g'],'train':z['m'],'blind':bm})
 return {'fold':fi,'train_tickers':train,'blind_tickers':blind,'unique':len(cache),'generations':ge+1,
         'finalist_freeze':str(freeze_path),'frontier':scored,'elapsed_sec':time.time()-t0}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--benchmark',action='store_true'); ap.add_argument('--fold-only',type=int,default=-1); ap.add_argument('--aggregate',action='store_true'); ap.add_argument('--population',type=int,default=250); ap.add_argument('--generations',type=int,default=200); args=ap.parse_args()
 d67,d50,dev=load_dev117(); dates,tickers,X,RX,ew_partition_mean,rf,feats,groups=make_arrays(dev); fs=folds(dev)
 manifest={'freeze_sha256':sha(FREEZE),'predictor_sha256':sha(PRED),'treasury_sha256':sha(RF),'heldout50_cohort_sha256':sha(H50),'cache67_sha256':sha(CACHE67),'dev67':d67,'consumed_holdout50':d50,'dev117':dev,'folds':[{'train':a,'blind':b} for a,b in fs],'features':feats,'groups':groups,'dates':[str(dates[0].date()),str(dates[-1].date())],'seed':SEED}
 STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(manifest,indent=2))
 LOG.parent.mkdir(parents=True,exist_ok=True)
 results=[]; start=time.time()
 if args.aggregate:
  results=[json.load(open(ROOT/f'Research/Reports/MTS_FROZEN_ARCH_GA_V2_FOLD{i}_20261005.json'))['result'] for i in range(4)]
  flat=[{'fold':r['fold'],**z} for r in results for z in r['frontier']]
  bands={}
  for b in DD_BANDS:
   ok=[z for z in flat if z['blind']['mdd']>=-b]
   bands[str(b)]=max(ok,key=lambda z:z['blind']['cagr']) if ok else None
  out={'format':'MTS_FROZEN_ARCH_GA_V2','status':'DEV117_COMPLETE','provenance':'NEW_RESEARCH_POST_RECOVERY','manifest':manifest,'fold_results':results,'behavioral_dd_frontier':bands,'next_evidence_stage':'DV25 only after DEV117 findings/finalists are frozen; A25 only after DV25 pass; preserve A75+B100'}
  OUT.write_text(json.dumps(out,indent=2)); print('AGGREGATED',OUT,flush=True); return
 if args.fold_only>=0:
  fi=args.fold_only
  r=search_fold(fi,*fs[fi],dev,X,RX,rf,dates,feats,groups,args.population,args.generations,False)
  fp=ROOT/f'Research/Reports/MTS_FROZEN_ARCH_GA_V2_FOLD{fi}_20261005.json'
  fp.write_text(json.dumps({'format':'MTS_FROZEN_ARCH_GA_V2_FOLD','manifest_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),'result':r},indent=2))
  print('FOLD_COMPLETE',fi,fp,flush=True); return
 if args.benchmark:
  # benchmark one fold until >=1000 unique evaluations
  r=search_fold(0,*fs[0],dev,X,RX,rf,dates,feats,groups,max(args.population,250),20,True); results=[r]
  rate=r['unique']/max(r['elapsed_sec'],1e-9); est=4*args.population*args.generations/rate
  out={'format':'MTS_HORIZON_FREE_GA_BENCHMARK_V1','eval_per_sec':rate,'estimated_full_seconds_no_early_stop':est,'estimated_full_hours_no_early_stop':est/3600,'benchmark':r,'manifest':manifest}
  OUT.with_name('MTS_HORIZON_FREE_GA_FINAL_STUDY_BENCHMARK_20261005.json').write_text(json.dumps(out,indent=2))
  print('BENCHMARK_EVAL_PER_SEC',rate,'ETA_HOURS',est/3600,flush=True); return
 for fi,(tr,bl) in enumerate(fs):
  results.append(search_fold(fi,tr,bl,dev,X,RX,rf,dates,feats,groups,args.population,args.generations,False))
 # Cross-fold recurrence: summarize genomes appearing near identical by feature set; preserve all blind outcomes.
 flat=[]
 for r in results:
  for z in r['frontier']: flat.append({'fold':r['fold'],**z})
 # Blind outcomes are diagnostic only; no cross-fold winner is selected using blind evidence.
 out={'format':'MTS_FROZEN_ARCH_GA_V2','status':'DEV117_COMPLETE','provenance':'NEW_RESEARCH_POST_RECOVERY',
      'elapsed_sec':time.time()-start,'manifest':manifest,'fold_results':results,
      'blind_policy':'diagnostic only; no finalist or winner selected from blind performance',
      'next_evidence_stage':'DV25 remains sealed pending explicit post-DEV117 decision; A25 only after DV25 pass; preserve A75+B100'}
 OUT.write_text(json.dumps(out,indent=2))
 print('COMPLETE',OUT,'ELAPSED_HOURS',(time.time()-start)/3600,flush=True)

if __name__=='__main__': main()
