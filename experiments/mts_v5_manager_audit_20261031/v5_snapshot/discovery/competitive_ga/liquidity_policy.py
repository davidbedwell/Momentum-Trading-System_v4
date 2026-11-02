"""Causal three-bucket liquidity policy for evolutionary portfolio managers.

Outputs target allocations, not guaranteed same-session settlement or fills.
SGOV is an invested security, never silently treated as settled cash.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class LiquidityGenes:
    base_cash: float = .05
    opportunity_sensitivity: float = .5
    uncertainty_sensitivity: float = .1
    max_cash: float = .25
    sgov_preference: float = .8


def targets(genes, *, near_term_opportunity, uncertainty, active_target,
            sgov_eligible=True):
    values=(genes.base_cash,genes.opportunity_sensitivity,genes.uncertainty_sensitivity,
            genes.max_cash,genes.sgov_preference,near_term_opportunity,uncertainty,active_target)
    if any(not isfinite(v) for v in values) or any(not 0<=v<=1 for v in values):
        raise ValueError('liquidity policy requires finite normalized inputs')
    if genes.base_cash>genes.max_cash:
        raise ValueError('base reserve exceeds cap')
    # Anticipated opportunities and uncertainty can raise immediately available reserve.
    desired=min(genes.max_cash,genes.base_cash+
                genes.opportunity_sensitivity*near_term_opportunity+
                genes.uncertainty_sensitivity*uncertainty)
    active=min(active_target,1-desired)
    remainder=1-active
    cash=desired+(remainder-desired)*(1-genes.sgov_preference if sgov_eligible else 1)
    sgov=remainder-cash
    return {'active':active,'cash':cash,'sgov':sgov}
