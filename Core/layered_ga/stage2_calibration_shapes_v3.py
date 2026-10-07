"""Deterministic full-horizon planted calibration profiles."""
import numpy as np

SHAPES = {
    "FAST": (1, 3, 7, 12),
    "MEDIUM": (3, 10, 20, 30),
    "SLOW": (8, 25, 45, 60),
}


def planted_profile(shape, horizons=63):
    a, b, c, d = SHAPES[shape]
    if not (1 <= a < b < c < d < horizons):
        raise ValueError("invalid frozen plateau geometry")
    # FAST begins on day one: it must not create duplicate x coordinates.
    if a == 1:
        knots = ((1, 0.0), (b, 1.0), (c, 1.0), (d, 0.0), (horizons, 0.0))
    else:
        knots = ((1, 0.0), (a, 0.0), (b, 1.0), (c, 1.0),
                 (d, 0.0), (horizons, 0.0))
    x, y = zip(*knots)
    return np.interp(np.arange(1, horizons + 1), x, y)
