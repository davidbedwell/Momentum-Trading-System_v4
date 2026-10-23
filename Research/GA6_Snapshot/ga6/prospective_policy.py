from dataclasses import dataclass
@dataclass(frozen=True)
class Policy:
 trigger:float=.05
 recovery:float=.5
 min_wait:int=1
 max_wait:int=10
 def __post_init__(self):
  if not (0<self.trigger<1 and 0<=self.recovery<=1 and 1<=self.min_wait<=self.max_wait):raise ValueError('bad policy')
class ExitReentry:
 def __init__(self,p):
  self.p=p;self.peak=None;self.trough=None;self.out=False;self.wait=0;self.pending=None
 def close(self,price):
  if price<=0:raise ValueError('bad close')
  if self.out:
   self.wait+=1;self.trough=min(self.trough,price)
   target=self.trough+(self.peak-self.trough)*self.p.recovery
   if self.wait>=self.p.min_wait and (price>=target or self.wait>=self.p.max_wait):self.pending='BUY'
  else:
   self.peak=max(self.peak or price,price)
   if price<=self.peak*(1-self.p.trigger):self.pending='SELL'
  return self.pending
 def open(self,price):
  if price<=0:raise ValueError('bad open')
  action=self.pending;self.pending=None
  if action=='SELL':self.out=True;self.wait=0;self.trough=price
  elif action=='BUY':self.out=False;self.peak=price;self.trough=None
  return action
