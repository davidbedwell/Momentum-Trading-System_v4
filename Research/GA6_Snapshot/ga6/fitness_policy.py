"""GA6 portfolio-and-policy research fitness. Reject weak or non-positive net EV."""
from math import isfinite

def score(trade,policy,niches=None):
 n=trade['count'];ev=trade['net_ev'];logev=trade['geometric_log_ev']
 if n<50 or ev is None or logev is None or ev<=0 or logev<=0:return -1e6
 if not policy.get('eligible',False):return -1e6
 if niches is not None and not any(x.get('eligible') for x in niches.values()):return -1e6
 delta=policy['mean_incremental'];tail=policy['tail_incremental']
 if not all(isfinite(v) for v in (ev,logev,delta,tail)):return -1e6
 # Score rewards incremental gains, penalizes catastrophic policy outcomes.
 return 100*ev+30*logev+100*delta+30*tail
