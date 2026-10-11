"""Auditable non-scalar Stage-2 calibration phenotype selection.

Keep the two economic objectives independent: net EV and cluster
LCB95; adverse excursion is reported, not a selection objective. Do not substitute a weighted scalar objective.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Phenotype:
    horizon: int
    ev_net: float
    lcb95: float
    mae_mean: float


def nondominated_curve(curve):
    points = []
    for p in curve.points:
        keys = ("ev_net", "lcb95", "mae_mean")
        if not all(np.isfinite(p.get(k, np.nan)) for k in keys):
            continue
        points.append(Phenotype(int(p["horizon"]), *(float(p[k]) for k in keys)))
    front = []
    for p in points:
        if any(
            (q.ev_net >= p.ev_net and q.lcb95 >= p.lcb95)
            and (q.ev_net > p.ev_net or q.lcb95 > p.lcb95)
            for q in points
        ):
            continue
        front.append(p)
    return tuple(front)


def dominates(a, b):
    """Dominance across matched horizons; never exchange EV for drawdown."""
    if a.horizon != b.horizon:
        raise ValueError("only matched-horizon phenotypes can be compared")
    return (
        a.ev_net >= b.ev_net and a.lcb95 >= b.lcb95
        and (a.ev_net > b.ev_net or a.lcb95 > b.lcb95)
    )


def describe_front(curve):
    return [
        {"horizon": p.horizon, "ev_net": p.ev_net,
         "lcb95": p.lcb95, "mae_mean": p.mae_mean}
        for p in nondominated_curve(curve)
    ]
