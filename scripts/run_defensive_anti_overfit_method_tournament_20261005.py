#!/usr/bin/env python3
import json,collections,statistics,math
from pathlib import Path
import numpy as np
ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
FINAL=json.load(open(ROOT/'Research/Protocols/MTS_DEFENSIVE_STRATEGY_BANK_FINALISTS_FREEZE_20261004.json'))['finalists']
DEV50=sorted("AMGN CI MPC STLD EXC CFG AJG NUE KKR TDG PPG TRV RL CTSH T FIS NOW SBAC SMCI KDP COST OMC NKE RSG ROK SO XEL DECK TRGP WELL CDW ITW DHI IRM COIN TPL FANG HWM NFLX BEN BNY BLDR EVRG GILD MCO TECH CLX PCAR COO FITB".split())
FOLD={t:i%5 for i,t in enumerate(DEV50)}
def env():
 p=ROOT/'scripts/run_defensive_strategy_bank_ga_discovery_20261004.py'; s=p.read_text(); s=s[:s.index('pop=[randg()')]
 ns={'__file__':str(p),'__name__':'method_tournament'}; exec(compile(s,str(p),'exec'),ns); return ns
ns=env(); E=ns['E']
def mean(z):return float(np.mean(z)) if z else None
def sd(z):return float(np.std(z,ddof=1)) if len(z)>1 else 0.0
def stats_for(g):
 tr=ns['_trade_candidates'](ns['canon'](g)); rows=[]
 for t in tr:
  r=t['exit_price']/t['entry_price']-1
  rows.append({'ticker':t['ticker'],'date':t['entry_date'],'episode':t['window'],'ret':float(r),'fold':FOLD[t['ticker']]})
 # B: one date = one unit
 dates=collections.defaultdict(list)
 eps=collections.defaultdict(list)
 folds=collections.defaultdict(list)
 for x in rows: dates[x['date']].append(x['ret']); eps[x['episode']].append(x['ret']); folds[x['fold']].append(x['ret'])
 date_means=[mean(v) for v in dates.values()]
 epmeans={k:mean(v) for k,v in eps.items()}
 foldmeans={str(k):mean(folds.get(k,[])) for k in range(5)}
 fm=[v for v in foldmeans.values() if v is not None]
 # A: equal-weight cross-sectional composite of selected trade returns per entry date
 composite={'mean_daily_selected_composite_return':mean(date_means),'positive_date_fraction':sum(v>0 for v in date_means)/len(date_means) if date_means else None,'date_units':len(date_means)}
 # E is a descriptive stability vector, not a fitted scalar
 return {'events':len(rows),'pooled_mean':mean([x['ret'] for x in rows]),'pooled_win':sum(x['ret']>0 for x in rows)/len(rows),
 'A_composite':composite,
 'B_cluster_weighted':{'date_weighted_mean':mean(date_means),'date_weighted_sd':sd(date_means),'positive_date_fraction':composite['positive_date_fraction']},
 'C_stock_folds':{'fold_means':foldmeans,'mean_fold':mean(fm),'worst_fold':min(fm),'sd_folds':sd(fm),'positive_folds':sum(v>0 for v in fm),'n_folds':len(fm)},
 'D_episode_holdout':{'episode_means':epmeans,'episode_balanced_mean':mean(list(epmeans.values())),'worst_episode_mean':min(epmeans.values()),'positive_episodes':sum(v>0 for v in epmeans.values()),'n_episodes':len(epmeans)},
 'E_hierarchical':{'worst_stock_fold':min(fm),'positive_stock_folds':sum(v>0 for v in fm),'worst_episode_mean':min(epmeans.values()),'positive_episodes':sum(v>0 for v in epmeans.values()),'date_weighted_mean':mean(date_means),'positive_date_fraction':composite['positive_date_fraction']}}
dev={}
for f in FINAL: dev[f['id']]=stats_for(f['genome'])
out={'format':'MTS_DEFENSIVE_ANTI_OVERFIT_METHOD_TOURNAMENT_DEV50_V1','status':'DEV50_ONLY_METRICS_FROZEN_BEFORE_ANSWER_KEY','stock_fold_map':FOLD,'results':dev}
p=ROOT/'Research/Reports/MTS_DEFENSIVE_ANTI_OVERFIT_METHOD_TOURNAMENT_DEV50_20261005.json'; p.write_text(json.dumps(out,indent=2))
print('WROTE',p)
for k,z in dev.items():print(k,'pooled',round(100*z['pooled_mean'],2),'date',round(100*z['B_cluster_weighted']['date_weighted_mean'],2),'folds',[round(100*v,2) for v in z['C_stock_folds']['fold_means'].values()],'eps',{e:round(100,v*100) for e,v in z['D_episode_holdout']['episode_means'].items()})
