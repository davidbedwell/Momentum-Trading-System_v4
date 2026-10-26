"""Track GA7 chromosome-level improvement without portfolio risk gates."""
import math
from ga7.engine import breeding_eligible

def feasible_signature(results, **_unused):
    """Track only eligible chromosome fitness frontier."""
    points = []
    for m in results:
        if not breeding_eligible(m):
            continue
        vals = (m.get("fitness"), m.get("return_per_session"), m.get("mae"))
        if all(v is not None and math.isfinite(float(v)) for v in vals):
            points.append((round(float(vals[0]), 5),
                           round(float(vals[1]), 6),
                           round(float(vals[2]), 4)))
    return sorted(set(points))

def frontier_improved(current, historical):
    return any(not any(all(h >= v for h, v in zip(old, point))
                       for old in historical) for point in current)

def update_stagnation(results, frontier, stagnant, **_unused):
    current = feasible_signature(results)
    improved = frontier_improved(current, frontier)
    if improved:
        union = sorted(set(map(tuple, frontier)) | set(current))
        frontier = [p for p in union if not any(
            q != p and all(a >= b for a, b in zip(q, p)) for q in union)]
    return frontier, 0 if improved else stagnant + 1, improved
