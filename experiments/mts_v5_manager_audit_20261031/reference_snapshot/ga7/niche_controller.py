"""Daily GA7 niche arbitration, independent memberships with one controller."""
from math import isfinite

def controlling_niche(distances, radii, identifiers, previous=None, switch_margin=0.05):
    """Return (controller, qualifying niches ordered by normalized distance).

    Distances/radii are aligned by center. Only centers within their frozen
    radius qualify. Switch only if challenger improves normalized distance
    by more than switch_margin; never force a position exit on niche change.
    """
    if len(distances)!=len(radii) or len(radii)!=len(identifiers):
        raise ValueError("Center count mismatch")
    if not isfinite(switch_margin) or switch_margin<0:
        raise ValueError("Invalid switching margin")
    if len(set(identifiers))!=len(identifiers):
        raise ValueError("Duplicate niche identifiers")
    scored=[]
    for niche,d,r in zip(identifiers,distances,radii):
        if not isfinite(d) or not isfinite(r) or d<0 or r<=0:
            raise ValueError("Invalid center distance or radius")
        score=d/r
        if score<=1:
            scored.append((score,str(niche)))
    scored.sort()
    qualified=tuple(n for _,n in scored)
    if not scored:
        return None,qualified
    best_score,best=scored[0]
    previous_score=next((s for s,n in scored if n==previous),None)
    if previous_score is not None and previous_score-best_score<=switch_margin:
        return previous,qualified
    return best,qualified
