"""GA6 EV-first discovery: conservative realized EV fitness; no CAGR/MDD selection."""
from math import isfinite
MIN_TRADES=30
def fitness(r):
 m=r.get('ga6_completed_position_metrics',{})
 n=m.get('completed_trades',0)
 lcb=m.get('net_ev_lower_confidence_95')
 if n<MIN_TRADES or lcb is None or not isfinite(lcb):
  return -100.
 return float(lcb)
def rank_scored(scored):
 return sorted(scored,key=lambda x:(-x[0],-x[2].get('ga6_completed_position_metrics',{}).get('completed_trades',0),x[1].identity()))
