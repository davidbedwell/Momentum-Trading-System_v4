"""GA7 stagnation tracker using feasible, risk-aware Pareto progress."""
import math

def feasible_signature(results, *, max_mdd=.20, min_trades=20):
    """Monotone two-dimensional frontier: CAGR and Calmar among feasible genomes.

    Quantization prevents floating point noise from resetting stagnation.
    """
    points=[]
    for m in results:
        c=float(m.get("cagr") or 0)
        d=float(m.get("mdd") or 0)
        k=float(m.get("calmar") or 0)
        if (all(math.isfinite(x) for x in (c,d,k))
            and 0 < d <= max_mdd and c > 0 and m.get("trades",0)>=min_trades):
            points.append((round(c,4),round(k,3)))
    return sorted(set(points))

def frontier_improved(current, historical):
    """True if any current feasible point improves on the historical frontier."""
    return any(not any(hc>=c and hk>=k for hc,hk in historical)
               for c,k in current)

def update_stagnation(results, frontier, stagnant, *, max_mdd=.20, min_trades=20):
    current=feasible_signature(results,max_mdd=max_mdd,min_trades=min_trades)
    improved=frontier_improved(current,frontier)
    if improved:
        union=sorted(set(frontier)|set(current))
        frontier=[p for p in union if not any(
            q!=p and q[0]>=p[0] and q[1]>=p[1] for q in union)]
    return frontier, 0 if improved else stagnant+1, improved
