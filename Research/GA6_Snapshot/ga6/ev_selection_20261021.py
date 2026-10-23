"""Completed-position EV selection. One score, no CAGR/MDD in breeding."""
from math import isfinite,sqrt
def fitness(r):
 m=r.get('ga6_completed_position_metrics',{})
 n=m.get('completed_trades',0)
 ev=m.get('net_ev_entry_equity')
 if not n or ev is None or not isfinite(float(ev)):return -100.
 # Conservative effective sample size: correlated trades can overstate evidence.
 # This penalty is deliberately a provisional regularizer, not a confidence bound.
 return float(ev)*n/(n+100)
def rank_scored(scored):
 return sorted(scored,key=lambda x:(-x[0],x[1].identity()))
