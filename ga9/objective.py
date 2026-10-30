"""Matched outcome labels, frozen conditional expectation and funded excess objective."""
from dataclasses import dataclass
import numpy as np
from .risk import MAX_DRAWDOWN, risk_feasible
from .execution import scores, metrics
from .benchmarks import primary_name

@dataclass(frozen=True)
class HorizonMix:
    sessions: tuple = (5, 20, 60, 120)
    weights: tuple = (.25, .25, .25, .25)

    def __post_init__(self):
        if (len(self.sessions) != len(self.weights) or not self.sessions or
            min(self.sessions) < 1 or min(self.weights) < 0 or
            not np.isclose(sum(self.weights), 1)):
            raise ValueError('Invalid horizon distribution')


def labels(p, horizon, cutoff):
    """Close t decision, next-open entry, exit at open after close t+h.

    Primary is the predeclared SPY/QQQ ETF when attached; unit fixtures can use
    equal cash sleeves until PIT listing,
    with one entry fee and no terminal liquidation. Candidate pays both sides.
    Dividend receivables count in NAV, never compounding. Outcomes are labels only.
    Missing endpoints after listing fail; never filter the universe by future success.
    """
    primary_name(p)  # require a declared ETF outside explicitly marked synthetic fixtures
    n, m = p.close.shape
    relative = np.full((n, m), np.nan)
    absolute = relative.copy()
    entry_factor = 1.0005*1.0001
    exit_factor = .9995*.9999
    for t in range(n-horizon-1):
        endpoint = t+horizon+1
        if p.dates[endpoint] >= np.datetime64(cutoff):
            break
        eligible = np.isfinite(p.close[t])
        if not eligible.any():
            continue
        if not np.isfinite(p.open[t+1,eligible]).all():
            raise ValueError('Missing next open for decision-time eligible symbol')
        if not np.isfinite(p.open[endpoint,eligible]).all():
            raise ValueError('Missing eligible endpoint; refusing survivor filtering')
        # Every symbol has a sleeve, including cash before listing and during a window.
        sleeve = np.zeros(m)
        for j in range(m):
            available = np.flatnonzero(np.isfinite(p.open[t+1:endpoint+1,j]))
            if not len(available):
                continue
            entry = t+1+int(available[0])
            if not np.isfinite(p.open[endpoint,j]):
                raise ValueError('Missing benchmark endpoint after listing')
            div = p.dividends[entry+1:endpoint+1,j].sum()
            sleeve[j] = (p.open[endpoint,j]+div)/(p.open[entry,j]*entry_factor)-1
        passive = sleeve.mean()
        if p.primary_benchmark is not None:
            ref=p.primary_benchmark
            if not ref.dates.equals(p.dates):
                raise ValueError('Primary benchmark calendar differs from strategy')
            div=ref.dividends[t+2:endpoint+1,0].sum()
            passive=(ref.open[endpoint,0]+div)/(ref.open[t+1,0]*entry_factor)-1
        dividends = p.dividends[t+2:endpoint+1].sum(axis=0)
        net = (p.open[endpoint]*exit_factor+dividends)/(p.open[t+1]*entry_factor)-1
        absolute[t,eligible] = net[eligible]
        relative[t,eligible] = net[eligible]-passive
    return relative, absolute


def fit(p, gene, mix, cutoff, min_samples=25, label_cache=None):
    """Fixed score bins, no full-sample quantiles; only matured labels before cutoff."""
    z = scores(p, [gene])[0]
    bins = np.array([-1., 0., .5, 1., 2.])
    index = np.digitize(z, bins)
    model = []
    for h, w in zip(mix.sessions, mix.weights):
        key = (primary_name(p), h, str(cutoff))
        if label_cache is not None and key in label_cache:
            rel, absolute = label_cache[key]
        else:
            rel, absolute = labels(p, h, cutoff)
            if label_cache is not None:
                label_cache[key] = (rel, absolute)
        rows = []
        for b in range(len(bins)+1):
            mask = (index == b) & np.isfinite(z) & (z >= gene.threshold) & np.isfinite(rel)
            count = int(mask.sum())
            rows.append(dict(count=count, relative=float(rel[mask].mean()) if count >= min_samples else 0.,
                             cash=float(absolute[mask].mean()) if count >= min_samples else 0.))
        model.append(dict(horizon=h, weight=w, bins=rows))
    return dict(cutoff=str(cutoff), benchmark=primary_name(p), min_samples=min_samples, boundaries=bins.tolist(), components=model)


def expected(p, gene, model):
    if model.get('benchmark',primary_name(p)) != primary_name(p):
        raise ValueError('Frozen model benchmark mismatch; switching is forbidden')
    z = scores(p, [gene])[0]
    ix = np.digitize(z, model['boundaries'])
    rel, cash = np.zeros_like(z), np.zeros_like(z)
    for component in model['components']:
        # Per-session expected value permits competition across horizon mixtures.
        scale = component['weight']/component['horizon']
        rel += np.array([r['relative'] for r in component['bins']])[ix]*scale
        cash += np.array([r['cash'] for r in component['bins']])[ix]*scale
    return z, rel, cash


def predict(p, gene, model):
    z, rel, cash = expected(p, gene, model)
    edge = np.minimum(rel, cash)
    return np.where(np.isfinite(z) & (z >= gene.threshold) & (edge > 0), edge, -np.inf)



def holding_predict(p, gene, model):
    """Expected value of existing capital: entry costs are sunk, not charged twice.

    Unknown niche/bin forecasts leave native hold/exit management in control.
    Fresh capital, including adds, still requires the net new-entry forecast.
    """
    if model.get('benchmark',primary_name(p)) != primary_name(p):
        raise ValueError('Frozen model benchmark mismatch; switching is forbidden')
    z = scores(p,[gene])[0]
    ix = np.digitize(z,model['boundaries'])
    rel,cash = np.zeros_like(z),np.zeros_like(z)
    support = np.zeros_like(z,dtype=bool)
    entry_factor=1.0005*1.0001
    for c in model['components']:
        a=np.array([r['cash'] for r in c['bins']])[ix]
        r=np.array([r['relative'] for r in c['bins']])[ix]
        known=np.array([r['count']>=model['min_samples'] for r in c['bins']])[ix]
        scale=c['weight']/c['horizon']
        cash+=np.where(known,(a+1)*entry_factor-1,0)*scale
        rel+=np.where(known,r+(a+1)*(entry_factor-1),0)*scale
        support|=known & (c['weight']>0)
    return np.where(np.isfinite(z)&support,np.minimum(rel,cash),np.nan)


def benchmark(p, start, end):
    """Fixed exact-sample sleeves, cash until first PIT listing; no daily rebalancing.

    All sleeves wait through first decision close, matching strategy earliest fill.
    GEV sleeve is cash before Apr 2 2024, buys first regular-way open thereafter.
    Dividends become unspendable receivables. No terminal liquidation for either side.
    """
    days = np.flatnonzero((p.dates >= start) & (p.dates < end))
    m = len(p.symbols)
    cash = np.full(m, 100000./m)
    q = np.zeros(m)
    receivable = 0.
    path, fills, exposure = [], [], []
    for pos, t in enumerate(days):
        receivable += float(np.dot(q, p.dividends[t]))
        if pos > 0:
            for j in range(m):
                if q[j] == 0 and cash[j] > 0 and np.isfinite(p.open[t,j]) and (p.eligible is None or (p.eligible[days[pos-1],j] and p.eligible[t,j])):
                    px = p.open[t,j]*1.0005
                    q[j] = cash[j]/(px*1.0001)
                    fills.append(dict(date=str(p.dates[t].date()),ticker=p.symbols[j],quantity=float(q[j]),price=float(px),cost=q[j]*(px-p.open[t,j])+q[j]*px*.0001, notional=q[j]*px, action='ENTRY'))
                    cash[j] = 0.
        held = q > 0
        if not np.isfinite(p.close[t,held]).all():
            raise ValueError('Missing benchmark held close')
        marked = float(np.dot(q[held], p.close[t,held]))
        nav = float(cash.sum()+receivable+marked)
        weights = q[held]*p.close[t,held]/nav
        path.append(dict(date=str(p.dates[t].date()),nav=nav,cash=float(cash.sum()),unsettled=receivable,holdings=marked,
                         exposure=marked/nav,positions=int(held.sum()),max_symbol_weight=float(weights.max()) if len(weights) else 0.,
                         concentration_hhi=float(np.sum(weights**2))))
        exposure.append(marked/nav)
    result = metrics([r['nav'] for r in path], fills, exposure, len(days))
    result['max_symbol_weight'] = max(r['max_symbol_weight'] for r in path)
    result['mean_concentration_hhi'] = float(np.mean([r['concentration_hhi'] for r in path]))
    return dict(metrics=result,equity=path,fills=fills,benchmark_symbols=list(p.symbols))


def objective(result, passive):
    m = result['metrics']
    m['primary_benchmark'] = passive.get('benchmark_id','synthetic_equal_weight_fixture')
    m['benchmark_cagr'] = passive['metrics']['cagr']
    m['excess_pp'] = 100*(m['cagr']-m['benchmark_cagr'])
    m['incremental_nav'] = m['final_nav']-passive['metrics']['final_nav']
    m['feasible'] = risk_feasible(m['max_drawdown'])
    m['drawdown_reference'] = .08
    m['risk_limit'] = .02
    m['success'] = bool(m['feasible'] and m['excess_pp'] > 0)
    # Economic objective dominates Calmar and drawdown after hard gate.
    return (m['feasible'], m['excess_pp'] if m['feasible'] else -m['max_drawdown'],
            m['calmar'], -m['max_drawdown'])


def discrimination(p, genes, models, mix, start, end):
    """Post-freeze diagnostic only; these outcomes must never feed selection."""
    result = []
    rows = (p.dates >= start) & (p.dates < end)
    for gene, model in zip(genes, models):
        z, prediction, _ = expected(p, gene, model)
        prediction = np.where(np.isfinite(z),prediction,np.nan)
        selected = np.isfinite(predict(p,gene,model))
        per_horizon = []
        for h,w in zip(mix.sessions,mix.weights):
            relative,_ = labels(p,h,end)
            usable = np.isfinite(prediction) & np.isfinite(relative) & rows[:,None]
            ics = []
            for t in np.flatnonzero(rows):
                mask = usable[t]
                if mask.sum() >= 3 and np.ptp(prediction[t,mask]) > 0 and np.ptp(relative[t,mask]) > 0:
                    # Rank correlation without a scipy dependency.
                    from pandas import Series
                    a=Series(prediction[t,mask]).rank().to_numpy()
                    b=Series(relative[t,mask]).rank().to_numpy()
                    if np.ptp(a)>0 and np.ptp(b)>0:
                        ic=float(np.corrcoef(a,b)[0,1])
                        if np.isfinite(ic):
                            ics.append(ic)
            per_horizon.append(dict(horizon=h,weight=w,evaluated_labels=int(usable.sum()),selected_labels=int((usable & selected).sum()),
                                    mean_selected_net_relative=float(relative[usable & selected].mean()) if (usable & selected).any() else None,
                                    positive_relative_fraction=float((relative[usable]>0).mean()) if usable.any() else None,
                                    mean_rank_ic=float(np.mean(ics)) if ics else None))
        result.append(per_horizon)
    return result
