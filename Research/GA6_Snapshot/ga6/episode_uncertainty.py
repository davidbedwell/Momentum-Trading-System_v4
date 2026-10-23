from collections import defaultdict
from statistics import mean
from math import log1p
import random

def assess(trades,seed=6106,resamples=400):
    groups=defaultdict(list)
    for t in trades:
        groups[str(t['entry_date'])[:7]].append(float(t['net_return']))
    blocks=list(groups.values())
    if len(blocks)<12:
        return {'eligible':False,'independent_months':len(blocks)}
    rng=random.Random(seed)
    # Cache per-block sums; retain the exact bootstrap draw sequence and
    # the same trade-weighted means, without re-logging each trade 400 times.
    stats=[(len(b),sum(b),sum(log1p(v) for v in b)) for b in blocks]
    samples=[]
    for _ in range(resamples):
        drawn=[rng.randrange(len(blocks)) for _ in blocks]
        count=sum(stats[i][0] for i in drawn)
        samples.append((sum(stats[i][1] for i in drawn)/count,
                        sum(stats[i][2] for i in drawn)/count))
    ev=sorted(x[0] for x in samples)[int(resamples*.025)]
    ge=sorted(x[1] for x in samples)[int(resamples*.025)]
    return {'eligible':True,'independent_months':len(blocks),'ev_ci95_lower':ev,'log_ev_ci95_lower':ge,'robust_positive':ev>0 and ge>0}
