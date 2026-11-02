"""GA9 isolated snapshot of GA8 execution; see inspection.json."""
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import hashlib
import json
import numpy as np
from .risk import MAX_DRAWDOWN, risk_feasible
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
    sector_cap: float = .30
    niche_bias: tuple = (0., 0., 0.)
    specialist_bias: tuple = ()
    entry_floor: float = -1e30
    size_scale: float = 1.
    score_size: float = 0.
    allow_add: bool = True
    reduce_floor: float = -1e30
    exit_floor: float = -1e30

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
    sectors: tuple = ()
    primary_benchmark: object = None
    eligible: object = None
    screen_score: object = None
    screen_mask: object = None
    synthetic_benchmark_fixture: bool = False


def load_panel(path, end="2027-01-01", sample=None, membership=None, screen_policy=None):
    d = pd.read_parquet(path)
    if sample is not None:
        missing = set(sample)-set(d.ticker)
        if missing:
            raise ValueError(f'Unknown sample symbols: {sorted(missing)}')
        d = d[d.ticker.isin(sample)].copy()
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
    symbols = sorted(sample) if sample is not None else sorted(d.ticker.unique())
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
    from .screening import membership_mask, daily_screen, ScreenPolicy
    eligible = membership_mask(dates, symbols, membership) & c.notna().to_numpy()
    eligible_frame = pd.DataFrame(eligible, index=dates, columns=symbols)
    breadth = (trend.gt(0) & eligible_frame).sum(axis=1) / (trend.notna() & eligible_frame).sum(axis=1).replace(0, np.nan)
    screen_score, screen_mask = daily_screen(tr, c, eligible_frame, screen_policy or ScreenPolicy())
    # Every threshold is fixed a priori; cross-sectional rank uses current close only.
    features = {
        'trend': trend / .05,
        'momentum': m20 / .08,
        'volatility': (.025 - vol) / .015,
        'volume': (v / v.rolling(20, min_periods=20).mean() - 1),
        'recursive': (c / c.ewm(span=20, adjust=False, min_periods=50).mean() - 1) / .04,
        'breadth': pd.DataFrame(np.repeat(((breadth - .5) * 2).values[:, None], len(symbols), axis=1), index=dates, columns=symbols),
        'relative_strength': m60.where(eligible_frame).rank(axis=1, pct=True) * 2 - 1,
    }
    # Closest fixed overlapping prototype; fixed centres avoid full-sample fitting.
    x = np.stack([np.clip((trend / .1).values, -2, 2), np.clip((vol / .02 - 1).values, -2, 2)], axis=-1)
    centres = np.array([[-.7, .2], [.0, -.3], [.7, .2]])
    distance = ((x[:, :, None, :] - centres[None, None, :, :]) ** 2).sum(axis=-1)
    niche = np.argmin(np.nan_to_num(distance, nan=1e9), axis=-1)
    niche[~np.isfinite(x).all(axis=-1)] = -1
    features = {k: f.where(eligible_frame) for k, f in features.items()}
    niche[~eligible] = -1
    audit['membership_basis'] = str(membership) if membership else 'fixed research cohort; historical survivorship unverified'
    return Panel(dates, symbols, o.values, c.values, div.values, r.values,
                 {k: f.values for k, f in features.items()}, niche, breadth.values, eligible=eligible, screen_score=screen_score, screen_mask=screen_mask), audit


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
                feasible=risk_feasible(mdd),
                fills=len(fills), closed_trades=sum(f['action'] in ('EXIT', 'REPLACE') for f in fills),
                exposure=float(np.mean(exposure)), costs=float(sum(f['cost'] for f in fills)),
                turnover=float(sum(f['notional'] for f in fills) / np.mean(nav)), sessions=sessions)


def replay(p, genes, manager, start, end, detail=False, signal=None, edge_mode=False, hold_signal=None, horizon_mix=None, niche_first=False, enforce_drawdown=False, absolute_edges=False):
    """Close t decisions, open t+1 execution, one settled shared account.

    Sale proceeds mature after two sessions (conservative T+2 throughout).
    Stops observed at close; next-open gaps may exceed the -2% trigger.
    """
    if absolute_edges and (not edge_mode or signal is None):
        raise ValueError('Absolute edges require explicit net-return signal and edge mode')
    if signal is None:
        signal = scores(p, genes)
    if hold_signal is None:
        hold_signal = signal
    days = np.flatnonzero((p.dates >= start) & (p.dates < end))
    cash = 100000.
    pending = []
    positions = {}
    orders = []
    fills, path, exposures, events = [], [], [], []
    attribution = np.zeros(len(genes))
    audit = dict(holds=0, abstentions=0, competition=0, correlation_rejections=0,
                 risk_rejections=0, sector_rejections=0, evaluate_minus_one=0, max_identity_error=0., min_cash=cash,
                 max_symbol_weight=0., max_total_risk=0.)
    previous_marks = {}
    peak_nav = cash
    order_date = None
    sectors = p.sectors or ('UNKNOWN',)*len(p.symbols)
    if len(sectors) != len(p.symbols):
        raise ValueError('Sector metadata shape mismatch')
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
                                  quantity=q, price=execution, notional=q * execution, cost=cost, reason=reason,
                                  decision_date=order_date, raw_open=float(px)))
                pos['q'] -= q
                if pos['q'] < 1e-10:
                    del positions[j]
            else:
                if p.eligible is not None and not p.eligible[ti, j]:
                    continue
                marked = sum(x['q'] * p.open[ti, k] for k, x in positions.items())
                nav = cash + sum(x[1] for x in pending) + marked
                existing = positions[j]['q'] * px if j in positions else 0
                # Enforce 10% post-fill cap and reserved settled cash.
                budget = min(target * nav - existing, .099 * nav - existing,
                             cash - manager.reserve * nav,
                             max(0., manager.risk_cap * nav / .02 - marked))
                if edge_mode:
                    sector_value = sum(x['q'] * p.open[ti,k] for k,x in positions.items()
                                       if sectors[k] == sectors[j])
                    sector_budget = max(0., manager.sector_cap*nav-sector_value)
                    if sector_budget < budget:
                        audit['sector_rejections'] += 1
                    budget = min(budget, sector_budget)
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
                    planned = genes[gi].hold_sessions
                    if horizon_mix is not None:
                        horizons, weights = horizon_mix
                        key = f'{date}:{p.symbols[j]}:{json.dumps(asdict(genes[gi]),sort_keys=True)}'
                        draw = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],'big')/2**64
                        k = min(int(np.searchsorted(np.cumsum(weights),draw)),len(horizons)-1)
                        planned = horizons[k]-1  # close decision t+h, next-open exit
                    positions[j] = dict(q=q, entry=execution, peak=execution, born=ti, g=gi,
                                        planned_hold_sessions=planned,added=False,reduced=False)
                fills.append(dict(date=date, ticker=p.symbols[j], gene=gi, action=action,
                                  quantity=q, price=execution, notional=q * execution, cost=cost, reason=reason,
                                  decision_date=order_date, raw_open=float(px)))
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
        peak_nav = max(peak_nav, nav)
        if enforce_drawdown and 1 - nav / peak_nav > MAX_DRAWDOWN:
            raise RuntimeError(f'PORTFOLIO_DRAWDOWN_CEILING_BREACHED {date}: {1-nav/peak_nav:.8f}; next-open execution cannot guarantee a gap-proof ceiling')
        weights = [pos['q'] * p.close[ti, j] / nav for j, pos in positions.items()]
        audit['max_symbol_weight'] = max([audit['max_symbol_weight']] + weights)
        audit['max_total_risk'] = max(audit['max_total_risk'], marked / nav * .02)
        audit['min_cash'] = min(audit['min_cash'], cash)
        sector_weights = {}
        for j,pos in positions.items():
            sector_weights[sectors[j]] = sector_weights.get(sectors[j],0.)+pos['q']*p.close[ti,j]/nav
        path.append(dict(date=date, nav=nav, cash=cash, unsettled=sum(x[1] for x in pending), holdings=marked,
                         exposure=marked/nav, positions=len(positions), max_symbol_weight=max(weights,default=0.),
                         max_sector_weight=max(sector_weights.values(),default=0.),
                         concentration_hhi=sum(w*w for w in weights),
                         holdings_detail=[dict(ticker=p.symbols[j],gene=pos['g'],quantity=pos['q'],
                                               weight=pos['q']*p.close[ti,j]/nav,planned_hold_sessions=pos['planned_hold_sessions']) for j,pos in positions.items()]))
        exposures.append(marked / nav)
        orders = []
        if ti == days[-1]:
            continue  # Mark residual positions; no fictitious close liquidation.
        for j, pos in list(positions.items()):
            g = genes[pos['g']]
            px = p.close[ti, j]
            gain = px / pos['entry'] - 1
            pos['peak'] = max(pos['peak'], px)
            score = hold_signal[pos['g'], ti, j]
            if gain <= -.01:
                audit['evaluate_minus_one'] += 1
            reason = ('membership_exit' if p.eligible is not None and not p.eligible[ti,j] else 'loss_policy' if gain <= -.02 else 'trailing' if px < pos['peak'] * (1-g.trailing)
                      else 'opportunity_cost' if edge_mode and np.isfinite(score) and score <= 0 else 'time' if ti-pos['born'] >= pos['planned_hold_sessions'] else 'native_exit' if p.features[g.exit_family][ti, j] < g.exit_threshold
                      else 'cap' if pos['q'] * px / nav > .10 else '')
            if reason:
                orders.append(('EXIT', j, pos['g'], 0, reason))
            elif score < manager.exit_floor:
                orders.append(('EXIT', j, pos['g'], 0, 'manager_exit'))
            elif (gain <= g.reduce or score < manager.reduce_floor) and not pos['reduced']:
                orders.append(('REDUCE', j, pos['g'], 0, 'evaluate_minus_one'))
                pos['reduced'] = True
            elif (manager.allow_add and gain >= g.add and not pos['added'] and (not edge_mode or signal[pos['g'],ti,j] > 0) and
                  p.features[g.hold_family][ti, j] >= g.hold_threshold):
                orders.append(('ADD', j, pos['g'], min(.099, g.weight * 1.5 * manager.size_scale), 'native_add'))
            else:
                audit['holds'] += 1
        candidates = []
        for gi, g in enumerate(genes):
            for j in np.flatnonzero(np.isfinite(signal[gi, ti]) & (signal[gi, ti] >= g.threshold)):
                if j not in positions and (p.eligible is None or p.eligible[ti,j]) and (not edge_mode or p.screen_mask is None or p.screen_mask[ti,j]):
                    candidates.append((float(signal[gi, ti, j]), int(j), gi))
        # Route each symbol to eligible specialists first. Generalists are fallback
        # only after the identical eligibility, screen and threshold gates above.
        if niche_first:
            routed = []
            for j in sorted({x[1] for x in candidates}):
                pool = [x for x in candidates if x[1] == j]
                specialist = [x for x in pool if genes[x[2]].niche == p.niche[ti,j] and genes[x[2]].niche >= 0]
                routed.extend(specialist or [x for x in pool if genes[x[2]].niche == -1])
            candidates = routed
        candidates = [(value + (0. if absolute_edges else manager.niche_bias[int(p.niche[ti,j])] * (p.niche[ti,j] >= 0)
                       + (manager.specialist_bias[gi] if gi < len(manager.specialist_bias) else 0.)), j, gi)
                      for value,j,gi in candidates]
        candidates = [x for x in candidates if x[0] >= manager.entry_floor]
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
                weak = [(float(np.nan_to_num(hold_signal[pos['g'], ti, k],nan=0.)), k, pos['g']) for k, pos in positions.items()
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
            orders.append(('ENTRY', j, gi, min(.099, genes[gi].weight * manager.size_scale * max(.1, 1 + manager.score_size * value)), 'niche_eligible'))
            selected.append(j)
            seen.add(j)
        order_date = date
        if detail:
            events.append(dict(date=date, screened_candidates=[dict(ticker=p.symbols[j],score=float(p.screen_score[ti,j]))
                               for j in (np.flatnonzero(p.screen_mask[ti]) if p.screen_mask is not None else [])], decision='TRADE' if orders else 'NO_TRADE',
                               ranked_candidates=[dict(ticker=p.symbols[j],gene=gi,expected_net_edge_per_session=value,
                                                       expected_incremental_nav_per_session=value*nav*genes[gi].weight,
                                                       momentum_screen_score=float(p.screen_score[ti,j]) if p.screen_score is not None and np.isfinite(p.screen_score[ti,j]) else None)
                                                  for value,j,gi in candidates[:20]], niche_counts=np.bincount(p.niche[ti][p.niche[ti]>=0], minlength=3).tolist(), eligible=len(candidates), orders=len(orders),
                               order_details=[dict(action=a,ticker=p.symbols[j],gene=g,target=w,reason=r) for a,j,g,w,r in orders]))
    m = metrics([x['nav'] for x in path], fills, exposures, len(days))
    m['attribution'] = attribution.tolist()
    m['open_positions'] = len(positions)
    m['max_symbol_weight'] = max((r['max_symbol_weight'] for r in path),default=0.)
    m['max_sector_weight'] = max((r['max_sector_weight'] for r in path),default=0.)
    m['mean_concentration_hhi'] = float(np.mean([r['concentration_hhi'] for r in path]))
    result = dict(metrics=m, audit=audit)
    if detail:
        peak = 100000.
        for row in path:
            peak = max(peak, row['nav'])
            row['drawdown'] = 1-row['nav']/peak
        result.update(fills=fills, equity=path, events=events)
    return result


def identity(genes, manager):
    return hashlib.sha256(json.dumps([list(map(asdict, genes)), asdict(manager)], sort_keys=True).encode()).hexdigest()[:16]
