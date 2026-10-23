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
    samples=[]
    for _ in range(resamples):
        vals=[v for _ in blocks for v in rng.choice(blocks)]
        samples.append((mean(vals),mean(log1p(v) for v in vals)))
    ev=sorted(x[0] for x in samples)[int(resamples*.025)]
    ge=sorted(x[1] for x in samples)[int(resamples*.025)]
    return {'eligible':True,'independent_months':len(blocks),'ev_ci95_lower':ev,'log_ev_ci95_lower':ge,'robust_positive':ev>0 and ge>0}
