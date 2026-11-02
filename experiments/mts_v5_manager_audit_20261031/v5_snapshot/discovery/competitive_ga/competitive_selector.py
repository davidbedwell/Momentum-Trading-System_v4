"""Research-only cross-family allocator. Estimates must be historical and after costs."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Genes:
    minimum_edge: float
    risk_penalty: float
    reserve_value: float

def select(genes, opportunities):
    """Return key or None; tuples are (key, net_edge, drawdown_cost, alternative_value).
    Alternative value must incorporate incumbent, other opportunities, cash and SGOV.
    Never compare incompatible raw GA6/GA7 native scores.
    """
    if not (0 <= genes.minimum_edge <= 1 and genes.risk_penalty >= 0 and genes.reserve_value >= 0):
        raise ValueError('invalid allocation genes')
    best = None
    floor = max(genes.minimum_edge, genes.reserve_value)
    for key, net, drawdown, alternative in opportunities:
        if not all(isfinite(v) for v in (net, drawdown, alternative)) or drawdown < 0:
            raise ValueError('invalid opportunity evidence')
        utility = net - genes.risk_penalty * drawdown
        if net > genes.minimum_edge and utility > max(floor, alternative):
            best, floor = key, utility
    return best
