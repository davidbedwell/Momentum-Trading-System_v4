"""Research-only Horizons close-to-next-open target decisions.
Requires externally certified causal normalized full-universe features.
Not certified for original simulator parity or full manager evolution.
"""
from .horizons_causal_rank import evaluate
from .horizons_causal_allocation import allocate

def decide(genome,normalized_by_ticker,previous=None,cap=.10):
 previous=previous or {}
 ranked=evaluate(genome,normalized_by_ticker)
 strengths={t:x['strength'] for t,x in ranked.items()}
 target=allocate(genome,strengths,previous,cap)
 actions={}
 for ticker in sorted(set(target)|set(previous)):
  old=float(previous.get(ticker,0.))
  new=float(target.get(ticker,0.))
  if abs(new-old)<1e-10:action='HOLD'
  elif old<=0 and new>0:action='ENTER'
  elif new<=0 and old>0:action='EXIT'
  elif new>old:action='ADD'
  else:action='REDUCE'
  actions[ticker]={'action':action,'target_weight':new,'previous_weight':old,'rank':ranked.get(ticker,{}).get('rank')}
 return actions
