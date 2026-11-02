"""Observable close-only market state; never use future returns or regime labels."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class MarketState:
    momentum:float
    volatility:float
    asof_session:int

def state_from_closes(history,session,lookback=5):
    """history includes closes through the current decision close only."""
    if len(history)!=session+1:raise ValueError('future or missing close in state history')
    if len(history)<lookback+1:return MarketState(0.,0.,session)
    recent=history[-lookback-1:]
    if any(not isfinite(v) or v<=0 for v in recent):raise ValueError('invalid close')
    returns=[recent[i]/recent[i-1]-1 for i in range(1,len(recent))]
    mean=sum(returns)/len(returns)
    variance=sum((r-mean)**2 for r in returns)/len(returns)
    return MarketState(recent[-1]/recent[0]-1,variance**.5,session)
