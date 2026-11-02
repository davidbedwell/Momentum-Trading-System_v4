"""Fail-closed Horizons long-only proposal bridge into next-open research replay.
Requires caller to supply yesterday's targets; never executes same-close.
"""
from engines.portfolio_replay.kernel import Signal

def signals_from_decisions(decisions,chromosome_id,cap=.10):
 if not 0<cap<=.10:raise ValueError('learning cap must be <= 10%')
 out=[]
 for ticker,row in sorted(decisions.items()):
  target=float(row['target_weight']);old=float(row['previous_weight'])
  if not 0<=target<=cap or old<0:raise ValueError('signed/over-cap Horizons position requires certified execution')
  if row['action'] in ('ENTER_SHORT','ADD_SHORT','REDUCE_SHORT','COVER_SHORT','REVERSE_TO_SHORT'):
   raise ValueError('short action blocked')
  out.append(Signal(ticker,'HORIZONS',str(chromosome_id),target))
 return out
