"""Point-in-time, long-only portfolio risk gate. Proposals only; no simulated fills."""
from dataclasses import dataclass
from collections import defaultdict
import math
import numpy as np

@dataclass(frozen=True)
class RiskPolicy:
    max_stock: float = .10
    max_sector: float = .30
    max_names_per_sector: int = 3
    max_gross: float = 1.0
    correlation_lookback: int = 60
    correlation_threshold: float = .80
    max_correlated_cluster: float = .30
    min_observations: int = 40
    fee_rate: float = .001


def _corr(a, b, *, asof, lookback, min_obs):
    """Return trailing daily-return correlation; never use prices dated after asof."""
    a = {str(k):float(v) for k,v in a.items() if str(k)<=asof and math.isfinite(float(v))}
    b = {str(k):float(v) for k,v in b.items() if str(k)<=asof and math.isfinite(float(v))}
    dates = sorted(set(a)&set(b))[-lookback:]
    if len(dates)<min_obs:return None
    x=np.array([a[k] for k in dates]); y=np.array([b[k] for k in dates])
    if np.std(x)<1e-12 or np.std(y)<1e-12:return None
    return float(np.corrcoef(x,y)[0,1])


def allocate(candidates, *, asof, cash, nav, holdings, sector_by_symbol, trailing_returns, policy=RiskPolicy()):
    """Ranked, cash-funded target weights; no credit for pending sale proceeds.

    candidates: {symbol, chromosome, niche, score, target_weight, evidence_cutoff}.
    holdings: symbol -> current NAV weight. Positions are retained unless explicit target
    reduction supplied by a candidate; reductions are emitted before additions.
    Correlation clusters use connected components of |rho| >= threshold.
    """
    if nav<=0 or cash<0:raise ValueError('invalid account')
    if any(v<0 or not math.isfinite(v) for v in holdings.values()):raise ValueError('invalid holding')
    if sum(holdings.values())>policy.max_gross+1e-8:raise ValueError('existing gross above limit')
    if policy.min_observations>policy.correlation_lookback:raise ValueError('lookback too short')
    winners={}
    shadow=[]
    for p in candidates:
        s=p['symbol']; cutoff=str(p['evidence_cutoff'])
        if cutoff>asof:raise ValueError('future evidence')
        if s not in sector_by_symbol:raise ValueError('unknown sector '+s)
        if s not in trailing_returns:raise ValueError('missing return history '+s)
        if not all(math.isfinite(float(p[k])) for k in ('score','target_weight')):raise ValueError('invalid score')
        if not 0<=p['target_weight']<=policy.max_stock+1e-9:raise ValueError('invalid target')
        shadow.append(dict(p))
        if s not in winners or (p['score'],-p['chromosome'])>(winners[s]['score'],-winners[s]['chromosome']):winners[s]=p
    for s in holdings:
        if s not in sector_by_symbol or s not in trailing_returns:raise ValueError('missing existing holding metadata '+s)
    # Build correlation graph over every current/proposed stock. Conservative treatment
    # of negative correlation: use absolute correlation for shared-factor exposure.
    symbols=sorted(set(holdings)|set(winners))
    edges={s:set() for s in symbols}; pairs=[]
    for i,a in enumerate(symbols):
        for b in symbols[i+1:]:
            rho=_corr(trailing_returns[a],trailing_returns[b],asof=asof,lookback=policy.correlation_lookback,min_obs=policy.min_observations)
            if rho is not None and abs(rho)>=policy.correlation_threshold:
                edges[a].add(b);edges[b].add(a);pairs.append((a,b,rho))
    clusters=[];seen=set()
    for s in symbols:
        if s in seen:continue
        stack=[s];cluster=set()
        while stack:
            z=stack.pop()
            if z in cluster:continue
            cluster.add(z);stack.extend(edges[z]-cluster)
        seen.update(cluster);clusters.append(cluster)
    by_cluster={s:i for i,c in enumerate(clusters) for s in c}
    weights=dict(holdings); orders=[]
    # First release target weights logically, but DO NOT use expected proceeds as buying power.
    for s,p in sorted(winners.items()):
        old=weights.get(s,0.0)
        if p['target_weight']<old:
            weights[s]=p['target_weight']
            orders.append(dict(symbol=s,action='REDUCE',target_weight=p['target_weight'],chromosome=p['chromosome'],execute_not_before='next_session'))
    remaining=cash
    for p in sorted(winners.values(),key=lambda p:(-p['score'],p['symbol'],p['chromosome'])):
        s=p['symbol']; old=weights.get(s,0.0)
        if p['score']<=0 or p['target_weight']<=old:continue
        sector=sector_by_symbol[s]
        sec_weight=sum(w for k,w in weights.items() if sector_by_symbol[k]==sector)
        sec_names=sum(w>1e-10 for k,w in weights.items() if sector_by_symbol[k]==sector)
        if old<=1e-10 and sec_names>=policy.max_names_per_sector:continue
        cluster_weight=sum(weights.get(k,0) for k in clusters[by_cluster[s]])
        gross=sum(weights.values())
        increment=min(p['target_weight']-old,policy.max_stock-old,policy.max_sector-sec_weight,policy.max_correlated_cluster-cluster_weight,policy.max_gross-gross,remaining/nav/(1+policy.fee_rate))
        if increment<=1e-10:continue
        weights[s]=old+increment;remaining-=increment*nav*(1+policy.fee_rate)
        orders.append(dict(symbol=s,action='ADD' if old>0 else 'ENTER',incremental_weight=increment,target_weight=weights[s],chromosome=p['chromosome'],niche=p['niche'],score=p['score'],execute_not_before='next_session'))
    return dict(asof=asof,orders=orders,proposed_weights=weights,remaining_cash=remaining,shadow_decisions=shadow,correlated_pairs=pairs,correlation_clusters=[sorted(x) for x in clusters],execution_status='PROPOSALS_ONLY')
