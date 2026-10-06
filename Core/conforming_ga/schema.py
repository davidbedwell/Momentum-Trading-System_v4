"""Typed modular genome schema: strict superset of reduced linear ranker."""
from __future__ import annotations
from dataclasses import dataclass, field
from .engine import AllocationMode

@dataclass(frozen=True)
class MarketContext: feature:str; weight:float
@dataclass(frozen=True)
class SectorContext: feature:str; weight:float
@dataclass(frozen=True)
class StockState: feature:str; weight:float
@dataclass(frozen=True)
class Module:
    family:str
    stock_terms:tuple[StockState,...]
    market_terms:tuple[MarketContext,...]=()
    sector_terms:tuple[SectorContext,...]=()
    applicability_market:tuple[MarketContext,...]=()
    applicability_sector:tuple[SectorContext,...]=()
@dataclass(frozen=True)
class OpportunityMap: intercept:float=0.0; scale:float=1.0
@dataclass(frozen=True)
class Allocation:
    mode:AllocationMode=AllocationMode.STRENGTH
    tau:float=1.0; q:float=0.0; gamma:float=1.0; eta:float=1.0
@dataclass(frozen=True)
class Lifecycle: kappa:float=1.0; lambda_u:float=0.0
@dataclass(frozen=True)
class ShortPolicy: enabled:bool=False; extra_hurdle:float=0.0
@dataclass(frozen=True)
class Genome:
    market_contexts:tuple[MarketContext,...]
    sector_contexts:tuple[SectorContext,...]
    stock_states:tuple[StockState,...]
    modules:tuple[Module,...]
    opportunity_map:OpportunityMap
    allocation:Allocation
    lifecycle:Lifecycle
    short_policy:ShortPolicy

def reduced_linear_as_genome(weights:dict[str,float])->Genome:
    """PF-26 nesting: any old sparse linear stock score is representable as one ungated module."""
    terms=tuple(StockState(k,float(v)) for k,v in sorted(weights.items()))
    m=Module("reduced_linear",terms)
    return Genome((),(),terms,(m,),OpportunityMap(),Allocation(),Lifecycle(),ShortPolicy(False))
