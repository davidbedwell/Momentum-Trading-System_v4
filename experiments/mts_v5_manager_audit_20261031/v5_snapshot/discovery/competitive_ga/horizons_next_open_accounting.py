"""Research-only long-only next-open fill accounting for Horizons proposals.
No short, borrow, corporate-action, or full manager execution certification implied.
"""
from dataclasses import dataclass,field
import math
@dataclass
class Account:
 cash:float=100000.
 shares:dict=field(default_factory=dict)
 fees_paid:float=0.

def execute(account,targets,opens,fee_rate=.001,max_weight=.10):
 if not 0<=fee_rate<1:raise ValueError('invalid fee')
 if not 0<max_weight<=1:raise ValueError('invalid cap')
 if any(not math.isfinite(float(v)) or float(v)<0 or float(v)>max_weight for v in targets.values()):raise ValueError('long-only cap violated')
 if any(not math.isfinite(float(v)) or float(v)<=0 for v in opens.values()):raise ValueError('invalid open')
 tickers=set(targets)|set(account.shares)
 if not tickers<=set(opens):raise ValueError('missing next-open prices')
 equity=account.cash+sum(q*opens[t] for t,q in account.shares.items())
 if equity<=0:raise ValueError('nonpositive equity')
 desired={t:float(targets.get(t,0))*equity/opens[t] for t in tickers}
 trades=[]
 # Liquidations first to free cash; never borrow to execute long-only orders.
 for t in sorted(tickers):
  old=account.shares.get(t,0.);delta=min(0.,desired[t]-old)
  if delta<0:
   proceeds=-delta*opens[t];fee=proceeds*fee_rate
   account.cash+=proceeds-fee;account.fees_paid+=fee
   account.shares[t]=old+delta
   trades.append((t,delta,opens[t],fee))
 for t in sorted(tickers):
  old=account.shares.get(t,0.);wanted=max(0.,desired[t]-old)
  if wanted>0:
   qty=min(wanted,max(0.,account.cash)/(opens[t]*(1+fee_rate)))
   if qty<=0:continue
   cost=qty*opens[t];fee=cost*fee_rate
   account.cash-=cost+fee;account.fees_paid+=fee
   account.shares[t]=old+qty
   trades.append((t,qty,opens[t],fee))
 account.shares={t:q for t,q in account.shares.items() if q>1e-10}
 if account.cash< -1e-7:raise AssertionError('negative cash')
 return {'trades':trades,'cash':account.cash,'equity_after_fees':account.cash+sum(q*opens[t] for t,q in account.shares.items()),'fees_paid':account.fees_paid}
