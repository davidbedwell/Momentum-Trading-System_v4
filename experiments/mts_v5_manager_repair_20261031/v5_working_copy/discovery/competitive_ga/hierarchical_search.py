"""Exhaustive, priority-ordered native candidate routing; no top-N prefilter.

Search tiers are discovery order, NOT portfolio rank. A later-tier match can
outcompete an earlier-tier match. All supplied candidates are visited.
"""
from dataclasses import dataclass
from collections import Counter

TIERS=("NICHE","NO_NICHE","GA4_HORIZONS")

@dataclass(frozen=True)
class RoutedCandidate:
    chromosome_id:str
    family:str
    niche:str|None=None

def tier(candidate,controlling_niche):
    family=candidate.family.upper()
    if family in ("GA4","HORIZONS"):return "GA4_HORIZONS"
    if candidate.niche is None or candidate.niche.upper() in ("NO-NICHE","NO_NICHE"):
        return "NO_NICHE"
    if controlling_niche is not None and candidate.niche==controlling_niche:
        return "NICHE"
    return None

def screen_all(stock_rows,candidates,niche_at_close,feature_gate,native_decision,asof):
    """Return every qualifying native action and full screening counts.

    niche_at_close must be chronological, never retrospectively fit labels.
    Missing niche classification does not suppress NO_NICHE or GA4/HORIZONS.
    """
    groups={name:[] for name in TIERS}
    for candidate in candidates:
        if candidate.family.upper() in ("GA4","HORIZONS"):
            groups["GA4_HORIZONS"].append(candidate)
        elif candidate.niche is None or candidate.niche.upper() in ("NO-NICHE","NO_NICHE"):
            groups["NO_NICHE"].append(candidate)
        else:groups["NICHE"].append(candidate)
    counts=Counter();matches=[]
    for ticker,row in stock_rows.items():
        niche=niche_at_close(ticker,row,asof)
        for name in TIERS:
            for candidate in groups[name]:
                counts["considered_"+name]+=1
                if tier(candidate,niche)!=name:continue
                counts["eligible_"+name]+=1
                if not feature_gate(candidate,row,asof):continue
                counts["evaluated_"+name]+=1
                action,weight=native_decision(candidate,row,None,asof)
                if action in ("ENTER","ADD","REDUCE","EXIT","HOLD"):
                    matches.append((name,ticker,candidate.chromosome_id,action,float(weight or 0)))
                    counts["matched_"+name]+=1
    counts["stocks"]=len(stock_rows)
    counts["matches"]=len(matches)
    return matches,dict(counts)
