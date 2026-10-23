"""Independent evidence accounting for all thirteen niches."""
from collections import defaultdict
from math import log1p
from statistics import mean

def summarize(trades,labels,niches,min_trades=50,min_episodes=10):
 grouped=defaultdict(list)
 for t in trades:
  niche=labels.get((str(t['entry_date'])[:10],t['ticker']))
  if niche in niches:grouped[niche].append(t)
 result={}
 for niche in niches:
  ts=grouped[niche];n=len(ts);episodes=len({str(t['entry_date'])[:7] for t in ts})
  vals=[float(t['net_return']) for t in ts]
  if any(v<=-1 for v in vals):raise ValueError('Nonphysical trade return')
  ev=mean(vals) if vals else None
  lg=mean(log1p(v) for v in vals) if vals else None
  from ga6.episode_uncertainty import assess
  confidence=assess(ts)
  eligible=n>=min_trades and episodes>=min_episodes and ev>0 and lg>0
  result[niche]={'count':n,'episodes':episodes,'net_ev':ev,'log_ev':lg,'eligible':eligible,'uncertainty':confidence,'win_rate':sum(v>0 for v in vals)/n if n else None,'tail_5pct':mean(sorted(vals)[:max(1,(n+19)//20)]) if n else None}
 return result

def rank_all(chromosomes,niches):
 ranks={n:[] for n in niches}
 for chromosome_id,report in chromosomes.items():
  for niche in niches:
   m=report[niche]
   if m['eligible']:ranks[niche].append((chromosome_id,m))
 for n in niches:ranks[n].sort(key=lambda x:(-x[1]['net_ev'],-x[1]['log_ev'],-x[1]['tail_5pct'],x[0]))
 return ranks
