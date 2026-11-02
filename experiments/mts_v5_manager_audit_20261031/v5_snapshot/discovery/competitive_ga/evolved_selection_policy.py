"""Small evolvable selection grammar, not an optimizer or performance claim."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class SelectionGenes:
    fit_bonus: float
    ev_weight: float
    uncertainty_weight: float
    min_edge: float
    momentum_fit_weight: float=0.
    volatility_fit_weight: float=0.
    min_market_momentum: float|None=None
    def __post_init__(self):
        if not all(isfinite(v) for v in (self.fit_bonus,self.ev_weight,self.uncertainty_weight,self.min_edge,self.momentum_fit_weight,self.volatility_fit_weight)):
            raise ValueError('nonfinite genes')
        if self.min_market_momentum is not None and not isfinite(self.min_market_momentum):
            raise ValueError('nonfinite market momentum threshold')
        if self.ev_weight<0 or self.uncertainty_weight<0 or self.min_edge<0:
            raise ValueError('invalid selection genes')

def score(genes,candidate,controlling,matches,estimate,learned=None,market_state=None):
    """None means abstain; learned estimates are from a strict prior-session snapshot."""
    if estimate is None or not isfinite(estimate) or estimate<=0:return None
    if genes.min_market_momentum is not None:
        if market_state is None or market_state.momentum < genes.min_market_momentum:
            return None
    fit=int(controlling is not None and candidate.niche==controlling)
    distance=next((d for n,d in matches if n==candidate.niche),None)
    bucket='NEAR' if distance is not None and distance<=.5 else 'FAR_OR_UNKNOWN'
    key=(candidate.family,candidate.chromosome_id,controlling,'MATCH' if fit else 'OTHER',bucket)
    if learned and learned.get('genome_hashes'):
        digest=learned['genome_hashes'].get((candidate.family,candidate.chromosome_id))
        if digest is None:raise ValueError('missing candidate genome fingerprint')
        key=(candidate.family,candidate.chromosome_id,digest,controlling,'MATCH' if fit else 'OTHER',bucket)
    elif learned and learned.get('estimates'):
        key=(candidate.family,candidate.chromosome_id,None,controlling,'MATCH' if fit else 'OTHER',bucket)
    learned=(learned or {}).get('estimates',{}).get(key)
    edge=learned['net_ev'] if learned else estimate
    uncertainty=learned['uncertainty'] if learned else 0.
    if edge-genes.uncertainty_weight*uncertainty<=genes.min_edge:return None
    state_bonus=0. if market_state is None else (genes.momentum_fit_weight*market_state.momentum+
        genes.volatility_fit_weight*market_state.volatility)
    return genes.ev_weight*edge+(genes.fit_bonus+state_bonus)*fit-genes.uncertainty_weight*uncertainty
