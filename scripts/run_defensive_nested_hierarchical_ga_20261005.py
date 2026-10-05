#!/usr/bin/env python3
# Nested hierarchical Defensive GA: true exclusion during evolution.
import json,random,math,statistics
from pathlib import Path
import numpy as np
ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
BASE=ROOT/'scripts/run_defensive_strategy_bank_ga_discovery_20261004.py'
s=BASE.read_text(); s=s[:s.index('pop=[randg()')]
ns={'__file__':str(BASE),'__name__':'nested_ga_base'}; exec(compile(s,str(BASE),'exec'),ns)
E=ns['E']; X=ns['X']; FEATURES=ns['FEATURES']; QLEVELS=ns['QLEVELS']; FAMILIES=ns['FAMILIES']; HORIZONS=ns['HORIZONS']
DEV50=sorted("AMGN CI MPC STLD EXC CFG AJG NUE KKR TDG PPG TRV RL CTSH T FIS NOW SBAC SMCI KDP COST OMC NKE RSG ROK SO XEL DECK TRGP WELL CDW ITW DHI IRM COIN TPL FANG HWM NFLX BEN BNY BLDR EVRG GILD MCO TECH CLX PCAR COO FITB".split())
foldmap={t:i%5 for i,t in enumerate(DEV50)}
POP=220; ELITE=36; MAXGEN=20; STALE=6
# Event identities and windows.
TICK=np.array([e['ticker'] for e in E],object); WIN=np.array([e['window'] for e in E],int)
def make_cond(train_mask):
 conds=[]; meta=[]
 for fi,name in enumerate(FEATURES):
  vals=X[train_mask,:,fi].reshape(-1); vals=vals[np.isfinite(vals)]
  qs=np.quantile(vals,QLEVELS)
  for qi,q in enumerate(qs):
   a=X[:,:,fi]; conds.append(np.isfinite(a)&(a>=q)); meta.append({'feature':name,'direction':'>=','quantile':QLEVELS[qi],'threshold':float(q)})
   conds.append(np.isfinite(a)&(a<=q)); meta.append({'feature':name,'direction':'<=','quantile':QLEVELS[qi],'threshold':float(q)})
 return np.stack(conds,axis=2),meta
def run(label,train_mask,test_mask,seed):
 R=random.Random(seed); ns['R']=R; cache={}
 # Training-only thresholds, applied unchanged to heldout.
 cond,meta=make_cond(train_mask); ns['COND']=cond; ns['cond_meta']=meta; ns['M']=cond.shape[2]
 train_ids=set(np.flatnonzero(train_mask)); test_ids=set(np.flatnonzero(test_mask))
 def filt(g,ids):
  return [t for t in ns['_trade_candidates'](g) if t['i'] in ids]
 def cluster_metrics(tr):
  if not tr:return {'date_mean':-1,'episode_mean':-1,'worst_episode':-1,'positive_episodes':0,'dates':0}
  bydate={}; byep={}
  for t in tr:
   r=t['exit_price']/t['entry_price']-1
   bydate.setdefault(t['entry_date'],[]).append(r); byep.setdefault(t['window'],[]).append(r)
  dm=[float(np.mean(v)) for v in bydate.values()]; em=[float(np.mean(v)) for v in byep.values()]
  return {'date_mean':float(np.mean(dm)),'date_sd':float(np.std(dm)),'positive_dates':sum(x>0 for x in dm)/len(dm),'episode_mean':float(np.mean(em)),'worst_episode':min(em),'positive_episodes':sum(x>0 for x in em),'dates':len(dm),'episodes':len(em)}
 def evalg(g):
  g=ns['canon'](g); k=json.dumps(g,sort_keys=True,default=list)
  if k in cache:return cache[k]
  tr=filt(g,train_ids)
  if len(tr)<25:
   z={'score':-999,'g':g,'n':len(tr)}; cache[k]=z; return z
  cm=cluster_metrics(tr); sim=ns['_simulate_exact'](tr)
  # Correlated ticker multiplicity cannot directly improve score. Date-cluster and episode-balanced
  # economics dominate; exact-MTM drawdown remains explicit.
  score=6.0*cm['date_mean']+4.0*cm['episode_mean']+2.0*min(0,cm['worst_episode'])+1.25*sim['max_daily_mtm_drawdown']+.02*(cm['positive_episodes']/max(1,cm['episodes']))
  z={'score':float(score),'g':g,'n':len(tr),'cluster':cm,'sim':sim}; cache[k]=z; return z
 pop=[ns['randg']() for _ in range(POP)]; best=None; stale=0
 for gen in range(MAXGEN):
  ev=sorted((evalg(g) for g in pop),key=lambda z:z['score'],reverse=True)
  if best is None or ev[0]['score']>best['score']+1e-12:best=ev[0];stale=0
  else:stale+=1
  print(label,'GEN',gen,'UNIQUE',len(cache),'SCORE',round(best['score'],6),'DATE',round(best.get('cluster',{}).get('date_mean',0),5),'MDD',round(best.get('sim',{}).get('max_daily_mtm_drawdown',0),5),'STALE',stale,flush=True)
  if stale>=STALE:break
  elites=[z['g'] for z in ev[:ELITE]]; nxt=list(elites)
  while len(nxt)<POP:
   ch=ns['mutate'](R.choice(elites[:18]))
   if R.random()<.22:ch=ns['mutate'](ch)
   nxt.append(ch)
  pop=nxt
 g=best['g']; testtr=filt(g,test_ids); testcm=cluster_metrics(testtr); testsim=ns['_simulate_exact'](testtr)
 return {'label':label,'train_events':int(train_mask.sum()),'heldout_events':int(test_mask.sum()),'unique_genomes':len(cache),'genome':g,'genome_described':ns['describe'](g),'train':best,'heldout':{'n':len(testtr),'cluster':testcm,'sim':testsim}}
runs=[]
for f in range(5):
 test=np.array([foldmap.get(t,-1)==f for t in TICK]); train=~test
 runs.append(run('STOCK_FOLD_'+str(f),train,test,2026100500+f))
for w in range(6):
 test=(WIN==w); train=~test
 runs.append(run('EPISODE_'+ns['WNAMES'][w],train,test,2026100600+w))
out={'format':'MTS_DEFENSIVE_NESTED_HIERARCHICAL_GA_DEV50_V1','status':'DEV50_NESTED_COMPLETE_NO_VERIFICATION_ACCESSED','population':'DEV50','stock_fold_map':foldmap,'search_budget':{'pop':POP,'elite':ELITE,'maxgen':MAXGEN,'stale':STALE},'runs':runs,'preserved50_accessed':False,'test17_accessed':False,'protected_accessed':False}
p=ROOT/'Research/Reports/MTS_DEFENSIVE_NESTED_HIERARCHICAL_GA_DEV50_20261005.json'; p.write_text(json.dumps(out,indent=2,default=list))
print('WROTE',p)
for z in runs: print('FINAL',z['label'],'trainDate',round(100*z['train']['cluster']['date_mean'],2),'heldDate',round(100*z['heldout']['cluster']['date_mean'],2),'heldPosDate',round(100*z['heldout']['cluster'].get('positive_dates',0),1),'heldMDD',round(100*z['heldout']['sim']['max_daily_mtm_drawdown'],2),'heldN',z['heldout']['n'])
