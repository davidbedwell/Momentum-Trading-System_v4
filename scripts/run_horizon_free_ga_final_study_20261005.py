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
OUT=ROOT/'Research/Reports/MTS_HORIZON_FREE_GA_FINAL_STUDY_20261005.json'
CHECK=ROOT/'Research/Reports/MTS_HORIZON_FREE_GA_FINAL_STUDY_CHECKPOINT_20261005.json'
LOG=ROOT/'Research/Logs/MTS_HORIZON_FREE_GA_FINAL_STUDY_20261005.log'
STATE=ROOT/'Research/State/MTS_HORIZON_FREE_GA_FINAL_STUDY_INPUT_MANIFEST_20261005.json'
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
 cols=['security_id','effective_date','eligible','return_5__v1','return_20__v1','close_to_sma_20__v1','range_position_20__v1','rsi_14__v1','relative_volume_20_percentile__v1','drawdown_252__v1','realized_vol_20_percentile__v1','breadth_above_sma_200__v1','breadth_positive_20__v1']
 p=pq.read_table(PRED,columns=cols).to_pandas()
 p['date']=pd.to_datetime(p.effective_date).dt.tz_localize(None)
 p['ticker']=p.security_id.astype(str).str.rsplit('_',n=1).str[-1]
 p=p[p.eligible.fillna(False)]
 ren={'return_5__v1':'ret5','return_20__v1':'ret20','close_to_sma_20__v1':'sma20','range_position_20__v1':'range20','rsi_14__v1':'rsi14','relative_volume_20_percentile__v1':'relvol','drawdown_252__v1':'dd252','realized_vol_20_percentile__v1':'rvpct'}
 p=p.rename(columns=ren)
 market=p.groupby('date').agg(mret5=('ret5','median'),mret20=('ret20','median'),mdd=('dd252','median'),breadth200=('breadth_above_sma_200__v1','median'),breadth20=('breadth_positive_20__v1','median'),mrv=('rvpct','median')).sort_index()
 # R1 causal dimensions. Differences use only current/prior observations.
 market['breadth_vel5']=market.breadth20-market.breadth20.shift(5)
 market['breadth_vel10']=market.breadth20-market.breadth20.shift(10)
 market['breadth_accel']=market.breadth_vel5-market.breadth_vel5.shift(5)
 market['breadth_persist']=market.breadth20.rolling(5,min_periods=3).mean()
 market['prior_destruction']=-market.mdd
 market['price_impulse']=market.mret5
 market['failed_rebound_reduction']=market.mret20-market.mret20.shift(5)
 market['short_trend_repair']=market.mret20-market.mret20.shift(10)
 # stress: VIX/VVIX and OFR lagged two business observations
 v=pd.read_csv(ROOT/'Research/Data/CrashMultiMarketV1/VIX_History.csv'); v['date']=pd.to_datetime(v.DATE,format='%m/%d/%Y'); market['vix']=pd.to_numeric(v.set_index('date').CLOSE,errors='coerce').reindex(market.index).ffill()
 vv=pd.read_csv(ROOT/'Research/Data/CrashMultiMarketV1/VVIX_History.csv'); vv['date']=pd.to_datetime(vv.DATE,format='%m/%d/%Y'); market['vvix']=pd.to_numeric(vv.set_index('date').VVIX,errors='coerce').reindex(market.index).ffill()
 ofr=pd.read_csv(ROOT/'Research/Data/CrashCausalPackV1/ofr_fsi_raw_20261004.csv'); ofr['date']=pd.to_datetime(ofr.Date); ofr=ofr.set_index('date')[['Funding','Credit']].apply(pd.to_numeric,errors='coerce').sort_index().shift(2).reindex(market.index).ffill()
 market['funding']=ofr.Funding; market['credit']=ofr.Credit
 market['stress_norm']=-(market.vix.pct_change(5).replace([np.inf,-np.inf],np.nan).fillna(0)+market.vvix.pct_change(5).replace([np.inf,-np.inf],np.nan).fillna(0))/2
 market['recovery_retention']=market.mret20-market.mret20.rolling(20,min_periods=5).min()
 sf=['ret5','ret20','sma20','range20','rsi14','relvol','dd252','rvpct']
 mf=['mret5','mret20','mdd','breadth200','breadth20','mrv','breadth_vel5','breadth_vel10','breadth_accel','breadth_persist','prior_destruction','price_impulse','failed_rebound_reduction','short_trend_repair','vix','vvix','funding','credit','stress_norm','recovery_retention']
 q=p[p.ticker.isin(dev)][['ticker','date']+sf].merge(market.reset_index()[['date']+mf],on='date',how='left')
 return q,sf,mf,market

def make_arrays(dev):
 px=load_prices(dev); panel,sf,mf,market=load_panel(dev)
 dates=px.index.intersection(pd.Index(sorted(panel.date.unique())))
 dates=dates[(dates>=pd.Timestamp('2006-09-15'))&(dates<=pd.Timestamp('2026-09-14'))]
 T=len(dates); N=len(dev); idx={t:i for i,t in enumerate(dev)}
 ret=px[dev].reindex(dates).pct_change().shift(-1).to_numpy(dtype=np.float32)
 spy=np.nanmean(ret,axis=1).astype(np.float32)  # reporting comparator only; not a GA input
 feats=sf+mf; F=len(feats); X=np.full((T,N,F),np.nan,np.float32)
 p2=panel.set_index(['date','ticker'])
 for j,t in enumerate(dev):
  z=p2.xs(t,level='ticker').reindex(dates)
  X[:,j,:]=z[feats].to_numpy(dtype=np.float32)
 # cross-sectional causal ranks normalize stock features daily; market features same for all stocks
 for k in range(len(sf)):
  a=X[:,:,k]
  order=np.argsort(np.argsort(np.nan_to_num(a,nan=-1e30),axis=1),axis=1).astype(np.float32)
  valid=np.isfinite(a); den=np.maximum(valid.sum(1,keepdims=True)-1,1)
  r=order/den; r[~valid]=np.nan; X[:,:,k]=r
 # market features robust expanding percentile to avoid future scaling
 for k in range(len(sf),F):
  s=pd.Series(X[:,0,k],index=dates)
  vals=[]
  hist=[]
  for v in s:
   if np.isfinite(v):
    h=np.asarray(hist[-1260:],float)
    vals.append(float((h<=v).mean()) if len(h)>=60 else .5); hist.append(float(v))
   else: vals.append(.5)
  X[:,:,k]=np.asarray(vals,np.float32)[:,None]
 rf=pd.read_csv(RF); rf['observation_date']=pd.to_datetime(rf.observation_date); rf['DGS3MO']=pd.to_numeric(rf.DGS3MO,errors='coerce')
 rfd=rf.set_index('observation_date').DGS3MO.reindex(dates).ffill().fillna(0).to_numpy(dtype=np.float32)/100/252
 return dates,np.asarray(dev),X,ret,spy,rfd,feats,sf,mf

def folds(dev):
 # four predetermined rotations; each has 37 blind and 80 discovery. Rotation covers every ticker at least once.
 n=len(dev); out=[]
 for f in range(4):
  blind={dev[(f*29+i)%n] for i in range(37)}
  out.append((sorted(set(dev)-blind),sorted(blind)))
 assert set().union(*[set(b) for _,b in out])==set(dev)
 return out

# Genome: sparse causal feature weights + qualification, long/short permissions, replacement margin and allocation transform.
def random_genome(R,F):
 n=R.randint(8,min(12,F)); ids=sorted(R.sample(range(F),n))
 return {'ids':ids,'w':[R.uniform(-2,2) for _ in ids],'qual':R.uniform(.50,.90),'short':R.random()<.45,'short_qual':R.uniform(.50,.90),'replace_margin':R.uniform(0,.30),'alloc':R.choice(['strength','uncertainty','downside']),'safe_margin':R.uniform(0,.03)}

def mutate(R,g,F):
 z=json.loads(json.dumps(g)); k=R.randrange(8)
 if k==0:
  j=R.randrange(len(z['w'])); z['w'][j]=max(-3,min(3,z['w'][j]+R.gauss(0,.35)))
 elif k==1 and len(z['ids'])<12:
  choices=[i for i in range(F) if i not in z['ids']]
  if choices:
   z['ids'].append(R.choice(choices)); z['w'].append(R.uniform(-2,2))
 elif k==2 and len(z['ids'])>8:
  j=R.randrange(len(z['ids'])); z['ids'].pop(j); z['w'].pop(j)
 elif k==3:z['qual']=min(.95,max(.40,z['qual']+R.gauss(0,.04)))
 elif k==4:z['short']=not z['short']
 elif k==5:z['short_qual']=min(.95,max(.40,z['short_qual']+R.gauss(0,.04)))
 elif k==6:z['replace_margin']=min(.5,max(0,z['replace_margin']+R.gauss(0,.04)))
 else:
  if R.random()<.5:z['alloc']=R.choice(['strength','uncertainty','downside'])
  else:z['safe_margin']=min(.08,max(0,z['safe_margin']+R.gauss(0,.006)))
 q=sorted(zip(z['ids'],z['w'])); z['ids']=[a for a,b in q]; z['w']=[b for a,b in q]
 return z

def key(g): return json.dumps(g,sort_keys=True,separators=(',',':'))

def simulate(g,X,RX,rf,cost_bps=5):
 ids=np.asarray(g['ids']); w=np.asarray(g['w'],float)
 raw=np.nan_to_num(X[:,:,ids],nan=.5)@w
 # daily cross-sectional percentile of opportunity score
 rank=np.argsort(np.argsort(raw,axis=1),axis=1)/(raw.shape[1]-1)
 long=np.maximum(rank-g['qual'],0)
 short=np.maximum((1-rank)-g['short_qual'],0) if g['short'] else np.zeros_like(long)
 strength=long-short
 # SAFE hurdle: weak opportunities stay in Treasury.
 hurdle=g['safe_margin']/252
 mag=np.abs(strength); active=mag>hurdle
 strength=np.where(active,strength,0)
 if g['alloc']=='uncertainty':
  dispersion=np.nanstd(raw,axis=1,keepdims=True)+1e-6; strength=strength/dispersion
 elif g['alloc']=='downside':
  downside=np.nanstd(np.minimum(np.nan_to_num(RX,nan=0),0),axis=1,keepdims=True)+1e-4; strength=strength/downside
 # no slot ceiling; normalize gross exposure <=1. Incumbent persistence is economic replacement margin, not time.
 W=np.zeros_like(strength); prev=np.zeros(strength.shape[1]); turnover=np.zeros(strength.shape[0])
 for t in range(strength.shape[0]-1):
  s=strength[t].copy(); gross=np.abs(s).sum()
  target=s/gross if gross>0 else s
  if np.abs(prev).sum()>0 and np.abs(target).sum()>0:
   keep=(np.sign(prev)==np.sign(target)) & (np.abs(target)+g['replace_margin']>=np.abs(prev))
   target=np.where(keep,np.maximum(np.abs(prev),np.abs(target))*np.sign(target),target)
   gg=np.abs(target).sum(); target=target/gg if gg>1 else target
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
  s=pd.Series(p).rolling(n).apply(lambda x:np.prod(1+x)-1,raw=True); return float(s.min()) if s.notna().any() else 0
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

def search_fold(fi,train,blind,dev,X,RX,rf,dates,feats,popn,gens,bench=False):
 R=random.Random(SEED+fi); idx={t:i for i,t in enumerate(dev)}; tr=np.array([idx[t] for t in train]); bl=np.array([idx[t] for t in blind])
 log_path=LOG.with_name(f'MTS_HORIZON_FREE_GA_FINAL_STUDY_FOLD{fi}_20261005.log')
 check_path=CHECK.with_name(f'MTS_HORIZON_FREE_GA_FINAL_STUDY_FOLD{fi}_CHECKPOINT_20261005.json')
 log_path.write_text('')
 cache={}; pop=[random_genome(R,len(feats)) for _ in range(popn)]; stale=0; lastfront=None; t0=time.time()
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
   c=mutate(R,R.choice(elite),len(feats))
   if R.random()<.2:c=mutate(R,c,len(feats))
   pop.append(c)
 # freeze full training Pareto and blind-score it without feeding blind results back
 allv=[{'g':json.loads(k),'m':v} for k,v in cache.items()]
 fr=pareto(allv)
 scored=[]
 for z in fr:
  bm=evaluate(z['g'],X,RX,rf,dates,bl,5)
  scored.append({'genome':z['g'],'train':z['m'],'blind':bm})
 return {'fold':fi,'train_tickers':train,'blind_tickers':blind,'unique':len(cache),'generations':ge+1,'frontier':scored,'elapsed_sec':time.time()-t0}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--benchmark',action='store_true'); ap.add_argument('--fold-only',type=int,default=-1); ap.add_argument('--aggregate',action='store_true'); ap.add_argument('--population',type=int,default=250); ap.add_argument('--generations',type=int,default=200); args=ap.parse_args()
 d67,d50,dev=load_dev117(); dates,tickers,X,RX,spy,rf,feats,sf,mf=make_arrays(dev); fs=folds(dev)
 manifest={'freeze_sha256':sha(FREEZE),'predictor_sha256':sha(PRED),'treasury_sha256':sha(RF),'heldout50_cohort_sha256':sha(H50),'cache67_sha256':sha(CACHE67),'dev67':d67,'consumed_holdout50':d50,'dev117':dev,'folds':[{'train':a,'blind':b} for a,b in fs],'features':feats,'dates':[str(dates[0].date()),str(dates[-1].date())],'seed':SEED}
 STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(manifest,indent=2))
 LOG.parent.mkdir(parents=True,exist_ok=True)
 results=[]; start=time.time()
 if args.aggregate:
  results=[json.load(open(ROOT/f'Research/Reports/MTS_HORIZON_FREE_GA_FINAL_STUDY_FOLD{i}_20261005.json'))['result'] for i in range(4)]
  flat=[{'fold':r['fold'],**z} for r in results for z in r['frontier']]
  bands={}
  for b in DD_BANDS:
   ok=[z for z in flat if z['blind']['mdd']>=-b]
   bands[str(b)]=max(ok,key=lambda z:z['blind']['cagr']) if ok else None
  out={'format':'MTS_HORIZON_FREE_GA_FINAL_STUDY_V1','status':'DEV117_COMPLETE','provenance':'NEW_RESEARCH_POST_RECOVERY','manifest':manifest,'fold_results':results,'behavioral_dd_frontier':bands,'next_evidence_stage':'DV25 only after DEV117 findings/finalists are frozen; A25 only after DV25 pass; preserve A75+B100'}
  OUT.write_text(json.dumps(out,indent=2)); print('AGGREGATED',OUT,flush=True); return
 if args.fold_only>=0:
  fi=args.fold_only
  r=search_fold(fi,*fs[fi],dev,X,RX,rf,dates,feats,args.population,args.generations,False)
  fp=ROOT/f'Research/Reports/MTS_HORIZON_FREE_GA_FINAL_STUDY_FOLD{fi}_20261005.json'
  fp.write_text(json.dumps({'format':'MTS_HORIZON_FREE_GA_FOLD_V1','manifest_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),'result':r},indent=2))
  print('FOLD_COMPLETE',fi,fp,flush=True); return
 if args.benchmark:
  # benchmark one fold until >=1000 unique evaluations
  r=search_fold(0,*fs[0],dev,X,RX,rf,dates,feats,max(args.population,250),20,True); results=[r]
  rate=r['unique']/max(r['elapsed_sec'],1e-9); est=4*args.population*args.generations/rate
  out={'format':'MTS_HORIZON_FREE_GA_BENCHMARK_V1','eval_per_sec':rate,'estimated_full_seconds_no_early_stop':est,'estimated_full_hours_no_early_stop':est/3600,'benchmark':r,'manifest':manifest}
  OUT.with_name('MTS_HORIZON_FREE_GA_FINAL_STUDY_BENCHMARK_20261005.json').write_text(json.dumps(out,indent=2))
  print('BENCHMARK_EVAL_PER_SEC',rate,'ETA_HOURS',est/3600,flush=True); return
 for fi,(tr,bl) in enumerate(fs):
  results.append(search_fold(fi,tr,bl,dev,X,RX,rf,dates,feats,args.population,args.generations,False))
 # Cross-fold recurrence: summarize genomes appearing near identical by feature set; preserve all blind outcomes.
 flat=[]
 for r in results:
  for z in r['frontier']: flat.append({'fold':r['fold'],**z})
 # behavioral frontier on blind results
 bands={}
 for b in DD_BANDS:
  ok=[z for z in flat if z['blind']['mdd']>=-b]
  bands[str(b)]=max(ok,key=lambda z:z['blind']['cagr']) if ok else None
 out={'format':'MTS_HORIZON_FREE_GA_FINAL_STUDY_V1','status':'DEV117_COMPLETE','provenance':'NEW_RESEARCH_POST_RECOVERY','elapsed_sec':time.time()-start,'manifest':manifest,'fold_results':results,'behavioral_dd_frontier':bands,'next_evidence_stage':'DV25 only after DEV117 findings/finalists are frozen; A25 only after DV25 pass; preserve A75+B100'}
 OUT.write_text(json.dumps(out,indent=2))
 print('COMPLETE',OUT,'ELAPSED_HOURS',(time.time()-start)/3600,flush=True)

if __name__=='__main__': main()
