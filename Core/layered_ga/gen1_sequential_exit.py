"""Deterministic one-exit trade-path replay; decisions use prior observations only."""
from collections.abc import Callable
from math import isfinite


def replay(entry_price: float, executable_prices: list[float], observed_features: list[dict],
           exit_policy: Callable[[dict], bool], side: int = 1, roundtrip_cost: float = 0.0) -> dict:
    """For session i, decide using features observed before executable_prices[i].

    The last executable price is the forced original-horizon exit. Prices must
    already reflect the actual intended fill convention, including any gaps.
    Returns are in entry-price units; roundtrip_cost is a fractional return.
    """
    if side not in (-1, 1) or not isfinite(entry_price) or entry_price <= 0:
        raise ValueError('invalid entry/side')
    if not executable_prices or len(executable_prices) != len(observed_features):
        raise ValueError('one feature snapshot per executable session required')
    if not isfinite(roundtrip_cost) or roundtrip_cost < 0:
        raise ValueError('invalid cost')
    # Validate the complete counterfactual path before any early exit can mask bad data.
    if any(not isfinite(price) or price <= 0 for price in executable_prices):
        raise ValueError('invalid executable price')
    if any(not isinstance(snapshot, dict) for snapshot in observed_features):
        raise ValueError('invalid observation snapshot')
    for i, (price, snapshot) in enumerate(zip(executable_prices, observed_features)):
        if i == len(executable_prices) - 1 or bool(exit_policy(snapshot)):
            realized = side * (price / entry_price - 1.0) - roundtrip_cost
            horizon = side * (executable_prices[-1] / entry_price - 1.0) - roundtrip_cost
            return {'exit_index': i, 'forced': i == len(executable_prices) - 1,
                    'realized_net': realized, 'horizon_net': horizon,
                    'gain_vs_horizon': realized - horizon,
                    'missed_recovery': max(0.0, horizon - realized),
                    'loss_avoided': max(0.0, realized - horizon)}
    raise AssertionError('unreachable')
