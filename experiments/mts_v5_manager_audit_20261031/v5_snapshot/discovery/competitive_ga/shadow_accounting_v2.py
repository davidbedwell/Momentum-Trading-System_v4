"""Independent shadow trades with fee-inclusive weighted basis.

Targets express proportional changes to shadow units, not a claim that an
isolated trade has the same capital constraints as the shared portfolio.
Returns divide total realized P&L by all entry/add capital, after full exit.
"""
from math import isfinite
from .causal_calibration import TradeOutcome

class ShadowLedger:
    def __init__(self,fee=.001):
        if not isfinite(fee) or not 0<=fee<1:raise ValueError('invalid fee')
        self.fee=fee
        self.positions={}
        self.pending={}
        self.outcomes=[]

    def at_open(self,session,bars):
        matured=[]
        for key,pos in self.positions.items():
            bar=bars[key[2]]
            if not isfinite(bar.split) or bar.split<=0:raise ValueError('invalid split')
            pos['shares']*=bar.split
            pos['basis']/=bar.split
            pos['entry_price']/=bar.split
            pos['peak']/=bar.split
            if not isfinite(bar.dividend):raise ValueError('invalid dividend')
            pos['realized']+=pos['shares']*bar.dividend
        for key,(action,target) in self.pending.items():
            price=float(bars[key[2]].open)
            if not isfinite(price) or price<=0:raise ValueError('invalid execution price')
            pos=self.positions.get(key)
            if action=='ENTER' and pos is None:
                self.positions[key]={'shares':1.,'basis':price*(1+self.fee),
                                     'initial_cost':price*(1+self.fee),
                                     'realized':0.,'entry':session,'target':target,
                                     'entry_price':price,'peak':price}
            elif pos is not None and action=='ADD' and target>pos['target']:
                qty=pos['shares']*(target/pos['target']-1)
                cost=qty*price*(1+self.fee)
                pos['entry_price']=(pos['entry_price']*pos['shares']+qty*price)/(pos['shares']+qty)
                pos['basis']=(pos['basis']*pos['shares']+cost)/(pos['shares']+qty)
                pos['shares']+=qty
                pos['initial_cost']+=cost
                pos['target']=target
            elif pos is not None and action in ('REDUCE','EXIT'):
                fraction=1. if action=='EXIT' else max(0.,min(1.,1-target/pos['target']))
                qty=pos['shares']*fraction
                pos['realized']+=qty*(price*(1-self.fee)-pos['basis'])
                pos['shares']-=qty
                pos['target']=target
                if pos['shares']<=1e-10:
                    ret=pos['realized']/pos['initial_cost']
                    outcome=TradeOutcome(key[1],(key[0]+'_ENTRY',),pos['entry'],session,ret,'shadow')
                    matured.append(outcome)
                    self.outcomes.append(outcome)
                    del self.positions[key]
        self.pending.clear()
        return matured

    @property
    def completed(self):
        return self.outcomes

    def open_session(self,session,bars):
        return self.at_open(session,bars)

    def close_session(self,session,proposals):
        return self.at_close(proposals)

    def at_close(self,proposals):
        for p in proposals:
            key=(p.family,p.chromosome_id,p.ticker)
            if key in self.pending:raise ValueError('duplicate shadow order')
            if p.action=='ENTER' and key not in self.positions:
                self.pending[key]=('ENTER',p.target_weight)
            elif p.action in ('ADD','EXIT','REDUCE') and key in self.positions:
                self.pending[key]=(p.action,p.target_weight)

    def native_states(self,bars):
        """Isolated owner state; weights retain the proportional-unit convention."""
        result={}
        for (family,cid,ticker),pos in self.positions.items():
            pos['peak']=max(pos['peak'],bars[ticker].close)
            result.setdefault((family,cid),{})[ticker]={
                'entry':pos['entry_price'],'peak':pos['peak'],
                'entry_session':pos['entry'],'shares':pos['shares'],
                'weight':pos['target'],'owner':(family,cid)}
        return result
