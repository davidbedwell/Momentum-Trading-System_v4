#!/usr/bin/env python3
import gzip,pickle,json,math,collections,statistics
from pathlib import Path
import numpy as np
ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
DEV='/home/ubuntu/mts-v4-cache/discovery_research_population_v1.RECONSTRUCTED.pkl.gz'
REP='/home/ubuntu/mts-v4-cache/preserved50_test17_replay_population_20261005.pkl.gz'
OUT=ROOT/'Research/Reports/MTS_DEFENSIVE_STRATEGY_BANK_GENERALIZATION_AUTOPSY_20261005.json'
WINDOWS=[('GFC','2007-11-20','2009-03-30'),('2011','2011-06-13','2011-10-24'),('2015_16','2015-07-06','2016-03-04'),('2018','2018-11-14','2019-01-16'),('COVID','2020-04-01','2020-04-14'),('2022','2022-02-15','2022-11-02')]
def load(p):
 with gzip.open(p,'rb') as f:return pickle.load(f)['rows']
def win(d):
 for n,a,b in WINDOWS:
  if a<=d<=b:return n
 return None
def summarize(rows):
 r=[x for x in rows if win(x['signal_date'])]
 dates=collections.Counter(x['signal_date'] for x in r); tick=collections.Counter(x['ticker'] for x in r); fam=collections.Counter(x['family'] for x in r); hor=collections.Counter(x['h'] for x in r); epi=collections.Counter(win(x['signal_date']) for x in r)
 # date-cluster effective N from Herfindahl: 1/sum share^2
 def neff(c):
  s=sum(c.values()); return 1/sum((v/s)**2 for v in c.values()) if s else 0
 return {'events':len(r),'tickers':len(tick),'unique_dates':len(dates),'date_effective_n':neff(dates),'ticker_effective_n':neff(tick),'family_effective_n':neff(fam),
 'top10_date_share':sum(v for _,v in dates.most_common(10))/max(1,len(r)),'max_same_date':max(dates.values(),default=0),'by_episode':epi,'by_family':fam,'by_horizon':hor}
dev=load(DEV); rep=load(REP)
# split replay into P50/T17 using frozen names
T17={'BAX','FCX','CMCSA','BG','APA','LIN','VRSN','LYV','ARE','SNPS','GLW','DLTR','VRSK','NI','HD','SPG','NTAP'}
p50=[x for x in rep if x['ticker'] not in T17]; t17=[x for x in rep if x['ticker'] in T17]
# candidate ID concentration (candidate:hash)
def candidate_stats(rows):
 r=[x for x in rows if win(x['signal_date'])]
 c=collections.Counter((x['ticker'],x['family'],x['genome'],x['h']) for x in r)
 famcand=collections.Counter((x['family'],x['genome']) for x in r)
 s=len(r)
 return {'unique_ticker_candidates':len(c),'unique_family_candidate_ids':len(famcand),'top20_ticker_candidate_event_share':sum(v for _,v in c.most_common(20))/max(1,s),
 'median_events_per_ticker_candidate':statistics.median(c.values()) if c else 0,'max_events_one_ticker_candidate':max(c.values(),default=0)}
# Episode x ticker return correlation using candidate event ret aggregated by signal date then ticker.
def corr_structure(rows):
 out={}
 for n,a,b in WINDOWS:
  rr=[x for x in rows if a<=x['signal_date']<=b]
  dates=sorted(set(x['signal_date'] for x in rr)); ticks=sorted(set(x['ticker'] for x in rr))
  # per ticker/date mean candidate return; NaNs pairwise
  if len(dates)<3 or len(ticks)<2: out[n]={'median_pair_corr':None,'pairs':0}; continue
  di={d:i for i,d in enumerate(dates)}; ti={t:i for i,t in enumerate(ticks)}
  vals=[[[] for _ in dates] for __ in ticks]
  for x in rr: vals[ti[x['ticker']]][di[x['signal_date']]].append(float(x['ret']))
  A=np.full((len(ticks),len(dates)),np.nan)
  for i in range(len(ticks)):
   for j in range(len(dates)):
    if vals[i][j]:A[i,j]=np.mean(vals[i][j])
  cs=[]
  for i in range(len(ticks)):
   for j in range(i):
    m=np.isfinite(A[i])&np.isfinite(A[j])
    if m.sum()>=5 and np.std(A[i,m])>0 and np.std(A[j,m])>0: cs.append(float(np.corrcoef(A[i,m],A[j,m])[0,1]))
  med=float(np.median(cs)) if cs else None
  eff=(len(ticks)/(1+(len(ticks)-1)*max(0,med))) if med is not None else None
  out[n]={'median_pair_corr':med,'pairs':len(cs),'ticker_count':len(ticks),'corr_implied_effective_tickers':eff}
 return out
# frozen replay metrics + development metrics
rp=json.load(open(ROOT/'Research/Reports/MTS_DEFENSIVE_STRATEGY_BANK_PRESERVED50_TEST17_REPLAY_20261005.json'))
transport=[]
for z in rp['results']:
 d=z['development_metrics']; r=z['replay']
 transport.append({'id':z['id'],'dev_cagr':d['cagr'],'replay_cagr':r['cagr'],'cagr_delta':r['cagr']-d['cagr'],'dev_mdd':d['max_daily_mtm_drawdown'],'replay_mdd':r['max_daily_mtm_drawdown'],'mdd_delta':r['max_daily_mtm_drawdown']-d['max_daily_mtm_drawdown'],'replay_episodes':r['episodes'],'genome':r['g']})
# Family distribution total variation
sd=summarize(dev); sr=summarize(rep)
families=sorted(set(sd['by_family'])|set(sr['by_family']))
td=sum(sd['by_family'].values()); tr=sum(sr['by_family'].values())
tv=.5*sum(abs(sd['by_family'].get(f,0)/td-sr['by_family'].get(f,0)/tr) for f in families)
out={'format':'MTS_DEFENSIVE_STRATEGY_BANK_GENERALIZATION_AUTOPSY_V1','date':'2026-10-05','status':'DIAGNOSTIC_ONLY_NO_REPAIR',
'evidence':{'development':'consumed DEV population','replay':'preserved50 reconstructed + consumed TEST17','protected_access':False},
'population_structure':{'development':sd,'preserved50':summarize(p50),'test17':summarize(t17),'combined_replay':sr},
'candidate_preselection':{'development':candidate_stats(dev),'preserved50':candidate_stats(p50),'combined_replay':candidate_stats(rep)},
'cross_ticker_correlation':{'development':corr_structure(dev),'combined_replay':corr_structure(rep)},
'family_distribution_total_variation':tv,'finalist_transport':transport}
OUT.write_text(json.dumps(out,indent=2,default=lambda x:dict(x) if isinstance(x,collections.Counter) else x))
print('WROTE',OUT)
print('DEV',sd); print('REPLAY',sr); print('TV',tv); print('CORR_DEV',out['cross_ticker_correlation']['development']); print('CORR_REP',out['cross_ticker_correlation']['combined_replay'])
