"""Mandatory H.7 calibration hooks using the exact same evolve() machinery."""
from __future__ import annotations
import numpy as np
from .ga import evolve,BASE_GENERATIONS,POPULATION_SIZE
from .schema import Genome

def block_permute_returns(returns:np.ndarray,block:int,seed:int)->np.ndarray:
    """Permute time blocks jointly across stocks, preserving within-date cross-sectional structure."""
    r=np.asarray(returns,float);rng=np.random.Generator(np.random.PCG64(seed))
    blocks=[r[i:i+block] for i in range(0,len(r),block)]
    order=rng.permutation(len(blocks))
    return np.concatenate([blocks[i] for i in order],axis=0)[:len(r)]

def run_null(*,evaluator_factory,returns,master_seed,fold,generations=BASE_GENERATIONS,population_size=POPULATION_SIZE):
    null=block_permute_returns(returns,20,int.from_bytes(__import__("hashlib").sha256(f"null|{master_seed}|{fold}".encode()).digest()[:8],"big"))
    evaluator=evaluator_factory(null,kind="null")
    return evolve(evaluator=evaluator,master_seed=f"{master_seed}|NULL",fold=fold,generations=generations,population_size=population_size)

def planted_dataset(seed:int,T:int=1200,N:int=80):
    """Synthetic conditional signal: momentum only pays when breadth-persistence context is high."""
    rng=np.random.Generator(np.random.PCG64(seed))
    context=np.zeros(T); context[1:]=np.clip(.92*context[:-1]+rng.normal(0,.15,T-1),-1,1)
    signal=rng.normal(size=(T,N))
    noise=rng.normal(0,.5,size=(T,N))
    future=noise + (context[:,None]>.25)*.35*signal
    return {"context":context,"signal":signal,"future":future,"planted_feature":"signal","planted_context":"breadth_persistence"}

def planted_recovered(genome:Genome)->bool:
    """Structural recovery criterion: applicability references planted context and signal is used."""
    uses_signal=any(any(t.feature=="signal" for t in m.stock_terms) for m in genome.modules)
    uses_context=any(any(t.feature=="breadth_persistence" for t in m.applicability_market) for m in genome.modules)
    return bool(uses_signal and uses_context)

def run_planted(*,evaluator_factory,master_seed,fold=0,seeds=(0,1,2,3),generations=BASE_GENERATIONS,population_size=POPULATION_SIZE):
    out=[]
    for seed in seeds:
        data=planted_dataset(seed)
        evaluator=evaluator_factory(data,kind="planted")
        result=evolve(evaluator=evaluator,master_seed=f"{master_seed}|PLANTED|{seed}",fold=fold,generations=generations,population_size=population_size)
        genomes=[g for archive in result["archives"].values() for g,_ in archive]
        out.append(any(planted_recovered(g) for g in genomes))
    return {"recovered":out,"passed":sum(out)>=3}
