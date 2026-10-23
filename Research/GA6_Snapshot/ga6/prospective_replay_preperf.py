from ga6.prospective_policy import Policy,ExitReentry
from statistics import mean

def simulate(path,policy=Policy(),fee=.001,cash_daily=0.):
 if len(path)<3:raise ValueError('path too short')
 engine=ExitReentry(policy);shares=1/(path[0][1]*(1+fee));cash=0.;actions=[];held=True
 for i,(date,op,close) in enumerate(path):
  if i:
   act=engine.open(op)
   if act=='SELL' and held:
    cash=shares*op*(1-fee);shares=0.;held=False;actions.append((date,'SELL',op))
   elif act=='BUY' and not held:
    shares=cash/(op*(1+fee));cash=0.;held=True;actions.append((date,'BUY',op))
  if not held:cash*=1+cash_daily
  engine.close(close)
 final=(shares*path[-1][2]*(1-fee) if held else cash)-1
 hold=path[-1][2]*(1-fee)/(path[0][1]*(1+fee))-1
 return {'policy_net':final,'hold_net':hold,'incremental_net':final-hold,'actions':actions,'trades':len(actions),'cash_at_end':not held}
