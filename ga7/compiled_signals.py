"""Compiled signal-selection kernel, not a replacement for GA6 portfolio accounting."""
import numpy as np
try:
    from numba import njit
except ImportError:
    def njit(*args, **kwargs):
        raise ImportError("numba required; compiled execution must not silently fall back")

@njit(cache=True)
def scan_signals(features, present, eligible, defense, a, b, ta, tb, use_and):
    """Signals at close t, candidate eligibility at next open t+1.

    Eligibility for the following session is passed explicitly; PIT provenance
    must be certified separately. NaN features cannot trigger trades.
    """
    n_days, n_stocks, _ = features.shape
    signals = np.zeros((n_days, n_stocks), dtype=np.bool_)
    for day in range(n_days - 1):
        if defense[day]:
            continue
        for stock in range(n_stocks):
            if not present[day, stock] or not present[day + 1, stock]:
                continue
            if not eligible[day + 1, stock]:
                continue
            x = features[day, stock, a]
            y = features[day, stock, b]
            if not np.isfinite(x) or not np.isfinite(y):
                continue
            p = x >= ta
            q = y >= tb
            if (p and q) if use_and else (p or q):
                signals[day + 1, stock] = True
    return signals
