"""Evidence-gated capital competition; estimates must be causal and comparable.

This is a decision contract, not a predictor of strategy returns.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Opportunity:
    owner: tuple
    ticker: str
    expected_net_edge: float
    risk_cost: float
    turnover_cost: float
    eligible: bool = True

@dataclass(frozen=True)
class Transfer:
    incumbent: tuple
    challenger: tuple
    challenger_ticker: str
    released_weight: float
    incumbent_value: float
    challenger_value: float
    net_advantage: float


def compare(incumbent, challengers, *, held_weight, free_weight, margin=0., required_weight=None):
    if required_weight is None:
        required_weight = held_weight
    if (any(not isfinite(v) for v in (held_weight,free_weight,margin,required_weight)) or
        not 0 <= held_weight <= 1 or not 0 <= free_weight <= 1 or
        not 0 < required_weight <= 1 or margin < 0):
        raise ValueError('invalid capital constraints')
    items=(incumbent,*tuple(challengers))
    for item in items:
        if any(not isfinite(v) for v in (item.expected_net_edge,item.risk_cost,item.turnover_cost)):
            raise ValueError('nonfinite opportunity estimate')
        if item.risk_cost < 0 or item.turnover_cost < 0:
            raise ValueError('negative cost')
    if not incumbent.eligible or held_weight <= 0:
        raise ValueError('incumbent must be an existing funded position')
    value=lambda x:x.expected_net_edge-x.risk_cost-x.turnover_cost
    base=value(incumbent)
    viable=[x for x in items[1:] if x.eligible and x.owner!=incumbent.owner and value(x)>0]
    if not viable:return None
    best=max(viable,key=lambda x:(value(x),x.owner,x.ticker))
    advantage=value(best)-base
    shortfall=max(0.,required_weight-free_weight)
    if advantage<=margin or shortfall<=0:
        return None  # use sufficient idle capital before touching incumbents
    released=min(held_weight,shortfall)
    return Transfer(incumbent.owner,best.owner,best.ticker,released,base,value(best),advantage)
