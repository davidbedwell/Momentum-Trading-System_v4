"""Shared-capital next-open execution using the original GA6 settlement, corporate
 action and entry-equity risk primitives. Research-only until multi-stock validation.
"""
from ga5_redesign.settlement_ledger import SettledLedger
from mts_next_open_ledger_v1 import Order
from ga6.position_equity_risk_20261021 import PositionRisk
from ga5_chromosome_decisions import PositionState
from ga5_earnings_entry_embargo import entry_allowed

class SharedCapitalExecution:
 def __init__(self,cash=100000,fee=.001,annual_cash_yield=.03,max_sessions=40):
  if not 1<=max_sessions<=40:raise ValueError('invalid cap')
  self.ledger=SettledLedger(cash,fee,price_basis='split_adjusted')
  self.risk={};self.positions={};self.entry_index={};self.pending=[];self.nav=[]
  self.annual_cash_yield=annual_cash_yield;self.max_sessions=max_sessions
  self.last={};self.closed=[];self.rejections=[];self.session=-1
 def _sell(self,ds,t,price,decision,qty=None,reason='SELL'):
  held=self.ledger.holdings.get(t,0);qty=held if qty is None else min(held,qty)
  if qty<=0:return
  fill=self.ledger.execute_open(Order(decision,t,'SELL',qty),ds,price)
  self.risk[t].sell(qty,price,self.ledger.fee_rate)
  remaining=held-qty
  if not remaining:
   r=self.risk.pop(t);held_sessions=self.session-self.entry_index.pop(t)
   if held_sessions>self.max_sessions:raise RuntimeError('hold cap violated')
   self.closed.append(dict(symbol=t,exit_date=ds,holding_sessions=held_sessions,pnl=r.cumulative_realized_pnl,entry_equity=r.entry_equity,reason=reason))
   self.positions.pop(t,None)
  else:
   p=self.positions[t];self.positions[t]=PositionState(remaining,p.entry_price,p.peak_price,p.sessions_held)
  return fill
 def start(self,ds,opens,closes,rows,*,risk_veto,membership,blocked):
  self.session+=1;self.ledger.start_session(ds,self.session,self.annual_cash_yield)
  for t,r in rows.items():
   if r.get('dividends',0) or r.get('stock_splits',0):
    self.ledger.apply_ex_date(ds,t,float(r.get('stock_splits',0) or 0),float(r.get('dividends',0) or 0))
  # Sell mandatory exits first; settled cash cannot be spent until next session.
  mandatory=set()
  for t,r in list(self.risk.items()):
   if t not in opens:raise ValueError('missing held open '+t)
   if self.session-self.entry_index[t]>=self.max_sessions or r.mark(opens[t],self.ledger.fee_rate)['mandatory_exit'] or risk_veto.get(ds) is not True:
    self._sell(ds,t,opens[t],self.nav[-1][0] if self.nav else '1900-01-01',reason='MANDATORY');mandatory.add(t)
  previous=self.pending;self.pending=[]
  if risk_veto.get(ds) is True:
   for o in sorted(previous,key=lambda x:0 if x['action'] in ('EXIT','REPLACE_CANDIDATE','SCALE_OUT','REDUCE') else 1):
    t=o['symbol'];action=o['action'];price=opens.get(t)
    if t in mandatory or price is None:continue
    if action in ('EXIT','REPLACE_CANDIDATE') and self.ledger.holdings.get(t,0):self._sell(ds,t,price,o['decision_date'],reason=action)
    elif action in ('SCALE_OUT','REDUCE') and self.ledger.holdings.get(t,0):
     held=self.ledger.holdings[t];fraction=float(o.get('fraction',.5));self._sell(ds,t,price,o['decision_date'],qty=max(1,int(held*fraction)),reason=action)
    elif action in ('ENTER','SCALE_IN','ADD'):
     if not membership.get((ds,t),False) or not entry_allowed(t,ds,blocked):self.rejections.append((ds,t,'membership_or_earnings'));continue
     held=self.ledger.holdings.get(t,0)
     if action=='ENTER' and held:continue
     if action!='ENTER' and not held:continue
     equity=self.ledger.cash+sum(q*opens.get(k,self.last.get(k,0)) for k,q in self.ledger.holdings.items())
     weight=float(o.get('weight',0));limit=float(o.get('max_weight',.10))
     if action=='SCALE_IN':
      qty=min(int(equity*weight/(price*(1+self.ledger.fee_rate))),int(max(0,equity*limit-held*price)/(price*(1+self.ledger.fee_rate))))
     else:
      qty=int(max(0,equity*min(weight,limit)-held*price)/(price*(1+self.ledger.fee_rate)))
     qty=min(qty,int(self.ledger.available_cash()/(price*(1+self.ledger.fee_rate))))
     if qty<=0:self.rejections.append((ds,t,'unsettled_or_no_cash'));continue
     self.ledger.execute_open(Order(o['decision_date'],t,'BUY',qty),ds,price)
     if not held:
      self.risk[t]=PositionRisk(equity);self.entry_index[t]=self.session;self.positions[t]=PositionState(qty,price,price,0)
     else:
      p=self.positions[t];self.positions[t]=PositionState(held+qty,(held*p.entry_price+qty*price)/(held+qty),max(p.peak_price,price),p.sessions_held)
     self.risk[t].buy(qty,price,self.ledger.fee_rate)
  for t,r in self.risk.items():
   if t not in closes:raise ValueError('missing held close')
   r.mark(closes[t],self.ledger.fee_rate)
   p=self.positions[t];self.positions[t]=PositionState(p.shares,p.entry_price,max(p.peak_price,closes[t]),self.session-self.entry_index[t])
  self.last.update(closes)
  value=self.ledger.nav(closes);self.nav.append((ds,value))
  return value
 def schedule(self,ds,orders):
  if not self.nav or self.nav[-1][0]!=ds:raise ValueError('decision must follow close mark')
  for o in orders:
   if o['symbol'] not in self.last:raise ValueError('missing mark')
   self.pending.append({**o,'decision_date':ds})
