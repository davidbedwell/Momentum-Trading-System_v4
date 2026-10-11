"""GA4 research horizons: all trading days 1..63 inclusive.

Horizon observation does not imply a fixed holding-period exit.
"""

FORWARD_HORIZONS = tuple(range(1, 64))


def validate_horizons(horizons):
    """Reject sampled, missing, duplicated, or reordered forward horizons."""
    observed = tuple(horizons)
    if observed != FORWARD_HORIZONS:
        raise ValueError("GA4 requires each integer trading-day horizon 1 through 63")
    return observed
