"""Point-in-time chromosome competition kernel. Signal generation/execution adapters remain separate."""
from dataclasses import dataclass
from typing import Literal
from math import isfinite
Action=Literal['ENTER','HOLD','SCALE_IN','SCALE_OUT','EXIT','REPLACE_CANDIDATE']
@dataclass(frozen=True)
class Proposal:
 chromosome:int
 symbol:str
 asof:str
 action:Action
 niche:str
 expected_net_return:float
 confidence:float
 downside_risk:float
 target_weight:float
 evidence_cutoff:str
 def validate(self):
  assert self.evidence_cutoff<=self.asof,'future evidence leakage'
  assert self.action in ('ENTER','HOLD','SCALE_IN','SCALE_OUT','EXIT','REPLACE_CANDIDATE')
  assert all(isfinite(x) for x in (self.expected_net_return,self.confidence,self.downside_risk,self.target_weight))
  assert 0<=self.confidence<=1 and 0<=self.target_weight<=.10 and self.downside_risk>=0

def compete(proposals,*,asof,cash,nav,existing_weights=None,max_gross=1.0,per_name_limit=.10,fee=.001):
 """Deterministic cash-constrained proposals for NEXT session; never performs same-day fills.
 Only uses supplied point-in-time scores; real signal/mark adapters must be connected.
 """
 assert nav>0 and cash>=0
 existing_weights=existing_weights or {}
 for p in proposals:
  p.validate();assert p.asof==asof
 # Exit and reductions are considered before new purchases. No speculative release of unsettled proceeds.
 reductions={};bids={}
 for p in proposals:
  if p.action in ('EXIT','REPLACE_CANDIDATE'):reductions[p.symbol]=0.0
  elif p.action=='SCALE_OUT':reductions[p.symbol]=min(reductions.get(p.symbol,1.0),p.target_weight)
  elif p.action in ('ENTER','SCALE_IN','HOLD'):
   score=p.expected_net_return*p.confidence-p.downside_risk-fee
   if score>0 and (p.symbol not in bids or score>bids[p.symbol][0]):bids[p.symbol]=(score,p)
 orders=[{'symbol':s,'action':'REDUCE_OR_EXIT','target_weight':w,'execute_not_before':'next_session'} for s,w in sorted(reductions.items()) if existing_weights.get(s,0)>w]
 gross=sum(existing_weights.values());remaining_cash=cash
 for s,(score,p) in sorted(bids.items(),key=lambda item:(-item[1][0],item[0])):
  if s in reductions:continue
  held=existing_weights.get(s,0)
  desired=min(p.target_weight,per_name_limit)
  increment=max(0.0,min(desired-held,max_gross-gross,remaining_cash/nav/(1+fee)))
  if increment<=0:continue
  orders.append({'symbol':s,'action':'ENTER_OR_ADD','chromosome':p.chromosome,'niche':p.niche,'score':score,'incremental_weight':increment,'execute_not_before':'next_session'})
  remaining_cash-=increment*nav*(1+fee);gross+=increment
 return {'asof':asof,'orders':orders,'unallocated_cash_estimate':remaining_cash,'execution_status':'PROPOSALS_ONLY'}
