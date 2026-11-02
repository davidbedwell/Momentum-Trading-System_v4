"""Close-only causal niche prototype; fixed centers, not a trained production model."""
from .causal_market_state import state_from_closes
from .functional_niche_manager import NicheObservation

CENTERS={'A':(.035,.005),'B':(-.035,.005)}

def classify_closes(history,session,asof,trained_through='2025-12-31'):
    if session<0 or len(history)!=session+1:
        raise ValueError('PIT close history must end at current session')
    state=state_from_closes(history,session)
    distances=tuple((name,((state.momentum-m)**2+(state.volatility-v)**2)**.5)
                    for name,(m,v) in CENTERS.items())
    return NicheObservation(asof,trained_through,'synthetic-close-only-fixed-centers',distances)
