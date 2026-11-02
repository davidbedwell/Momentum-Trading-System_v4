"""Research portfolio manager V3: calibrated proposal competition and replacement.
Replacement sells are queued for next open; proceeds are NOT spendable until
settlement. Execution kernel must enforce cash, risk, defense and order validity.
"""
from discovery.competitive_ga.manager_policy_v2 import Proposal,Genes
from collections import defaultdict
from math import isfinite

def decide(proposals,holdings,settled_cash,genes=Genes(),defense=False):
    if not 0<=settled_cash<=1 or any(not 0<=w<=1 for w in holdings.values()):
        raise ValueError("invalid portfolio")
    if defense:
        return {t:("EXIT",0.,"DEFENSE") for t,w in holdings.items() if w>0}
    groups=defaultdict(list)
    for p in proposals:
        if p.action not in ("ENTER","INCREASE","HOLD","REDUCE","EXIT","PASS"):
            raise ValueError("invalid action")
        if any(not isfinite(float(v)) for v in (p.edge,p.downside,p.confidence,p.target)):
            raise ValueError("nonfinite")
        if p.matured_samples<0 or not 0<=p.confidence<=1 or not 0<=p.target<=1:
            raise ValueError("invalid bounds")
        if p.calibrated and p.matured_samples>0:groups[p.ticker].append(p)
    ranked={}
    for ticker,ps in groups.items():
        families={p.family for p in ps if p.action in ("ENTER","INCREASE","HOLD")}
        bonus=genes.agreement_bonus*max(0,len(families)-1)
        def score(p):
            return p.edge-genes.risk_penalty*max(0,p.downside)+(bonus*p.confidence if p.action in ("ENTER","INCREASE") else 0)
        buy=max((p for p in ps if p.action in ("ENTER","INCREASE")),key=score,default=None)
        # A negative-score reduction/exit is not automatically preferable to HOLD.
        # Explicit EXIT remains a candidate; action competition requires comparing
        # its incremental benefit, not merely the existence of an exit signal.
        manage=max((p for p in ps if p.action in ("EXIT","REDUCE")),key=score,default=None)
        hold=max((p for p in ps if p.action=="HOLD"),key=score,default=None)
        incumbent=max((score(p) for p in (buy,hold) if p is not None),default=float("-inf"))
        # Management proposal's calibrated edge represents incremental benefit
        # relative to retaining exposure, not a mandatory liquidation order.
        if manage is not None and score(manage)<=max(0.,incumbent):
            manage=None
        ranked[ticker]=(incumbent,buy,manage)
    out={}
    for ticker,held in holdings.items():
        if held<=0:continue
        edge,buy,manage=ranked.get(ticker,(float("-inf"),None,None))
        if manage:
            out[ticker]=(manage.action,0. if manage.action=="EXIT" else min(held,manage.target),manage.chromosome_id)
    # Consider opportunity-cost replacements; a replacement is a sell request
    # only. Its proceeds cannot finance the new entry in this decision cycle.
    available_new=sorted(((e,t,p) for t,(e,p,m) in ranked.items()
                         if t not in holdings and p and p.action=="ENTER" and e>=genes.min_edge),
                         reverse=True)
    if available_new:
        challenger_edge,challenger,_=available_new[0]
        for ticker,held in holdings.items():
            if held<=0 or ticker in out:continue
            incumbent_edge,buy,_=ranked.get(ticker,(float("-inf"),None,None))
            if incumbent_edge==float("-inf"):continue  # no reliable incumbent valuation
            if challenger_edge>incumbent_edge+genes.replace_margin:
                out[ticker]=("EXIT",0.,f"REPLACE_FOR:{challenger}")
    cash=max(0.,settled_cash-genes.min_cash)
    for edge,ticker,p in sorted(((e,t,p) for t,(e,p,m) in ranked.items() if p),reverse=True):
        if edge<genes.min_edge or ticker in out:continue
        held=holdings.get(ticker,0.)
        if held:
            if p.action!="INCREASE":continue
            target=min(genes.max_total,max(held,p.target))
            add=min(cash,target-held)
            if add>0:out[ticker]=("INCREASE",held+add,p.chromosome_id);cash-=add
        elif p.action=="ENTER":
            add=min(cash,genes.max_initial,p.target)
            if add>0:out[ticker]=("ENTER",add,p.chromosome_id);cash-=add
    return out
