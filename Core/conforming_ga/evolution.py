"""Frozen staged evolutionary mechanics for clean MTS runner."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from .schema import *
from .engine import AllocationMode

STAGES=((0,100,"A"),(100,250,"B"),(250,450,"C"),(450,500,"D"))
MAP_DESCRIPTOR_NAMES=("gross","safe_fraction","short_share","turnover","holdings_hhi","gfc_return","recovery_capture")

def stage_for_generation(g:int)->str:
    for lo,hi,s in STAGES:
        if lo<=g<hi:return s
    if g>=500:return "D"
    raise ValueError(g)

def deterministic_seed(master_seed:str,fold:int,island:int,generation:int)->int:
    b=f"{master_seed}|{fold}|{island}|{generation}".encode()
    return int.from_bytes(hashlib.sha256(b).digest()[:8],"big")

def operator_weights(stage:str)->dict[str,float]:
    base={"family":1.0,"structure":1.0,"context":1.0,"applicability":1.0,"sector":1.0,"lifecycle":1.0,"allocation":1.0,"short":1.0,"robustness":1.0}
    if stage=="B":
        for k in ("context","applicability","sector"):base[k]=2.0
    elif stage=="C":
        for k in ("lifecycle","allocation","short"):base[k]=2.0
    elif stage=="D":base["robustness"]=2.0
    elif stage!="A":raise ValueError(stage)
    return base

def ring_destination(island:int,n_islands:int=9)->int:return (island+1)%n_islands
def migration_count(population_size:int=250)->int:return max(1,int(np.ceil(population_size*.05)))
def plateau_action(consecutive:int)->str:
    return "NONE" if consecutive<=0 else "IMMIGRANTS_20_STRUCTURAL_UPWEIGHT" if consecutive==1 else "FREEZE_REALLOCATE"
def behavioral_distance(a:np.ndarray,b:np.ndarray)->float:
    a=np.asarray(a,float);b=np.asarray(b,float)
    if a.shape!=b.shape:raise ValueError("shape")
    return float(np.sqrt(np.mean((a-b)**2)))
def map_descriptor(metrics:dict[str,float])->tuple[float,...]:
    return tuple(float(metrics[k]) for k in MAP_DESCRIPTOR_NAMES)

def random_genome(seed:int,stock_features=("mom20","mom63","rv20","volume_rel20","earnings_surprise_pct__v1","days_since_earnings__v1","earnings_event_session__v1"),
                  market_features=("spy_ret_5","spy_ret_20","spy_dd","spy_vol_20","ofr_fsi"),
                  sector_features=("peer_ret1","peer_mom20"))->Genome:
    r=np.random.Generator(np.random.PCG64(seed))
    sf=tuple(r.choice(stock_features,size=min(3,len(stock_features)),replace=False))
    mf=tuple(r.choice(market_features,size=min(2,len(market_features)),replace=False))
    secf=tuple(r.choice(sector_features,size=min(1,len(sector_features)),replace=False))
    sts=tuple(StockState(x,float(r.normal())) for x in sf)
    mcs=tuple(MarketContext(x,float(r.normal())) for x in mf)
    scs=tuple(SectorContext(x,float(r.normal())) for x in secf)
    mod=Module(
        family=str(r.choice(["momentum","breakout","trend","mean_reversion","volatility","volume","relative_strength","earnings","market_structure","reversal","pullback","vol_breakout","breadth"])),
        stock_terms=sts,
        market_terms=mcs[:1],
        sector_terms=scs,
        applicability_market=mcs[1:],
        applicability_sector=scs,
    )
    mode=list(AllocationMode)[int(r.integers(0,4))]
    return Genome(mcs,scs,sts,(mod,),OpportunityMap(float(r.normal(0,.01)),float(r.uniform(.1,1.5))),
                  Allocation(mode,float(r.uniform(.05,1)),float(r.normal(0,.02)),float(r.uniform(.5,2)),float(r.uniform(.05,.5))),
                  Lifecycle(float(r.uniform(0,5)),float(r.uniform(0,.1))),
                  ShortPolicy(bool(r.integers(0,2)),float(r.uniform(0,.02))))

def canonical_genome(g:Genome)->str:
    def conv(o):
        if hasattr(o,"value") and isinstance(o,AllocationMode):return o.value
        if hasattr(o,"__dataclass_fields__"):return {k:conv(getattr(o,k)) for k in o.__dataclass_fields__}
        if isinstance(o,tuple):return [conv(x) for x in o]
        return o
    return json.dumps(conv(g),sort_keys=True,separators=(",",":"))

def checkpoint_bytes(master_seed:str,fold:int,island:int,generation:int,population:list[Genome],metrics:list[dict])->bytes:
    payload={"seed":deterministic_seed(master_seed,fold,island,generation),"fold":fold,"island":island,"generation":generation,
             "population":[canonical_genome(g) for g in population],"metrics":metrics}
    return json.dumps(payload,sort_keys=True,separators=(",",":")).encode()

def checkpoint_hash(*args,**kwargs)->str:return hashlib.sha256(checkpoint_bytes(*args,**kwargs)).hexdigest()


def genome_from_canonical(raw:str)->Genome:
    d=json.loads(raw)
    mc=tuple(MarketContext(**x) for x in d["market_contexts"])
    sc=tuple(SectorContext(**x) for x in d["sector_contexts"])
    ss=tuple(StockState(**x) for x in d["stock_states"])
    mods=[]
    for m in d["modules"]:
        mods.append(Module(m["family"],tuple(StockState(**x) for x in m["stock_terms"]),
            tuple(MarketContext(**x) for x in m["market_terms"]),
            tuple(SectorContext(**x) for x in m["sector_terms"]),
            tuple(MarketContext(**x) for x in m["applicability_market"]),
            tuple(SectorContext(**x) for x in m["applicability_sector"])))
    om=OpportunityMap(**d["opportunity_map"])
    a=dict(d["allocation"]);a["mode"]=AllocationMode(a["mode"]);al=Allocation(**a)
    return Genome(mc,sc,ss,tuple(mods),om,al,Lifecycle(**d["lifecycle"]),ShortPolicy(**d["short_policy"]))
