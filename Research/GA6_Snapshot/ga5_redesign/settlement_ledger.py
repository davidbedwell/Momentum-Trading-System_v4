"""Conservative cash-account T+1 settlement simulator, long-only.
Settlement uses exchange sessions supplied by the caller; not calendar days.
"""
from math import isfinite
from datetime import date
from ga5_corporate_action_ledger import ActionLedger
from mts_next_open_ledger_v1 import Order

class SettledLedger(ActionLedger):
 def __init__(self,starting_cash,fee_rate=.001,price_basis="split_adjusted"):
  super().__init__(starting_cash,fee_rate,price_basis)
  self.unsettled=[]
  self._unsettled_total=0.
  self.session_index=-1
  self.current_session=None
  self.last_session=None
  self.cash_yield_total=0.
 def start_session(self,date,index,annual_cash_yield=0.):
  if index<=self.session_index:raise ValueError("Nonmonotonic session")
  if not 0<=annual_cash_yield<1:raise ValueError("Invalid annual cash yield")
  if self.last_session is not None:
   elapsed=(__import__("datetime").date.fromisoformat(str(date)[:10])-__import__("datetime").date.fromisoformat(str(self.last_session)[:10])).days
   if elapsed<=0:raise ValueError("Nonmonotonic calendar date")
   # Research cash proxy: accrued on settled, uninvested cash only.
   earned=self.available_cash()*((1+annual_cash_yield)**(elapsed/365.25)-1)
   self.cash+=earned;self.cash_yield_total+=earned
  self.session_index=index
  self.current_session=date
  self.last_session=date
  self.unsettled=[(due,amount) for due,amount in self.unsettled if due>index]
  self._unsettled_total=sum(amount for _,amount in self.unsettled)
 def available_cash(self):
  return max(0.,self.cash-self._unsettled_total)
 def execute_open(self,order,execution_date,open_price):
  if execution_date!=self.current_session:raise ValueError("Session not opened")
  if not isfinite(open_price) or open_price<=0:raise ValueError("Invalid price")
  if order.side=="BUY":
   cost=order.shares*open_price*(1+self.fee_rate)
   if cost>self.available_cash()+1e-8:raise ValueError("Unsettled proceeds unavailable")
  result=super().execute_open(order,execution_date,open_price)
  if order.side=="SELL":
   proceeds=order.shares*open_price*(1-self.fee_rate)
   self.unsettled.append((self.session_index+1,proceeds))
   self._unsettled_total+=proceeds
  return result
