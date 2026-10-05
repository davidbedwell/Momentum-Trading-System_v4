#!/usr/bin/env python3
import json,collections,statistics
from pathlib import Path
ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
FINAL=json.load(open(ROOT/'Research/Protocols/MTS_DEFENSIVE_STRATEGY_BANK_FINALISTS_FREEZE_20261004.json'))['finalists']
def env(path,cut):
 s=Path(path).read_text(); s=s[:s.index(cut)]; ns={'__file__':str(path),'__name__':'autopsy_env'}; exec(compile(s,str(path),'exec'),ns); return ns
def analyze(ns):
 out={}
 for f in FINAL:
  g=ns['canon'](f['genome']); tr=ns['_trade_candidates'](g); E=ns['E']
  fam=collections.defaultdict(lambda:[0,0.0]); hor=collections.defaultdict(lambda:[0,0.0]); epi=collections.defaultdict(lambda:[0,0.0]); tick=collections.defaultdict(lambda:[0,0.0])
  rets=[]
  for t in tr:
   ev=E[t['i']]; r=t['exit_price']/t['entry_price']-1; rets.append(r)
   for d,k in [(fam,ev['family']),(hor,str(ev['h'])),(epi,t['window']),(tick,t['ticker'])]: d[k][0]+=1; d[k][1]+=r
  sr=sorted(((v[1],k,v[0]) for k,v in tick.items()),reverse=True); sl=sorted((v[1],k,v[0]) for k,v in tick.items())
  out[f['id']]={'candidate_trades':len(tr),'mean_trade_return':statistics.mean(rets) if rets else None,'win_rate':sum(x>0 for x in rets)/len(rets) if rets else None,
    'by_family':dict(fam),'by_horizon':dict(hor),'by_episode':dict(epi),'top5_tickers_by_sum_trade_return':sr[:5],'bottom5_tickers_by_sum_trade_return':sl[:5]}
 return out
dev=env(ROOT/'scripts/run_defensive_strategy_bank_ga_discovery_20261004.py','pop=[randg()')
rep=env(ROOT/'scripts/run_defensive_strategy_bank_preserved50_test17_replay_20261005.py','pop=[randg()')
out={'development':analyze(dev),'replay':analyze(rep)}
p=ROOT/'Research/Reports/MTS_DEFENSIVE_STRATEGY_BANK_GENERALIZATION_AUTOPSY_SELECTED_TRADES_20261005.json'; p.write_text(json.dumps(out,indent=2)); print('WROTE',p)
for side in out:
 print('\n',side)
 for k,z in out[side].items(): print(k,z['candidate_trades'],round(100*z['mean_trade_return'],2),round(100*z['win_rate'],1),z['by_family'])
