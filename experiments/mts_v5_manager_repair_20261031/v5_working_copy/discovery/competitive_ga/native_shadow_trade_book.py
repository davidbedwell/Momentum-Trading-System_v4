"""Isolated next-open native shadow positions; not funded portfolio parity."""
from .causal_calibration import TradeOutcome

class ShadowBook:
    def __init__(self,fee=.001,genome_hashes=None):
        if not 0<=fee<1: raise ValueError('invalid fee')
        self.fee=fee
        self.genome_hashes=genome_hashes or {}
        self.positions={}
        self.pending={}
        self.completed=[]

    def open_session(self,session,bars):
        matured=[]
        for key,(action,decision_session,target,context) in self.pending.items():
            ticker=key[2]
            if ticker not in bars: raise ValueError('missing shadow execution bar')
            price=float(bars[ticker].open)
            if price<=0: raise ValueError('invalid open price')
            pos=self.positions.get(key)
            if action=='ENTER' and pos is None:
                units=target*(1-self.fee)/price
                self.positions[key]={'units':units,'cash':1-target,'entry_session':session,
                    'entry_context':tuple(context),'entry_price':price,'peak':price,'entry_equity':1.0}
            elif action in ('ADD','REDUCE','EXIT') and pos is not None:
                equity=pos['cash']+pos['units']*price
                if equity<=0: raise ValueError('invalid shadow equity')
                desired=0. if action=='EXIT' else min(1.,max(0.,target))*equity/price
                delta=desired-pos['units']
                if delta>0:
                    pos['entry_price']=(pos['entry_price']*pos['units']+price*delta)/desired
                fee=abs(delta)*price*self.fee
                pos['cash']-=delta*price+fee
                pos['units']=desired
                if action=='EXIT' or desired<=1e-12:
                    ret=(pos['cash']-pos['entry_equity'])/pos['entry_equity']
                    outcome=TradeOutcome(key[1],pos['entry_context'],pos['entry_session'],session,ret,'shadow',ticker,key[0],self.genome_hashes.get(key[:2]))
                    self.completed.append(outcome);matured.append(outcome)
                    del self.positions[key]
        self.pending={}
        return matured

    def close_session(self,session,proposals,contexts=None):
        contexts=contexts or {}
        for p in proposals:
            key=(p.family,p.chromosome_id,p.ticker)
            if key in self.pending: raise ValueError('conflicting shadow signals')
            if p.action=='ENTER' and key not in self.positions:
                self.pending[key]=('ENTER',session,p.target_weight,contexts.get(key,(p.family+'_ENTRY',)))
            elif p.action in ('ADD','REDUCE','EXIT') and key in self.positions:
                self.pending[key]=(p.action,session,p.target_weight,())
