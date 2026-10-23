"""Causal feature adapter for the precomputed GA6-H research panel.
Forward-return labels are intentionally never accessed.
Unsupported features fail closed rather than being approximated silently.
"""
import math
from context_free_genome import validate_tree
from context_scoring import score_tree


def required_leaves(tree):
    return validate_tree(tree)


def feature_value(row, family, window):
    if family == 'momentum': key=f'return_{window}'
    elif family == 'reversal': key=f'return_{window}'
    elif family == 'volatility': key=f'volatility_{window}'
    elif family == 'volume': key=f'volume_ratio_{window}'
    elif family in ('acceleration','trend','liquidity','relative_strength','sector_strength','breadth'):
        # These families require separately computed, close-t causal indicators.
        # Do not substitute unrelated return or volume fields.
        key=f'{family}_{window}'
    else: return None
    v=row.get(key)
    if v is None or not math.isfinite(float(v)):return None
    return -float(v) if family=='reversal' else float(v)


def score_session(genome, rows):
    """rows contain only same-day, close-known inputs; cross-section fit at that date."""
    genome.validate()
    leaves=required_leaves(genome.tree)
    raw={}
    for row in rows:
        sym=row['symbol']
        raw[sym]={}
        for family,window,transform,_,_ in leaves:
            raw[sym][(family,window)]=feature_value(row,family,window)
    keys={(f,w) for f,w,_,_,_ in leaves}
    stats={}
    for key in keys:
        values=sorted(v[key] for v in raw.values() if v.get(key) is not None)
        if not values:continue
        mean=sum(values)/len(values)
        sd=(sum((x-mean)**2 for x in values)/len(values))**.5
        stats[key]=(mean,sd,values)
    result=[]
    for sym,values in raw.items():
        features={}
        for family,window,transform,_,_ in leaves:
            key=(family,window)
            if key not in stats or values.get(key) is None:continue
            v=values[key];mean,sd,ordered=stats[key]
            if transform=='raw':value=v
            elif transform=='zscore':value=(v-mean)/sd if sd else 0.0
            else:
                from bisect import bisect_left,bisect_right
                value=((bisect_left(ordered,v)+bisect_right(ordered,v))/2)/len(ordered)
            features[(family,window,transform)]=value
        score=score_tree(genome.tree,features)
        if score is None or not score[0] or score[1]<genome.entry_threshold:continue
        margin=score[1]
        if genome.rank_method=='count':margin=1.0
        result.append({'symbol':sym,'score':float(margin)})
    return sorted(result,key=lambda r:(-r['score'],r['symbol']))
