"""GA5-P research-only niche-isolated portfolio Pareto ranking.
No shadow-trade objectives, no cross-niche domination, no production mutations.
"""
import math
from collections import defaultdict

def portfolio_objectives(item):
    score, genome, result = item
    try:
        c=float(result['cagr_diagnostic'])
        dd=abs(float(result['mdd_diagnostic']))
        fills=int(result.get('fills',0))
    except (KeyError,TypeError,ValueError):
        return None
    if not (math.isfinite(c) and math.isfinite(dd) and 0<=dd<=1 and fills>0):
        return None
    return (c,-dd)

def rank_by_niche(scored):
    groups=defaultdict(list)
    for idx,item in enumerate(scored):
        niche=item[1].niche
        obj=portfolio_objectives(item)
        if obj is not None: groups[niche].append((idx,obj))
    ranks={}
    for niche,items in groups.items():
        remaining=items[:]
        level=0
        while remaining:
            front=[]
            for i,a in remaining:
                if not any(all(bk>=ak for bk,ak in zip(b,a)) and any(bk>ak for bk,ak in zip(b,a)) for j,b in remaining if j!=i):
                    front.append(i)
            if not front: raise AssertionError('No Pareto front')
            ranks.update({i:level for i in front})
            selected=set(front)
            remaining=[x for x in remaining if x[0] not in selected]
            level+=1
    return ranks

def niche_portfolio_selection(scored, per_niche=None):
    ranks=rank_by_niche(scored)
    groups=defaultdict(list)
    for i,item in enumerate(scored):
        if i in ranks:
            groups[item[1].niche].append((ranks[i],-portfolio_objectives(item)[0],-portfolio_objectives(item)[1],item[1].identity(),i))
    chosen={}
    for niche,items in groups.items():
        order=sorted(items)
        chosen[niche]=[scored[x[-1]] for x in (order if per_niche is None else order[:per_niche])]
    return chosen
