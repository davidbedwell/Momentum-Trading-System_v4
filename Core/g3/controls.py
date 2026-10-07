from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
import hashlib,json
from typing import Iterable
import numpy as np
from Core.g3.starter import temporal_block_permute,guarded_circular_shift,datewise_cross_sectional_permute

NULL_FAMILIES=("N1_TEMPORAL_BLOCK","N2_DATEWISE_CROSS_SECTION","N3_GUARDED_SHIFT")

def apply_single_ticker_null(y:np.ndarray,family:str,seed:int)->np.ndarray:
    if family=="N1_TEMPORAL_BLOCK": return temporal_block_permute(y,seed,20)
    if family=="N3_GUARDED_SHIFT": return guarded_circular_shift(y,seed,60)
    if family=="N2_DATEWISE_CROSS_SECTION":
        raise ValueError("N2 requires aligned multi-ticker outcomes")
    raise ValueError(f"unknown null family {family}")

def apply_aligned_n2(y_by_ticker:np.ndarray,seed:int,buckets:np.ndarray|None=None)->np.ndarray:
    return datewise_cross_sectional_permute(y_by_ticker,seed,buckets)

@dataclass(frozen=True)
class SearchAttempt:
    run_id:str; arm:str; null_family:str|None; generations:int; population:int; tickers:int
    ticker_evaluations:int; seed:int; outcome_reviewed:bool

class SearchLedger:
    def __init__(self): self._rows:list[SearchAttempt]=[]
    def add(self,a:SearchAttempt)->None:
        if any(x.run_id==a.run_id and x.arm==a.arm for x in self._rows):
            raise ValueError("duplicate run/arm ledger entry")
        self._rows.append(a)
    @property
    def attempts(self): return tuple(self._rows)
    @property
    def total_ticker_evaluations(self): return sum(x.ticker_evaluations for x in self._rows)
    @property
    def reviewed_attempts(self): return sum(bool(x.outcome_reviewed) for x in self._rows)
    def to_dict(self): return {"attempts":[asdict(x) for x in self._rows],"total_ticker_evaluations":self.total_ticker_evaluations,"reviewed_attempts":self.reviewed_attempts}

@dataclass(frozen=True)
class FrozenCandidate:
    candidate_id:str; genome_hash:str; scope_hash:str; source_run_id:str

def stable_hash(payload)->str:
    b=json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()
    return hashlib.sha256(b).hexdigest()

def freeze_candidate(candidate_id:str,genome:dict,scope:dict,source_run_id:str)->FrozenCandidate:
    return FrozenCandidate(candidate_id,stable_hash(genome),stable_hash(scope),source_run_id)

def assert_validation_barrier(candidate:FrozenCandidate,genome:dict,scope:dict,protected_loaded:bool)->None:
    if not protected_loaded: raise ValueError("protected validation data not explicitly loaded")
    if stable_hash(genome)!=candidate.genome_hash: raise ValueError("genome changed after freeze")
    if stable_hash(scope)!=candidate.scope_hash: raise ValueError("scope changed after freeze")
