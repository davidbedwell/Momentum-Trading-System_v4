"""Causal portfolio decision policy, version 2 (research).
Orders are target weights at next open. No sale proceeds are recycled at
decision time: cash from future fills is not yet settled.
"""
from dataclasses import dataclass
from math import isfinite
from collections import defaultdict

@dataclass(frozen=True)
class Proposal:
    ticker:str
    chromosome_id:str
    family:str
    action:str
    edge:float
    downside:float
    confidence:float
    target:float
    calibrated:bool
    matured_samples:int

@dataclass(frozen=True)
class Genes:
    min_edge:float=.01
    risk_penalty:float=1.
    replace_margin:float=.02
    agreement_bonus:float=.01
    max_initial:float=.10
    max_total:float=.30
    min_cash:float=0.

def decide(proposals,holdings,settled_cash,genes=Genes(),defense=False):
    """Return next-open target weights and provenance; no fabricated returns.
    Uncalibrated candidates may be shadow-evaluated but cannot win capital.
    Exits from existing owners have precedence over unrelated entry signals.
    """
    if not 0<=settled_cash<=1:raise ValueError("cash")
    if any(not 0<=w<=1 for w in holdings.values()):raise ValueError("holdings")
    if defense:return {t:("EXIT",0.,"DEFENSE") for t,w in holdings.items() if w>0}
    grouped=defaultdict(list)
    for p in proposals:
        if p.action not in ("ENTER","INCREASE","HOLD","REDUCE","EXIT","PASS"):raise ValueError("action")
        if p.matured_samples<0 or any(not isfinite(float(x)) for x in (p.edge,p.downside,p.confidence,p.target)):raise ValueError("invalid proposal")
        if not 0<=p.confidence<=1 or not 0<=p.target<=1:raise ValueError("bounds")
        if p.calibrated and p.matured_samples>0:grouped[p.ticker].append(p)
    out={}
    scored=[]
    for ticker,ps in grouped.items():
        held=holdings.get(ticker,0.)
        # Independent families reinforce only the entry/increase side.
        families={p.family for p in ps if p.action in ("ENTER","INCREASE","HOLD")}
        bonus=genes.agreement_bonus*max(0,len(families)-1)
        def score(p):
            return p.edge-genes.risk_penalty*max(0,p.downside)+(bonus*p.confidence if p.action in ("ENTER","INCREASE") else 0.)
        exits=[p for p in ps if p.action in ("EXIT","REDUCE")]
        if held and exits:
            x=max(exits,key=score)
            if x.action=="EXIT":out[ticker]=("EXIT",0.,x.chromosome_id)
            else:out[ticker]=("REDUCE",min(held,x.target),x.chromosome_id)
            continue
        buys=[p for p in ps if p.action in ("ENTER","INCREASE")]
        if buys:
            best=max(buys,key=score)
            scored.append((score(best),ticker,best))
    # Existing holdings have an opportunity cost. Replacement is only suggested,
    # never funded from unsettled sale proceeds.
    scored.sort(key=lambda x:(-x[0],x[1]))
    cash=max(0.,settled_cash-genes.min_cash)
    for score,ticker,p in scored:
        held=holdings.get(ticker,0.)
        if score<genes.min_edge:continue
        if held:
            target=min(genes.max_total,max(held,p.target))
            add=min(target-held,cash)
            if add>0:
                out[ticker]=("INCREASE",held+add,p.chromosome_id)
                cash-=add
        elif p.action=="ENTER":
            amount=min(p.target,genes.max_initial,cash)
            if amount>0:
                out[ticker]=("ENTER",amount,p.chromosome_id)
                cash-=amount
    return out
