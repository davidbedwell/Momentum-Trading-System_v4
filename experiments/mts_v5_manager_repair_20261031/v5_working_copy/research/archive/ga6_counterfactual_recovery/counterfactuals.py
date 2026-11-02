"""GA6 chronological next-open exit/hold/reentry research, per entry cohort.
This is an isolated research analysis, not an execution signal.
"""
from math import log1p
from statistics import mean

def compare_path(entry_open,exit_open,reentry_open,final_open,exit_index,reentry_index,fee=.001,cash_daily=0.):
 if not (0<=exit_index<reentry_index) or min(entry_open,exit_open,reentry_open,final_open)<=0:raise ValueError('Invalid chronology/prices')
 if fee<0 or fee>=1:raise ValueError('Invalid fee')
 hold=(final_open*(1-fee))/(entry_open*(1+fee))-1
 exit_rebuy=((exit_open*(1-fee))/(entry_open*(1+fee)))*((final_open*(1-fee))/(reentry_open*(1+fee)))*(1+cash_daily)**(reentry_index-exit_index)-1
 cash_days=reentry_index-exit_index
 return {'hold_net':hold,'exit_reentry_net':exit_rebuy,'incremental_net':exit_rebuy-hold,'cash_sessions':cash_days,'exit_avoided_loss':exit_open>reentry_open,'false_alarm':exit_rebuy<hold,'reentry_price_change':reentry_open/exit_open-1}

def classify(trades,threshold=0.):
 items=list(trades)
 groups={'avoided_loss':[],'temporary_drawdown':[],'false_alarm_winner':[],'other':[]}
 for x in items:
  if x['hold_net']>0 and x['incremental_net']<threshold:group='false_alarm_winner'
  elif x['exit_avoided_loss'] and x['incremental_net']>threshold:group='avoided_loss' if x['hold_net']<0 else 'temporary_drawdown'
  else:group='other'
  groups[group].append(x)
 return {k:{'count':len(v),'mean_incremental_net':mean(x['incremental_net'] for x in v) if v else None,'cash_sessions':sum(x['cash_sessions'] for x in v)} for k,v in groups.items()}
