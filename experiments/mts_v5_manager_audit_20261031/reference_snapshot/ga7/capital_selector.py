"""GA7 research capital competition. Decisions use only previously observed scores.

Portfolio executor must implement next-open fills, defense and settled cash.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Candidate:
    ticker: str
    score: float
    sector: str
    weight: float
    held: bool = False

def allocate(candidates, *, slots=10, sector_limit=3, max_weight=.30,
             replacement_margin=.005, cost_roundtrip=.002):
    """Return desired holdings, exits and rejected candidates.

    Turnover requires a strictly positive score advantage above estimated costs.
    Deterministic and order-invariant; no horizon or age restriction.
    """
    if not 1 <= slots <= 10 or not 1 <= sector_limit <= 3:
        raise ValueError("Invalid capacity")
    by_ticker = {}
    for c in candidates:
        if not c.ticker or not isfinite(c.score) or not 0 < c.weight <= max_weight:
            raise ValueError("Invalid candidate")
        if c.ticker in by_ticker:
            raise ValueError("Duplicate ticker")
        by_ticker[c.ticker] = c
    held = sorted((c for c in candidates if c.held), key=lambda c:(-c.score,c.ticker))
    new = sorted((c for c in candidates if not c.held), key=lambda c:(-c.score,c.ticker))
    chosen = []
    def sector_ok(c, pool):
        return sum(x.sector == c.sector for x in pool) < sector_limit
    for c in held:
        if len(chosen) < slots and sector_ok(c,chosen):
            chosen.append(c)
    for c in new:
        if c.score <= 0:
            continue
        if len(chosen) < slots and sector_ok(c,chosen):
            chosen.append(c)
            continue
        victims = [x for x in chosen if x.held and
                   (x.sector == c.sector or sector_ok(c,chosen))]
        if not victims:
            continue
        victim = min(victims,key=lambda x:(x.score,x.ticker))
        if c.score > victim.score + replacement_margin + cost_roundtrip:
            chosen.remove(victim)
            if sector_ok(c,chosen):
                chosen.append(c)
            else:
                chosen.append(victim)
    selected = {c.ticker for c in chosen}
    return {"holdings": sorted(selected),
            "exits": sorted(c.ticker for c in held if c.ticker not in selected),
            "rejected": sorted(c.ticker for c in candidates if c.ticker not in selected)}
