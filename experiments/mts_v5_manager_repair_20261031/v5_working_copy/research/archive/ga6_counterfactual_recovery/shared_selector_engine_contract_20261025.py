"""Shared-capital selector contract. No evolution, no independent NAV summation."""
from dataclasses import dataclass
from collections import defaultdict
from ga6.selector_learning_fourfold_20261025 import fold_for
@dataclass(frozen=True)
class CandidateDecision:
    date:str
    ticker:str
    chromosome_id:str
    niche:str
    action:str
    weight:float
    score:float
    defense_mode:str
    source_session:str
    def validate(self):
        if self.action not in ('ENTER','EXIT','SCALE_IN','SCALE_OUT','HOLD'):
            raise ValueError('Unknown action')
        if not 0<=self.weight<=.30:raise ValueError('Invalid weight')
        if self.date<=self.source_session:raise ValueError('No same-close execution')
        fold_for(self.source_session)
        return self
def select_entries(decisions,held,capacity=10):
    """Deterministic rank for one shared portfolio; no implicit capital."""
    if not 1<=capacity<=10:raise ValueError('Invalid capacity')
    entries=[d.validate() for d in decisions if d.action=='ENTER' and d.ticker not in held]
    entries.sort(key=lambda d:(-d.score,d.ticker,d.chromosome_id))
    selected=[];seen=set(held)
    for d in entries:
        if len(seen)>=capacity:break
        if d.ticker in seen:continue
        selected.append(d);seen.add(d.ticker)
    return selected
def validate_exits(decisions,ownership):
    """Only the chromosome that owns a position can exit or scale it."""
    result=[]
    for d in decisions:
        d.validate()
        if d.action in ('EXIT','SCALE_IN','SCALE_OUT'):
            if ownership.get(d.ticker)!=d.chromosome_id:continue
            result.append(d)
    return result
def self_test():
    a=CandidateDecision('2020-01-03','A','one','NICHE-0001','ENTER',.1,2.,'on','2020-01-02')
    b=CandidateDecision('2020-01-03','A','two','NICHE-0001','ENTER',.1,3.,'on','2020-01-02')
    c=CandidateDecision('2020-01-03','B','three','NICHE-0002','ENTER',.1,1.,'on','2020-01-02')
    assert [(x.ticker,x.chromosome_id) for x in select_entries([a,b,c],{},2)]==[('A','two'),('B','three')]
    assert not validate_exits([a.__class__('2020-01-03','A','one','NICHE-0001','EXIT',0,0,'on','2020-01-02')],{'A':'two'})
    assert len(validate_exits([a.__class__('2020-01-03','A','two','NICHE-0001','EXIT',0,0,'on','2020-01-02')],{'A':'two'}))==1
    try:
        a.__class__('2020-01-02','A','one','NICHE-0001','ENTER',.1,2.,'on','2020-01-02').validate()
        raise AssertionError('Lookahead not blocked')
    except ValueError:pass
    return 'SHARED_SELECTOR_CONTRACT_TEST_OK'
if __name__=='__main__':print(self_test())
