"""Horizons signed-weight transitions; research-only proposals, not fills.
Short orders require a separate borrow/margin/fee-aware execution engine.
"""
from .horizons_full_math import targets

def decide(genome,causal_panel,previous=None,prior_returns=None,cap=.10,allow_shorts=False):
 previous=previous or {}
 if genome.get('short',False) and not allow_shorts:
  raise ValueError('short-enabled genome blocked until borrow and fee accounting certified')
 new=targets(genome,causal_panel,previous,cap,prior_returns)
 result={}
 for ticker in sorted(set(new)|set(previous)):
  old=float(previous.get(ticker,0.));current=float(new.get(ticker,0.))
  if abs(current-old)<1e-12:action='HOLD'
  elif old==0:action='ENTER_LONG' if current>0 else 'ENTER_SHORT'
  elif current==0:action='EXIT_LONG' if old>0 else 'COVER_SHORT'
  elif old*current<0:action='REVERSE_TO_LONG' if current>0 else 'REVERSE_TO_SHORT'
  elif abs(current)>abs(old):action='ADD_LONG' if current>0 else 'ADD_SHORT'
  else:action='REDUCE_LONG' if current>0 else 'REDUCE_SHORT'
  result[ticker]={'action':action,'previous_weight':old,'target_weight':current}
 return result
