"""Frozen staged evolutionary mechanics for clean MTS runner."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, numpy as np

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
    # Relative engineering rates; preserve frozen stage emphasis without scientific thresholds.
    base={"family":1.0,"structure":1.0,"context":1.0,"applicability":1.0,"sector":1.0,"lifecycle":1.0,"allocation":1.0,"short":1.0,"robustness":1.0}
    if stage=="B":
        for k in ("context","applicability","sector"):base[k]=2.0
    elif stage=="C":
        for k in ("lifecycle","allocation","short"):base[k]=2.0
    elif stage=="D":
        base["robustness"]=2.0
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
