"""Six-question portfolio manager policy prototype.
Pure deterministic decision logic; inputs must be causal and chromosome
expected returns calibrated on matured, out-of-time observations.
Not a substitute for the native portfolio replay or evolutionary fitness.
"""
from dataclasses import dataclass
from math import isfinite

ACTIONS=("ENTER","INCREASE","HOLD","REDUCE","EXIT","PASS")
@dataclass(frozen=True)
class Opportunity:
    ticker:str
    chromosome_id:str
    action:str
    expected_net_r:float
    downside_r:float
    confidence:float
    requested_weight:float
    pattern:str
    family:str

@dataclass(frozen=True)
class PortfolioState:
    weights:dict
    cash_weight:float
    defense:bool=False

@dataclass(frozen=True)
class ManagerGenes:
    entry_edge:float=.01
    replace_margin:float=.015
    risk_aversion:float=1.
    agreement_bonus:float=.05
    max_new_weight:float=.10
    min_cash:float=0.

def coordinate(proposals,state,genes):
    """Compete across holdings and opportunities; one target action per ticker.
    No forced purchases, no invented liquidation, and no short exposure.
    Proposals are expected to be calibrated on a common net-return scale.
    """
    if state.defense:
        return {ticker:("EXIT",0., "DEFENSE") for ticker,w in state.weights.items() if w>0}
    groups={}
    for p in proposals:
        if p.action not in ACTIONS:raise ValueError("invalid action")
        if any(not isfinite(float(x)) for x in (p.expected_net_r,p.downside_r,p.confidence,p.requested_weight)):
            raise ValueError("nonfinite proposal")
        groups.setdefault(p.ticker,[]).append(p)
    candidates=[]
    for ticker,group in groups.items():
        # Do not count correlated same-family votes as independent reinforcement.
        distinct=len({p.family for p in group if p.action in ("ENTER","INCREASE","HOLD")})
        support=genes.agreement_bonus*max(0,distinct-1)
        ranked=sorted(group,key=lambda p:p.expected_net_r-genes.risk_aversion*max(0,p.downside_r)+support*max(0,p.confidence),reverse=True)
        best=ranked[0]
        edge=best.expected_net_r-genes.risk_aversion*max(0,best.downside_r)+support*max(0,best.confidence)
        candidates.append((edge,ticker,best))
    candidates.sort(key=lambda x:(-x[0],x[1]))
    result={}
    # Exits/reductions of held names are evaluated before new capital deployment.
    for edge,ticker,p in candidates:
        held=state.weights.get(ticker,0.)
        if held and p.action=="EXIT":result[ticker]=("EXIT",0.,p.chromosome_id)
        elif held and p.action=="REDUCE":result[ticker]=("REDUCE",max(0.,min(held,p.requested_weight)),p.chromosome_id)
    cash=state.cash_weight+sum(max(0.,state.weights[t]-target) for t,(act,target,_) in result.items())
    for edge,ticker,p in candidates:
        if ticker in result:continue
        held=state.weights.get(ticker,0.)
        if p.action in ("PASS","EXIT","REDUCE"):
            if held:result[ticker]=("HOLD",held,p.chromosome_id)
            continue
        if held:
            if p.action=="INCREASE" and edge>=genes.entry_edge:
                add=min(max(0.,p.requested_weight-held),genes.max_new_weight, max(0.,cash-genes.min_cash))
                if add>0:result[ticker]=("INCREASE",held+add,p.chromosome_id);cash-=add
                else:result[ticker]=("HOLD",held,p.chromosome_id)
            else:result[ticker]=("HOLD",held,p.chromosome_id)
        elif p.action=="ENTER" and edge>=genes.entry_edge:
            weight=min(max(0.,p.requested_weight),genes.max_new_weight,max(0.,cash-genes.min_cash))
            if weight>0:result[ticker]=("ENTER",weight,p.chromosome_id);cash-=weight
    return result
