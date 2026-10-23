"""Chronological shadow-learning simulation with immutable original signal snapshots.

Research-only: shadow candidates are independently capitalized; this is NOT
a shared-capital portfolio replay or a production selector.
"""
from collections import defaultdict
from math import sqrt

def chronological_shadow_scores(bank, *, niche, decision_start, decision_end,
                                min_samples=3, prior_strength=10, annual_cash_yield=0.0):
    if not niche or not bank: raise ValueError("bank and niche required")
    if not 0 <= annual_cash_yield < 1: raise ValueError("invalid cash yield")
    observations=[]
    for chromosome,result in bank.items():
        signal_index={(s["decision_date"],s["symbol"]):s
                      for s in result["decisions"]}
        for trade in result["positions"]["completed"]:
            key=(trade["entry_decision_date"],trade["symbol"])
            if key not in signal_index:
                raise ValueError("missing original decision-time evidence")
            signal=signal_index[key]
            if signal["evidence_cutoff"]>key[0]:
                raise ValueError("future evidence")
            if trade["exit_date"]<=key[0]:
                raise ValueError("nonchronological outcome")
            observations.append(dict(chromosome=str(chromosome),niche=niche,
                decision_date=key[0],symbol=key[1],
                maturity_date=trade["exit_date"],net_return=trade["net_return"],
                excess_return=trade["net_return"] - ((1+annual_cash_yield)**(trade["holding_sessions"]/252)-1),
                original_signal_action=signal["action"],
                original_features=signal["features"]))
    dates=sorted({o["decision_date"] for o in observations
                  if decision_start<=o["decision_date"]<decision_end})
    snapshots=[]
    for day in dates:
        # Strictly earlier closure date. Never use current-day or future labels.
        matured=[o for o in observations if o["maturity_date"]<day]
        prior=sum(o["excess_return"] for o in matured)/len(matured) if matured else 0.
        scores={}
        for chromosome in bank:
            values=[o["excess_return"] for o in matured if o["chromosome"]==str(chromosome)]
            if len(values)<min_samples: continue
            n=len(values)
            mean=(sum(values)+prior_strength*prior)/(n+prior_strength)
            sample_mean=sum(values)/n
            variance=sum((v-sample_mean)**2 for v in values)/(n-1) if n>1 else 0.
            score=mean-.5*sqrt(variance/n)
            scores[str(chromosome)]=dict(score=score,samples=n)
        snapshots.append(dict(decision_date=day,
            available_matured_labels=len(matured),scores=scores,
            leader=max(scores,key=lambda k:scores[k]["score"]) if scores else None,
            status="STRICT_PAST_ONLY_EXCESS_TRADE_RETURN_RESEARCH_NOT_SHARED_PORTFOLIO"))
    return snapshots
