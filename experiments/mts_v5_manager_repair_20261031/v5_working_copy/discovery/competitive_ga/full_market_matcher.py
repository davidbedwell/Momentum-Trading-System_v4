"""Full-universe matching at close t, without global top-N truncation."""
from dataclasses import dataclass
from collections import defaultdict

@dataclass(frozen=True)
class Match:
    session: str
    ticker: str
    chromosome_id: str
    action: str
    requested_weight: float

def match_all(asof, stock_rows, library, feature_gate, native_decision,
              *, held_states=None, allowed_actions=("ENTER","ADD","REDUCE","EXIT","HOLD")):
    """Every stock and every eligible chromosome. Caller supplies causal features
    and lossless native eligibility; this does not execute orders.
    """
    held_states=held_states or {}
    matches=[]
    counts=defaultdict(int)
    for ticker,row in stock_rows.items():
        counts["stocks_read"]+=1
        applicable=0
        for candidate in library:
            if not feature_gate(candidate,row,asof):
                continue
            applicable+=1
            counts["native_evaluations"]+=1
            held=held_states.get((ticker,candidate.chromosome_id))
            action,weight=native_decision(candidate,row,held,asof)
            if action in allowed_actions:
                matches.append(Match(str(asof),str(ticker),candidate.chromosome_id,
                                     action,float(weight or 0)))
        counts["applicable_pairs"]+=applicable
        if applicable==0:counts["stocks_without_applicable"]+=1
    counts["matches"]=len(matches)
    return matches,dict(counts)
