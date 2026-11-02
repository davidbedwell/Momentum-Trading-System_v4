"""Research-only T+1 sale-proceeds settlement on explicit trading-session dates.
Caller supplies the actual ordered session calendar; no weekday approximation.
"""
import pandas as pd
from .horizons_next_open_execution import settle
class SessionSettlement:
 def __init__(self,dates):
  index=pd.DatetimeIndex(pd.to_datetime(dates))
  if len(index)<2 or index.has_duplicates or not index.is_monotonic_increasing:raise ValueError('ordered unique session calendar required')
  self.sessions=tuple(index)
  self.position=-1
  self.last_sale_index=None
 def advance(self,book,date):
  next_index=self.position+1
  if next_index>=len(self.sessions) or pd.Timestamp(date)!=self.sessions[next_index]:raise ValueError('cannot skip, repeat, or reorder trading sessions')
  self.position=next_index
  if self.last_sale_index is not None and self.position>self.last_sale_index:
   settle(book);self.last_sale_index=None
 def execute(self,book,opens,fee_bps=0.,slippage_bps=0.,sector_by_ticker=None,prior_returns=None,return_tickers=None):
  if self.position<0:raise RuntimeError('advance to trading session first')
  from .horizons_next_open_execution import execute_next_open
  from .horizons_risk_gate import validate
  validate(book,{t:{'target_weight':w} for t,w in book.pending.items()},opens,sector_by_ticker)
  from .horizons_correlation_gate import validate as check_correlation
  from .horizons_next_open_execution import equity
  portfolio_equity=equity(book,opens)
  weights={t:q*float(opens[t])/portfolio_equity for t,q in book.shares.items() if q>0}
  weights.update(book.pending)
  check_correlation(weights,prior_returns,return_tickers)
  orders=execute_next_open(book,opens,fee_bps,slippage_bps)
  if any(o['side']=='SELL' for o in orders):self.last_sale_index=self.position
  return orders
