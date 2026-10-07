from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from Core.g3.starter import Rule, Specialist, Outcome, quality

@dataclass(frozen=True)
class V3Specialist:
    applicability: Rule
    gate: Rule
    signal: Rule
    side: int
    take_profit: float
    stop_loss: float
    max_horizon: int
    add_at: float
    reduce_at: float
    def validate(self,n_features:int):
        for r in (self.applicability,self.gate,self.signal):
            assert 0 <= r.feature < n_features
        assert self.side in (-1,1) and self.take_profit>0 and self.stop_loss>0 and self.max_horizon>=1
        assert self.add_at>0 and self.reduce_at>0

def stationary_bootstrap_y(y:np.ndarray,seed:int,expected_block:int=50)->np.ndarray:
    y=np.asarray(y); n=len(y)
    if expected_block<2 or n<2: raise ValueError("invalid stationary bootstrap dimensions")
    rng=np.random.default_rng(seed); p=1.0/expected_block
    idx=np.empty(n,dtype=int); idx[0]=int(rng.integers(0,n))
    for i in range(1,n):
        idx[i]=int(rng.integers(0,n)) if rng.random()<p else (idx[i-1]+1)%n
    return y[idx].copy()

def to_v2(g:V3Specialist)->Specialist:
    return Specialist(g.gate,g.signal,g.side,g.take_profit,g.stop_loss,g.max_horizon,g.add_at,g.reduce_at)

def evaluate_v3(g:V3Specialist,features:np.ndarray,future_returns:np.ndarray,cost_bps:float=10.0)->list[Outcome]:
    g.validate(features.shape[1])
    # Preserve row alignment while making applicability a hard causal entry condition.
    base=to_v2(g)
    fire_app=g.applicability.fires(features)
    gate=base.gate.fires(features); signal=base.signal.fires(features)
    # Use an impossible gate value on non-applicable rows without altering future paths.
    # Direct lifecycle implementation remains single-source in starter.evaluate_one.
    from Core.g3.starter import evaluate_one
    outs=[]
    # evaluate_one has no event indices, so mask gate feature rows in a copy.
    x=features.copy(); r=base.gate
    if r.direction>0: x[~fire_app,r.feature]=-np.inf
    else: x[~fire_app,r.feature]=np.inf
    return evaluate_one(base,x,future_returns,cost_bps)
