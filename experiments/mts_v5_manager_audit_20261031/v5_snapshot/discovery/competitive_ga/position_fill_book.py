"""Average-cost position attribution from executed portfolio fills.
Research accounting: records entry basis and realized P&L, including fees.
Not a replacement for broker lot/tax accounting or settlement certification.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass
class Position:
    owner:tuple
    shares:float
    basis:float
    stop:float
    entry:float = 0.
    peak:float = 0.
    entry_session:int = 0

class FillBook:
    def __init__(self):
        self.positions={}
        self.realized=[]

    def apply(self,fill,owner=None,stop=None,session=0):
        date,ticker,side,quantity,price,fee=fill
        quantity=float(quantity);price=float(price);fee=float(fee)
        if not all(isfinite(x) for x in (quantity,price,fee)) or quantity<=0 or price<=0 or fee<0:
            raise ValueError('invalid fill')
        existing=self.positions.get(ticker)
        if side=='BUY':
            if existing is None:
                if owner is None or len(owner)!=2 or not all(owner):raise ValueError('missing buy owner')
                if stop is None or not 0<stop<=.02:raise ValueError('missing stop')
                self.positions[ticker]=Position(tuple(owner),quantity,price+fee/quantity,float(stop),price,price,session)
            else:
                if owner is not None and tuple(owner)!=existing.owner:raise ValueError('cross-owner scale-in')
                total=existing.shares+quantity
                existing.entry=(existing.entry*existing.shares+quantity*price)/total
                existing.basis=(existing.basis*existing.shares+quantity*price+fee)/total
                existing.shares=total
        elif side=='SELL':
            if existing is None or quantity>existing.shares+1e-8:raise ValueError('unowned sell')
            if owner is not None and tuple(owner)!=existing.owner:raise ValueError('cross-owner sell')
            pnl=quantity*(price-existing.basis)-fee
            self.realized.append({'date':date,'ticker':ticker,'owner':existing.owner,
                                  'quantity':quantity,'pnl':pnl,'return':pnl/(quantity*existing.basis)})
            existing.shares-=quantity
            if existing.shares<=1e-10:del self.positions[ticker]
        else:raise ValueError('invalid fill side')

    def held(self,ticker,close,nav):
        p=self.positions[ticker]
        if close<=0 or nav<=0:raise ValueError('invalid valuation')
        return {'entry':p.entry,'initial_stop':p.stop,'weight':p.shares*close/nav}
