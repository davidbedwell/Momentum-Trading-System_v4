"""Deterministic next-open priority for a single shared cash account.
Exits/reductions free exposure first; entries compete by signal utility.
"""

def prioritize_pending(proposals):
    priority={'EXIT':0,'REDUCE':1,'HOLD':2,'INCREASE':3,'ENTER':4,'PASS':5}
    return sorted(proposals,key=lambda p:(priority[p.action],
        -(p.probability*p.expected_net_return-(1-p.probability)*p.downside_risk),
        -p.confidence,p.ticker,p.chromosome_id))
