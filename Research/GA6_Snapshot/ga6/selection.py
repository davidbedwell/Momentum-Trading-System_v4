"""GA6 research selection primitives. No live trading or retrospective promotion."""
from collections import defaultdict
from math import isfinite, log1p
from statistics import mean
from dataclasses import dataclass

@dataclass(frozen=True)
class TradeEvidence:
    niche: str
    net_return: float
    sessions: int
    baseline_hold_return: float | None = None

def metrics(trades, min_trades=50):
    trades=list(trades)
    n=len(trades)
    if any(not isfinite(t.net_return) or t.net_return <= -1 or t.sessions < 1 for t in trades):
        raise ValueError("Invalid net return or holding period")
    if n < min_trades:
        return {"eligible":False,"count":n,"reason":"INSUFFICIENT_EVIDENCE"}
    returns=[t.net_return for t in trades]
    gains=sum(max(0.,r) for r in returns)
    losses=sum(max(0.,-r) for r in returns)
    ev=mean(returns)
    log_ev=mean(log1p(r) for r in returns)
    tail=mean(sorted(returns)[:max(1,(n+19)//20)])
    days=sum(t.sessions for t in trades)
    counterfactual=[t.net_return-t.baseline_hold_return for t in trades if t.baseline_hold_return is not None]
    return {"eligible":ev>0 and log_ev>0,"count":n,"net_ev":ev,
            "geometric_log_ev":log_ev,"profit_factor":gains/losses if losses else float("inf"),
            "payoff_ratio":(gains/sum(r>0 for r in returns))/(losses/sum(r<0 for r in returns)) if gains and losses else None,
            "win_rate":sum(r>0 for r in returns)/n,"worst_5pct_mean":tail,
            "ev_per_session":sum(returns)/days,
            "exit_incremental_ev":mean(counterfactual) if counterfactual else None,
            "exit_counterfactual_count":len(counterfactual)}

def evaluate_by_niche(trades, niches, min_trades=50):
    grouped=defaultdict(list)
    for t in trades:
        if t.niche not in niches: raise ValueError("Unknown niche")
        grouped[t.niche].append(t)
    return {n:metrics(grouped[n],min_trades) for n in niches}

def rank_within_niche(chromosome_trades, niches, min_trades=50):
    by_niche={n:[] for n in niches}
    for chromosome_id,trades in chromosome_trades.items():
        for niche, m in evaluate_by_niche(trades,niches,min_trades).items():
            if m["eligible"]:
                by_niche[niche].append((chromosome_id,m))
    for niche in niches:
        by_niche[niche].sort(key=lambda item:(-item[1]["net_ev"],-item[1]["geometric_log_ev"],
            -item[1]["worst_5pct_mean"],item[0]))
    return by_niche
