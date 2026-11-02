"""Causal selection using closed, settled synthetic position outcomes only.
A closed trade becomes eligible the following session; ties use deterministic rotation.
Research baseline, not a trained manager GA.
"""
from collections import defaultdict
from .synthetic_entry_competition import choose

class MaturedSelector:
    def __init__(self, min_samples=5):
        self.min_samples=min_samples
        self.outcomes=defaultdict(list)
        self.pending=[]
    def mature(self, session):
        ready=[item for item in self.pending if item[0]<session]
        self.pending=[item for item in self.pending if item[0]>=session]
        for _,owner,ret in ready:self.outcomes[str(owner)].append(float(ret))
    def close(self, session, owner, net_return):
        self.pending.append((session,str(owner),float(net_return)))
    def select(self, eligible, ticker, session):
        candidates=[(str(owner),weight) for owner,weight in eligible if weight>0]
        if not candidates:return None
        scored=[(sum(self.outcomes[owner])/len(self.outcomes[owner]),owner,weight)
                for owner,weight in candidates if len(self.outcomes[owner])>=self.min_samples]
        if scored:
            best=max(score for score,_,_ in scored)
            return choose([(owner,weight) for score,owner,weight in scored if score==best],ticker,session)
        return choose(candidates,ticker,session)
