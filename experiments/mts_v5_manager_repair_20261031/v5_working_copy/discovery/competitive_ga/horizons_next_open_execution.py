"""Research-only next-open accounting for Horizons long-only weight proposals.
No implied fills at signal close; shorts deliberately blocked.
"""
from dataclasses import dataclass,field
import math
@dataclass
class Book:
 cash:float=100000.
 shares:dict=field(default_factory=dict)
 pending:dict=field(default_factory=dict)
 fees_paid:float=0.
 unsettled_cash:float=0.

def equity(book,prices):
 for ticker,qty in book.shares.items():
  if qty and (ticker not in prices or not math.isfinite(float(prices[ticker])) or float(prices[ticker])<=0):raise ValueError('missing held-position price')
 return book.cash+book.unsettled_cash+sum(q*float(prices[t]) for t,q in book.shares.items())

def settle(book):
 book.cash+=book.unsettled_cash
 book.unsettled_cash=0.

def apply_split(book,ticker,ratio):
 if not math.isfinite(float(ratio)) or ratio<=0:raise ValueError('invalid split ratio')
 if ticker in book.shares:book.shares[ticker]*=float(ratio)

def apply_dividend(book,ticker,amount_per_share):
 if not math.isfinite(float(amount_per_share)) or amount_per_share<0:raise ValueError('invalid dividend')
 payment=book.shares.get(ticker,0.)*float(amount_per_share)
 book.cash+=payment
 return payment

def queue(book,decisions):
 if book.pending:raise RuntimeError('pending orders must execute or cancel before new signals')
 for ticker,proposal in decisions.items():
  target=float(proposal['target_weight'])
  if not math.isfinite(target) or target<0 or target>.10+1e-12:raise ValueError('long-only 10 percent cap required')
  book.pending[ticker]=target

def execute_next_open(book,opens,fee_bps=0.,slippage_bps=0.):
 if not 0<=fee_bps<=1000 or not 0<=slippage_bps<=1000:raise ValueError('invalid costs')
 for ticker in book.pending:
  if ticker not in opens or not math.isfinite(float(opens[ticker])) or float(opens[ticker])<=0:raise ValueError('missing valid next-open price')
 if not book.pending:return []
 before=equity(book,opens)
 orders=[]
 # Sell first; proceeds remain unsettled and cannot finance same-session buys.
 for ticker in sorted(book.pending,key=lambda t:book.pending[t]):
  target=book.pending[ticker]
  price=float(opens[ticker]);current=book.shares.get(ticker,0.)
  desired=before*target/price
  if desired>=current:continue
  qty=current-desired;fill=price*(1-slippage_bps/10000);gross=qty*fill;fee=gross*fee_bps/10000
  book.unsettled_cash+=gross-fee;book.fees_paid+=fee;book.shares[ticker]=desired
  orders.append({'ticker':ticker,'side':'SELL','shares':qty,'price':fill,'fee':fee})
 for ticker in sorted(book.pending):
  target=book.pending[ticker];price=float(opens[ticker]);current=book.shares.get(ticker,0.)
  desired=max(0.,before*target/price-current)
  if desired<=0:continue
  fill=price*(1+slippage_bps/10000);unit=fill*(1+fee_bps/10000)
  qty=min(desired,max(0.,book.cash)/unit)
  if qty<=0:continue
  gross=qty*fill;fee=gross*fee_bps/10000
  book.cash-=gross+fee;book.fees_paid+=fee;book.shares[ticker]=current+qty
  orders.append({'ticker':ticker,'side':'BUY','shares':qty,'price':fill,'fee':fee})
 book.pending.clear()
 return orders
