from ga6.prospective_policy import Policy

def simulate(path,policy=Policy(),fee=.001,cash_daily=0.):
 if len(path)<3:raise ValueError('path too short')
 trigger=policy.trigger;recovery=policy.recovery;min_wait=policy.min_wait;max_wait=policy.max_wait
 shares=1/(path[0][1]*(1+fee));cash=0.;actions=[];held=True
 peak=None;trough=None;out=False;wait=0;pending=None
 for i,(date,op,close) in enumerate(path):
  if i:
   act=pending;pending=None
   if act=='SELL':out=True;wait=0;trough=op
   elif act=='BUY':out=False;peak=op;trough=None
   if act=='SELL' and held:
    cash=shares*op*(1-fee);shares=0.;held=False;actions.append((date,'SELL',op))
   elif act=='BUY' and not held:
    shares=cash/(op*(1+fee));cash=0.;held=True;actions.append((date,'BUY',op))
  if not held:cash*=1+cash_daily
  if close<=0:raise ValueError('bad close')
  if out:
   wait+=1;trough=min(trough,close)
   target=trough+(peak-trough)*recovery
   if wait>=min_wait and (close>=target or wait>=max_wait):pending='BUY'
  else:
   peak=max(peak or close,close)
   if close<=peak*(1-trigger):pending='SELL'
 final=(shares*path[-1][2]*(1-fee) if held else cash)-1
 hold=path[-1][2]*(1-fee)/(path[0][1]*(1+fee))-1
 return {'policy_net':final,'hold_net':hold,'incremental_net':final-hold,'actions':actions,'trades':len(actions),'cash_at_end':not held}


def simulate_incremental(path,policy,fee=.001,cash_daily=0.):
 if len(path)<3:raise ValueError('path too short')
 trigger=policy.trigger;recovery=policy.recovery;min_wait=policy.min_wait;max_wait=policy.max_wait
 shares=1/(path[0][1]*(1+fee));cash=0.;held=True
 peak=None;trough=None;out=False;wait=0;pending=None
 for i,(date,op,close) in enumerate(path):
  if i:
   act=pending;pending=None
   if act=='SELL':out=True;wait=0;trough=op
   elif act=='BUY':out=False;peak=op;trough=None
   if act=='SELL' and held:
    cash=shares*op*(1-fee);shares=0.;held=False
   elif act=='BUY' and not held:
    shares=cash/(op*(1+fee));cash=0.;held=True
  if not held:cash*=1+cash_daily
  if close<=0:raise ValueError('bad close')
  if out:
   wait+=1;trough=min(trough,close)
   target=trough+(peak-trough)*recovery
   if wait>=min_wait and (close>=target or wait>=max_wait):pending='BUY'
  else:
   peak=max(peak or close,close)
   if close<=peak*(1-trigger):pending='SELL'
 final=(shares*path[-1][2]*(1-fee) if held else cash)-1
 hold=path[-1][2]*(1-fee)/(path[0][1]*(1+fee))-1
 return final,hold
