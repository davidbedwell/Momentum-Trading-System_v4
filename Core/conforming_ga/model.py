"""Integrated causal opportunity model for conformance tests and production replay."""
from __future__ import annotations
import math
from .schema import Genome
from .engine import Opportunity
from .claims import frozen_claims

def _dot(terms, values):
    return sum(t.weight*float(values.get(t.feature,0.0)) for t in terms)

def _group_values(group, ticker):
    if not group:return {}
    v=group.get(ticker)
    return v if isinstance(v,dict) else group

def opportunity_values(genome:Genome, *, market:dict, sector:dict, stock:dict):
    """Sector argument is the contextual group layer and may be per-stock mapping.
    Formal sector labels never enter directly, only causal group measurements.
    """
    mctx=_dot(genome.market_contexts,market)
    out={}
    for ticker,features in stock.items():
        group=_group_values(sector,ticker)
        gctx=_dot(genome.sector_contexts,group)
        total=0.0
        for mod in genome.modules:
            z=_dot(mod.stock_terms,features)+_dot(mod.market_terms,market)+_dot(mod.sector_terms,group)
            app_raw=_dot(mod.applicability_market,market)+_dot(mod.applicability_sector,group)
            app=1.0/(1.0+math.exp(-app_raw)) if (mod.applicability_market or mod.applicability_sector) else 1.0
            total+=app*z
        out[ticker]=genome.opportunity_map.intercept+genome.opportunity_map.scale*(total+mctx+gctx)
    return out

def claims_from_values(genome:Genome, values:dict[str,float], uncertainty:dict[str,float]|None=None,
                       downside:dict[str,float]|None=None):
    uncertainty=uncertainty or {};downside=downside or {}
    ops={k:Opportunity(v,uncertainty.get(k,1.0),downside.get(k,1.0)) for k,v in values.items()}
    return frozen_claims(ops,genome.allocation.mode,tau=genome.allocation.tau,
                         q=genome.allocation.q,gamma=genome.allocation.gamma,eta=genome.allocation.eta)
