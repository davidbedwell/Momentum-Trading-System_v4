"""Independent GA8 causal research engine; no legacy runtime imports."""
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

FAMILIES = ('trend', 'momentum', 'volatility', 'volume', 'recursive', 'breadth', 'relative_strength')

@dataclass(frozen=True)
class Gene:
    family: str
    second: str = 'momentum'
    op: str = 'single'
    threshold: float = 0.25
    niche: int = -1
    exit_threshold: float = -0.3
    hold_sessions: int = 20
    trailing: float = .05
    add: float = .015
    reduce: float = -.01
    weight: float = .06
    hold_family: str = 'momentum'
    exit_family: str = 'trend'
    hold_threshold: float = -.15
    entry_tree: tuple = ()

@dataclass(frozen=True)
class Manager:
    slots: int = 10
    reserve: float = .1
    correlation: float = .8
    risk_cap: float = .02
    replacement: float = .5

@dataclass
class Panel:
    dates: pd.DatetimeIndex
    symbols: list
    open: np.ndarray
    close: np.ndarray
    dividends: np.ndarray
    returns: np.ndarray
    features: dict
    niche: np.ndarray
    breadth: np.ndarray


def load_panel(path, end="2027-01-01"):
    d = pd.read_parquet(path)
    d['date'] = pd.to_datetime(d.date)
    d = d[(d.date >= '2022-01-01') & (d.date < end)].copy()
    from .input_audit import inspect_prices
    audit = inspect_prices(d)
    if not audit['usable']:
        raise ValueError('Invalid required price data')
    # GEV when-issued bars precede regular-way listing on 2024-04-02.
    # Exclude them BEFORE all cross-sectional features, niche assignment and replay.
    d = d[~((d.ticker == 'GEV') & (d.date < pd.Timestamp('2024-04-02')))].copy()
    dates = pd.DatetimeIndex(sorted(d.date.unique()))
    symbols = sorted(d.ticker.unique())
    def wide(col):
        return d.pivot(index='date', columns='ticker', values=col).reindex(index=dates, columns=symbols)
    c, o, v = wide('close'), wide('open'), wide('volume')
    div = wide('dividends').fillna(0)
    # Vendor OHLC is split normalized. Do not multiply holdings a second time.
    splits = wide('stock_splits').fillna(0)
    split_days = splits.gt(0)
    jump = c / c.shift(1)
    if ((jump.lt(.5) | jump.gt(1.8)) & split_days).any().any():
        raise ValueError('Split normalization ambiguous: execution parity blocked')
    r = (c + div) / c.shift(1) - 1
    tr = (1 + r.fillna(0)).cumprod().where(c.notna())
    m20 = tr / tr.shift(20) - 1
    m60 = tr / tr.shift(60) - 1
    vol = r.rolling(20, min_periods=20).std()
    trend = c / c.rolling(50, min_periods=50).mean() - 1
    breadth = (trend.gt(0) & trend.notna()).sum(axis=1) / trend.notna().sum(axis=1).replace(0, np.nan)
    # Every threshold is fixed a priori; cross-sectional rank uses current close only.
    features = {
        'trend': trend / .05,
        'momentum': m20 / .08,
        'volatility': (.025 - vol) / .015,
        'volume': (v / v.rolling(20, min_periods=20).mean() - 1),
        'recursive': (c / c.ewm(span=20, adjust=False, min_periods=50).mean() - 1) / .04,
        'breadth': pd.DataFrame(np.repeat(((breadth - .5) * 2).values[:, None], len(symbols), axis=1), index=dates, columns=symbols),
        'relative_strength': m60.rank(axis=1, pct=True) * 2 - 1,
    }
    # Closest fixed overlapping prototype; fixed centres avoid full-sample fitting.
    x = np.stack([np.clip((trend / .1).values, -2, 2), np.clip((vol / .02 - 1).values, -2, 2)], axis=-1)
    centres = np.array([[-.7, .2], [.0, -.3], [.7, .2]])
    distance = ((x[:, :, None, :] - centres[None, None, :, :]) ** 2).sum(axis=-1)
    niche = np.argmin(np.nan_to_num(distance, nan=1e9), axis=-1)
    niche[~np.isfinite(x).all(axis=-1)] = -1
    return Panel(dates, symbols, o.values, c.values, div.values, r.values,
                 {k: f.values for k, f in features.items()}, niche, breadth.values), audit


def evaluate_tree(features, tree):
    if isinstance(tree, str):
        return features[tree]
    op, left, right = tree
    a, b = evaluate_tree(features, left), evaluate_tree(features, right)
    if op not in ('and', 'or'):
        raise ValueError('Unknown entry operator')
    return np.minimum(a, b) if op == 'and' else np.maximum(a, b)


def scores(panel, genes):
    result = []
    for g in genes:
        a, b = panel.features[g.family], panel.features[g.second]
        z = np.minimum(a, b) if g.op == 'and' else np.maximum(a, b) if g.op == 'or' else a
        if g.entry_tree:
            z = evaluate_tree(panel.features, g.entry_tree)
        result.append(np.where((panel.niche == g.niche) | (g.niche == -1), z, -np.inf))
    return np.array(result)


def metrics(equity, fills, exposure, sessions):
    nav = np.array(equity, dtype=float)
    if len(nav) == 0:
        raise ValueError('Empty replay')
    nav = np.r_[100000., nav]
    dd = 1 - nav / np.maximum.accumulate(nav)
    mdd = float(dd.max())
    cagr = float((nav[-1] / nav[0]) ** (252 / sessions) - 1) if nav[-1] > 0 else -1.
    calmar = cagr / mdd if mdd > 1e-12 else 0.
    return dict(cagr=cagr, max_drawdown=mdd, calmar=calmar, final_nav=float(nav[-1]),
                feasible=bool(mdd < .2 and calmar > 1.5 and cagr > 0),
                fills=len(fills), closed_trades=sum(f['action'] in ('EXIT', 'REPLACE') for f in fills),
                exposure=float(np.mean(exposure)), costs=float(sum(f['cost'] for f in fills)),
                turnover=float(sum(f['notional'] for f in fills) / np.mean(nav)), sessions=sessions)


def replay(p, genes, manager, start, end, detail=False, signal=None):
    """Close t decisions, open t+1 execution, one settled shared account.

    Sale proceeds mature after two sessions (conservative T+2 throughout).
    Stops observed at close; next-open gaps may exceed the -2% trigger.
    """
    if signal is None:
        signal = scores(p, genes)
    days = np.flatnonzero((p.dates >= start) & (p.dates < end))
    cash = 100000.
    pending = []
    positions = {}
    orders = []
    fills, path, exposures, events = [], [], [], []
    attribution = np.zeros(len(genes))
    audit = dict(holds=0, abstentions=0, competition=0, correlation_rejections=0,
                 risk_rejections=0, evaluate_minus_one=0, max_identity_error=0., min_cash=cash,
                 max_symbol_weight=0., max_total_risk=0.)
    previous_marks = {}
    for ti in days:
        date = str(p.dates[ti].date())
        ready = sum(x[1] for x in pending if x[0] <= ti)
        cash += ready
        pending = [x for x in pending if x[0] > ti]
        # Dividend entitlement belongs to overnight holdings, including open exits.
        for j, pos in positions.items():
            amount = pos['q'] * p.dividends[ti, j]
            # Payment dates unavailable: carry a nonspendable receivable.
            # It stays in NAV but cannot fund orders anywhere in this replay.
            if amount:
                pending.append((len(p.dates) + 1, amount))
            attribution[pos['g']] += amount
        # Mark overnight move before trading, using raw split-normalized shares.
        for j, pos in positions.items():
            if np.isfinite(p.open[ti, j]):
                attribution[pos['g']] += pos['q'] * (p.open[ti, j] - previous_marks[j])
        # Reductions/exits execute first; proceeds remain unsettled.
        for action, j, gi, target, reason in orders:
            px = p.open[ti, j]
            if not np.isfinite(px) or px <= 0:
                continue
            if action in ('EXIT', 'REDUCE', 'REPLACE'):
                if j not in positions:
                    continue
                pos = positions[j]
                q = pos['q'] if action != 'REDUCE' else pos['q'] / 2
                execution = px * (1 - .0005)
                fee = q * execution * .0001
                proceeds = q * execution - fee
                pending.append((ti + 2, proceeds))
                cost = q * (px - execution) + fee
                attribution[pos['g']] -= cost
                fills.append(dict(date=date, ticker=p.symbols[j], gene=pos['g'], action=action,
                                  quantity=q, price=execution, notional=q * execution, cost=cost, reason=reason))
                pos['q'] -= q
                if pos['q'] < 1e-10:
                    del positions[j]
            else:
                marked = sum(x['q'] * p.open[ti, k] for k, x in positions.items())
                nav = cash + sum(x[1] for x in pending) + marked
                existing = positions[j]['q'] * px if j in positions else 0
                # Enforce 10% post-fill cap and reserved settled cash.
                budget = min(target * nav - existing, .099 * nav - existing,
                             cash - manager.reserve * nav,
                             max(0., manager.risk_cap * nav / .02 - marked))
                if budget <= 1 or (j not in positions and len(positions) >= manager.slots):
                    audit['competition'] += 1
                    if manager.risk_cap * nav / .02 <= marked:
                        audit['risk_rejections'] += 1
                    continue
                execution = px * 1.0005
                q = budget / (execution * 1.0001)
                fee = q * execution * .0001
                cash -= q * execution + fee
                cost = q * (execution - px) + fee
                attribution[gi] -= cost
                if j in positions:
                    pos = positions[j]
                    pos['entry'] = (pos['entry'] * pos['q'] + execution * q) / (pos['q'] + q)
                    pos['q'] += q
                    pos['added'] = True
                else:
                    positions[j] = dict(q=q, entry=execution, peak=execution, born=ti, g=gi, added=False, reduced=False)
                fills.append(dict(date=date, ticker=p.symbols[j], gene=gi, action=action,
                                  quantity=q, price=execution, notional=q * execution, cost=cost, reason=reason))
        marked = 0.
        for j, pos in positions.items():
            px = p.close[ti, j]
            if not np.isfinite(px):
                raise ValueError('Missing held close; no silent forward fill')
            marked += pos['q'] * px
            attribution[pos['g']] += pos['q'] * (px - p.open[ti, j])
            previous_marks[j] = px
        nav = cash + sum(x[1] for x in pending) + marked
        if cash < -1e-6 or nav <= 0:
            raise AssertionError('Invalid funded account')
        error = abs(nav - (100000 + attribution.sum()))
        audit['max_identity_error'] = max(audit['max_identity_error'], error)
        if error > 1e-5:
            raise AssertionError(f'P&L reconciliation failed {error}')
        weights = [pos['q'] * p.close[ti, j] / nav for j, pos in positions.items()]
        audit['max_symbol_weight'] = max([audit['max_symbol_weight']] + weights)
        audit['max_total_risk'] = max(audit['max_total_risk'], marked / nav * .02)
        audit['min_cash'] = min(audit['min_cash'], cash)
        path.append(dict(date=date, nav=nav, cash=cash, unsettled=sum(x[1] for x in pending), holdings=marked))
        exposures.append(marked / nav)
        orders = []
        if ti == days[-1]:
            continue  # Mark residual positions; no fictitious close liquidation.
        for j, pos in list(positions.items()):
            g = genes[pos['g']]
            px = p.close[ti, j]
            gain = px / pos['entry'] - 1
            pos['peak'] = max(pos['peak'], px)
            score = signal[pos['g'], ti, j]
            if gain <= -.01:
                audit['evaluate_minus_one'] += 1
            reason = ('loss_policy' if gain <= -.02 else 'trailing' if px < pos['peak'] * (1-g.trailing)
                      else 'time' if ti-pos['born'] >= g.hold_sessions else 'native_exit' if p.features[g.exit_family][ti, j] < g.exit_threshold
                      else 'cap' if pos['q'] * px / nav > .10 else '')
            if reason:
                orders.append(('EXIT', j, pos['g'], 0, reason))
            elif gain <= g.reduce and not pos['reduced']:
                orders.append(('REDUCE', j, pos['g'], 0, 'evaluate_minus_one'))
                pos['reduced'] = True
            elif (gain >= g.add and not pos['added'] and
                  p.features[g.hold_family][ti, j] >= g.hold_threshold):
                orders.append(('ADD', j, pos['g'], min(.099, g.weight * 1.5), 'native_add'))
            else:
                audit['holds'] += 1
        candidates = []
        for gi, g in enumerate(genes):
            for j in np.flatnonzero(np.isfinite(signal[gi, ti]) & (signal[gi, ti] >= g.threshold)):
                if j not in positions:
                    candidates.append((float(signal[gi, ti, j]), int(j), gi))
        candidates.sort(reverse=True)
        if not candidates:
            audit['abstentions'] += 1
        selected = list(positions)
        seen = set(selected)
        for value, j, gi in candidates:
            if j in seen:
                continue
            if len(selected) >= manager.slots:
                audit['competition'] += 1
                # Challenger may replace weak incumbent; cannot spend sale proceeds today.
                weak = [(signal[pos['g'], ti, k], k, pos['g']) for k, pos in positions.items()
                        if not any(o[1] == k for o in orders)]
                if weak:
                    s, k, oldg = min(weak)
                    if value > s + manager.replacement:
                        orders.append(('REPLACE', k, oldg, 0, 'stronger_challenger'))
                break
            reject = False
            for k in selected:
                a, b = p.returns[max(0, ti-59):ti+1, j], p.returns[max(0, ti-59):ti+1, k]
                mask = np.isfinite(a) & np.isfinite(b)
                if mask.sum() >= 20 and np.std(a[mask]) > 0 and np.std(b[mask]) > 0:
                    if np.corrcoef(a[mask], b[mask])[0, 1] > manager.correlation:
                        reject = True
                        break
            if reject:
                audit['correlation_rejections'] += 1
                continue
            orders.append(('ENTRY', j, gi, genes[gi].weight, 'niche_eligible'))
            selected.append(j)
            seen.add(j)
        if detail:
            events.append(dict(date=date, niche_counts=np.bincount(p.niche[ti][p.niche[ti]>=0], minlength=3).tolist(), eligible=len(candidates), orders=len(orders)))
    m = metrics([x['nav'] for x in path], fills, exposures, len(days))
    m['attribution'] = attribution.tolist()
    m['open_positions'] = len(positions)
    result = dict(metrics=m, audit=audit)
    if detail:
        peak = 100000.
        for row in path:
            peak = max(peak, row['nav'])
            row['drawdown'] = 1-row['nav']/peak
        result.update(fills=fills, equity=path, events=events)
    return result


def rank(result):
    m = result['metrics']
    # Feasible first, then funded CAGR. Infeasible frontier uses explicit distance.
    violation = max(0., m['max_drawdown']-.199999) + max(0., 1.500001-m['calmar']) / 10
    return (m['feasible'], m['cagr'] if m['feasible'] else -violation, m['cagr'])


def identity(genes, manager):
    return hashlib.sha256(json.dumps([list(map(asdict, genes)), asdict(manager)], sort_keys=True).encode()).hexdigest()[:16]
