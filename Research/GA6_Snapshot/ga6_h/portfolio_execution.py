"""GA6-H deterministic long-only next-open execution primitives."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Order:
    symbol: str
    quantity: int
    side: str

@dataclass
class Portfolio:
    cash: float
    shares: dict
    entry_session: dict

    def equity(self, marks):
        return self.cash + sum(q * marks[s] for s,q in self.shares.items())

    def fill(self, order, open_price, cost_bps=10):
        if order.quantity <= 0 or not isfinite(open_price) or open_price <= 0:
            raise ValueError('invalid quantity or open price')
        if order.side == 'buy':
            amount=order.quantity*open_price*(1+cost_bps/10000)
            if amount>self.cash+1e-8: return False
            self.cash-=amount
            self.shares[order.symbol]=self.shares.get(order.symbol,0)+order.quantity
        elif order.side == 'sell':
            if self.shares.get(order.symbol,0)<order.quantity: return False
            self.cash+=order.quantity*open_price*(1-cost_bps/10000)
            remaining=self.shares[order.symbol]-order.quantity
            if remaining: self.shares[order.symbol]=remaining
            else:
                del self.shares[order.symbol]
                self.entry_session.pop(order.symbol,None)
        else: raise ValueError('invalid side')
        return True

def quantity_for_weight(cash,equity,price,weight,cost_bps=10):
    if not 0 < weight <= 0.10: raise ValueError('weight outside risk cap')
    if not isfinite(price) or price<=0: return 0
    return max(0,int(min(cash,equity*weight)/(price*(1+cost_bps/10000))))

def entry_permitted(symbol,session,schedules,sessions,decision_at,verified_tickers):
    from quarterly_embargo import entry_allowed
    return entry_allowed(symbol,session,schedules,sessions,decision_at,verified_tickers)
