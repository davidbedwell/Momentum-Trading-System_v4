Independently critique GA9 as a trading systems architect. Ignore formal certification. Diagnose why 16.06% CAGR, 20.01% MDD, Calmar 0.80, QQQ-relative -22.55pp despite momentum ranking. Recommend improved engineering, alternative trading strategies and at least three architectures: improved GA9, different evolutionary architecture, hybrid/non-GA. Challenge chromosome grammar, fitness, selection, entry/exit, trailing stops, turnover, allocation, cash/SGOV, risk accounting. Objectives: maximize CAGR, MDD <=20%, Calmar >=2, beat QQQ, 2% planned portfolio stop-risk. Rank concrete changes by benefit, effort, and compute. Distinguish defects from hypotheses. Give small rapid proof-of-function experiments and stop criteria. No certification work or lengthy validation. Keep economic realism and causality.

FILE REPORT.md
# GA9 bounded engineering session — 2026-10-30

Stopped after three repair cycles: no valid end-to-end economic proof. NO_TRADE; no GA, forward selection, promotion, or GA8 process intervention.

## Changes and hypotheses

1. Replace capital-times-constant risk proxy with sum(value * max(0,1-stop/mark)); admission uses remaining 2% NAV risk budget divided by actual candidate stop distance plus entry costs. Separate position cap, capital exposure, cash reserve, stop risk and realized drawdown. Remove 8% research rejection; retain reference. Remove first-16 and full-period-completeness universe filters; reuse causal multi-horizon daily screen.
2. Build frozen top-ten momentum diagnostic over all 125 non-quarantined archive symbols, using only 2022-2024 exposed development data; QQQ fixed before replay. Resolve isolated-copy partition dependency by read-only Research symlink. Initial baseline: CAGR 8.80%, MDD 14.75%, Calmar .597, excess CAGR -29.80 percentage points, mean exposure 50.65%. Audit discovered fixed-entry stop risk grew to 8.07% as unrealized profits accumulated. This result fails the planned-risk requirement.
3. Ratchet protective stop daily to at least close*(1-gene.stop_distance), execute breached stops next open. Add regression for gains not inflating planned loss-at-risk and replace obsolete hard-8% tests. Same baseline rerun: CAGR 16.06%, MDD 20.01%, Calmar .802, excess CAGR -22.55 percentage points, exposure 60.72%, maximum close planned risk 1.6124%. CAGR improved but drawdown worsened; neither result dominates on both objectives. No policy was selected for forward deployment.

## Verification

27 tests passed: ga9.test_engineering, ga9.test_execution, ga9.test_screening, ga9.test_objective. This includes future-prefix invariance, late listing eligibility, 40% capital at 5% stop = 2% planned risk, risk cap rejection above 2%, explicit gap fill, realistic deployment, dividends/settlement, abstention, objective, and accounting. Final max reconciliation error 7.28e-11, minimum settled cash $9,232.46. No full repository suite run.

Reproduce from this directory using /opt/mts/.venv/bin/python -m unittest ga9.test_engineering ga9.test_execution ga9.test_screening ga9.test_objective -q and /opt/mts/.venv/bin/python -m ga9.engineering_baseline NEW_OUTPUT.

Ranking diagnostic: average top-five versus bottom-five net 20-session returns among positive-momentum eligible names: 2022 +1.882% versus -1.794%; 2023-24 +2.938% versus +1.591%, spread +1.347pp. Overlapping labels are not independent; these are exposed development diagnostics, not forward evidence or a fitted net-edge forecast. Absolute positive return does not establish QQQ-relative edge.

## Limits and remaining work

Archive membership is not verified PIT membership. Daily eligibility uses currently observed valid bars and trailing history, never future completeness. Full historical eligible universe, delisting outcomes, dividend/adjustment parity, and full-universe equal-weight secondary benchmark remain unproven/unimplemented in this runner. No sealed 2025/2026 outcomes used for selection. Replay missing held marks raises an error instead of silently filling. Sector metadata unknown; sector constraints disabled for the diagnostic, all stocks appear UNKNOWN. Individual weights can drift above entry cap before next-open exits.

2% is planned stop loss-at-risk, not guaranteed realized loss or maximum drawdown. Daily ratcheting stops and admission sizing enforce the model's defined risk; execution gaps/slippage and intra-session moves can exceed it. Realized 20.01% MDD is allowed in research and is not confused with the 2% planned risk constraint. Costs are fixed 5bp slippage +1bp fee each side, conservative T+2. QQQ NAV includes entry cost but the generic benchmark metrics report zero fills/costs; do not interpret those metadata as a free fill. Both paths mark residual holdings without terminal liquidation. Distributions and corporate actions are unverified price-return assumptions.

GA defaults/mutation search and old supervisor entrypoints are not approved by this repair: some retain legacy benchmark policies and manager weights. Only engineering_baseline is the bounded reviewed entrypoint; no long GA until those paths are migrated and net-edge proof exists.

Next scoped session: isolate ranking, turnover and stop-exit drag versus QQQ on development data; add total-return benchmark parity and secondary full-universe benchmark; migrate remaining GA configuration only after baseline proof. Estimated 1-2 hours engineering plus data availability, not a success ETA. Stop here per no-proof/three-cycle limit.

FILE ga9/evolution.py
"""Small, serial GA with an internal chronological validation objective."""
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import random
import time
import numpy as np
from .execution import FAMILIES, Gene, Manager, replay
from .objective import HorizonMix, fit, predict, holding_predict, objective
from .benchmarks import selection_benchmark, primary_name


@dataclass(frozen=True)
class Candidate:
    genes: tuple
    manager: Manager
    mix: HorizonMix

    def record(self):
        return asdict(self)

    @property
    def id(self):
        return hashlib.sha256(json.dumps(self.record(),sort_keys=True).encode()).hexdigest()[:16]


def signals(p, candidate, models):
    if not candidate.genes:
        return np.empty((0,*p.close.shape))
    return np.stack([predict(p,g,m) for g,m in zip(candidate.genes,models)])


def funded(p, candidate, models, start, end, detail=True, omit=None):
    keep = [k for k in range(len(candidate.genes)) if k != omit]
    active = replace(candidate,genes=tuple(candidate.genes[k] for k in keep))
    models = [models[k] for k in keep]
    # The raw entry threshold belongs to predict; native engine sees net edge >0.
    genes = [replace(g,threshold=0.) for g in active.genes]
    hold = np.stack([holding_predict(p,g,m) for g,m in zip(active.genes,models)]) if active.genes else np.empty((0,*p.close.shape))
    return replay(p,genes,active.manager,start,end,detail,
                  signals(p,active,models),edge_mode=True,hold_signal=hold,horizon_mix=(active.mix.sessions,active.mix.weights))


def train_models(p, candidate, cutoff, cache):
    return [fit(p,g,candidate.mix,cutoff,label_cache=cache) for g in candidate.genes]


def seeds(horizons):
    mix = HorizonMix(tuple(horizons),tuple([1/len(horizons)]*len(horizons)))
    hold = round(sum(h*w for h,w in zip(mix.sessions,mix.weights)))
    manager = Manager(replacement=.0001)
    return [Candidate((),manager,mix),
            Candidate((Gene('trend',hold_sessions=hold),),manager,mix),
            Candidate((Gene('relative_strength','momentum','and',.2,hold_sessions=hold),),manager,mix),
            Candidate((Gene('volatility','recursive','and',.1,hold_sessions=hold),
                       Gene('momentum',hold_sessions=hold)),manager,mix)]


def mutate(parent, rng):
    w=np.array([rng.random()+.05 for _ in parent.mix.sessions]);w/=w.sum()
    mix=HorizonMix(parent.mix.sessions,tuple(w.tolist()))
    hold=round(sum(h*x for h,x in zip(mix.sessions,mix.weights)))
    genes=list(parent.genes) or [Gene(rng.choice(FAMILIES))]
    k=rng.randrange(len(genes));g=genes[k]
    genes[k]=replace(g,family=rng.choice(FAMILIES),second=rng.choice(FAMILIES),
                     op=rng.choice(['single','and','or']),threshold=rng.choice([-.2,.1,.3,.5]),
                     niche=rng.choice([-1,-1,0,1,2]),hold_sessions=hold,
                     hold_family=rng.choice(FAMILIES),exit_family=rng.choice(FAMILIES),
                     trailing=rng.choice([.03,.05,.08]),weight=rng.choice([.04,.06,.09]))
    if len(genes)<3 and rng.random()<.3:
        genes.append(Gene(rng.choice(FAMILIES),hold_sessions=hold))
    genes=[replace(g,hold_sessions=hold) for g in genes]
    manager=replace(parent.manager,slots=rng.choice([3,6,10]),reserve=rng.choice([.1,.3,.5]),
                    correlation=rng.choice([.6,.8,.95]),risk_cap=rng.choice([.004,.008,.012]),
                    replacement=rng.choice([.00005,.0001,.0003]),sector_cap=rng.choice([.20,.25,.30]))
    return Candidate(tuple(genes),manager,mix)


def search(p, year, generations=2, population=4, budget=30, seed=90079,
           horizons=(5,20,60,120), stop=lambda: False, progress=lambda row: None):
    """Select using internal forward half-year; external forward never enters here."""
    begin=time.monotonic()
    rng=random.Random(seed+year)
    calibration_end=f'{year-1}-07-01'
    train_end=f'{year}-01-01'
    passive=selection_benchmark(p,calibration_end,train_end)
    initial=seeds(horizons)
    population_rows=initial[:population]
    while len(population_rows)<population:
        population_rows.append(mutate(rng.choice(initial[1:]),rng))
    label_cache={}; evaluation_cache={}; journal=[]; rejected=[]
    best=None
    for generation in range(generations):
        ranked=[]
        for candidate in population_rows:
            if (stop() or time.monotonic()-begin>=budget) and best is not None:
                break
            if candidate.id not in evaluation_cache:
                models=train_models(p,candidate,calibration_end,label_cache)
                result=funded(p,candidate,models,calibration_end,train_end,detail=False)
                key=objective(result,passive)
                evaluation_cache[candidate.id]=(key,result,models)
            key,result,models=evaluation_cache[candidate.id]
            row=dict(generation=generation,id=candidate.id,candidate=candidate.record(),
                     label_cutoff=calibration_end,selection_start=calibration_end,selection_end=train_end,
                     phase='internal_validation_used_for_selection',benchmark=primary_name(p),metrics=result['metrics'],
                     elapsed_seconds=time.monotonic()-begin)
            journal.append(row)
            if not result['metrics']['feasible']:
                rejected.append(row)
            else:
                ranked.append((key,candidate))
                if best is None or key>best[0]:
                    best=(key,candidate)
            progress(row)
        if not ranked or stop() or time.monotonic()-begin>=budget:
            break
        ranked.sort(key=lambda x:x[0],reverse=True)
        elites=[c for _,c in ranked[:2]]
        population_rows=[initial[0],best[1]]
        while len(population_rows)<population:
            population_rows.append(mutate(rng.choice(elites),rng))
    if best is None:
        raise RuntimeError('No feasible candidate evaluated (cash control should be feasible)')
    selected=best[1]
    # Refit ONLY the selected genome after selection; no tuning on external forward.
    frozen_models=train_models(p,selected,train_end,label_cache)
    return selected,frozen_models,dict(journal=journal,rejected_risk=rejected,
               calibration_end=calibration_end,selection_start=calibration_end,selection_end=train_end,
               selected_id=selected.id,elapsed_seconds=time.monotonic()-begin,
               selection_metrics=evaluation_cache[selected.id][1]['metrics'],
               stop_reason='STOP' if stop() else 'budget' if time.monotonic()-begin>=budget else 'generation_cap')

FILE ga9/engineering_baseline.py
"""Frozen development diagnostic, no GA, no sealed forward data."""
import json
from pathlib import Path
from dataclasses import replace
import numpy as np
import pandas as pd
from .exploratory import inputs
from .execution import Gene,Manager,replay,metrics

def ranking(p,a,b,h=20):
    top=[];bottom=[]
    for t in range(a,b-h-1):
        valid=p.eligible[t]&np.isfinite(p.screen_score[t])&np.isfinite(p.open[t+1])&np.isfinite(p.open[t+h+1])
        js=np.flatnonzero(valid)
        if len(js)<10: continue
        js=js[np.argsort(p.screen_score[t,js],kind='stable')]
        y=p.open[t+h+1,js]*.99940005/(p.open[t+1,js]*1.00060005)-1
        bottom.append(float(np.mean(y[:5])));top.append(float(np.mean(y[-5:])))
    return dict(sessions=len(top),top_net_20d=float(np.mean(top)) if top else None,bottom_net_20d=float(np.mean(bottom)) if bottom else None,spread=float(np.mean(np.array(top)-bottom)) if top else None)

def run(out):
    out=Path(out);out.mkdir(exist_ok=True)
    p,prov,refs=inputs('real')
    # Freeze Nasdaq QQQ, top ten, 20/60/120 ranks, 2% price stop, 9% weights BEFORE outcomes.
    policy=dict(primary_benchmark='QQQ',top_n=10,weight=.09,stop_distance=.02,stop_policy='daily close ratchet, next-open execution',risk_cap=.02,reserve=.1,cost_bps_per_side=6,train='2022',development_test='2023-2024 previously exposed',sealed_data_access=False)
    (out/'policy.json').write_text(json.dumps(policy,indent=2))
    train=np.flatnonzero(p.dates<'2023');test=np.flatnonzero(p.dates>='2023')
    rank_train=ranking(p,int(train[0]),int(train[-1])+1)
    # Simple mechanical benchmark has no learned expected edge: explicitly diagnostic.
    mask=np.zeros_like(p.screen_mask)
    for t in range(len(p.dates)):
        js=np.flatnonzero(p.screen_mask[t]);js=js[np.argsort(-p.screen_score[t,js],kind='stable')[:10]];mask[t,js]=True
    p=replace(p,screen_mask=mask)
    signal=np.where(mask,p.screen_score,-np.inf)[None]
    g=Gene('momentum',threshold=0,weight=.09,stop_distance=.02,hold_sessions=20,add=100,reduce=-100,exit_threshold=-100,trailing=1)
    m=Manager(slots=10,reserve=.1,risk_cap=.02,position_cap=.10,correlation=1.1,sector_cap=1,allow_add=False,replacement=2)
    result=replay(p,[g],m,'2023','2025',True,signal,True,hold_signal=np.ones_like(signal))
    (out/'daily.json').write_text(json.dumps(result,allow_nan=False))
    ref=refs.get('QQQ');bench=None
    if ref is not None:
        d=ref.loc[p.dates[test]]
        if np.isfinite(d[['open','close']]).all().all():
            nav=np.r_[100000,100000*d.close.to_numpy()[1:]/(d.open.iloc[1]*1.00060005)]
            bench=metrics(nav.tolist(),[],[1]*len(nav),len(nav))
    metric=result['metrics'];excess=metric['cagr']-bench['cagr'] if bench else None
    report=dict(policy=policy,provenance=prov,symbol_count=len(p.symbols),train_ranking=rank_train,development_ranking=ranking(p,int(test[0]),int(test[-1])+1),momentum_diagnostic=metric,risk_audit=result['audit'],QQQ=bench,excess_cagr=excess,pareto=[dict(cagr=metric['cagr'],mdd=metric['max_drawdown'],calmar=metric['calmar'],excess_cagr=excess)],status='NO_VALID_PROOF_NO_TRADE',long_ga_started=False,limitations=['observed-bar eligibility is not verified historical membership','survivorship bias and missing delisting outcomes','archive distributions and split normalization unverified','QQQ completeness required for economic proof','fixed development diagnostic is not a positive expected net-edge model','close-observed stops execute next open; gaps can exceed 2% planned risk','close marked risk can drift above cap; admission constraint is not a guarantee'])
    (out/'baseline_report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps({k:v for k,v in report.items() if k!='provenance'},indent=2))
if __name__=='__main__':
    import sys
    run(sys.argv[1])

FILE ga9/execution.py
"""GA9 isolated snapshot of GA8 execution; see inspection.json."""
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import hashlib
import json
import numpy as np
from .risk import MAX_DRAWDOWN, risk_feasible, stop_risk, risk_budget, DRAWDOWN_REFERENCE
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
    stop_distance: float = .02
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
    position_cap: float = .20
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
                feasible=risk_feasible(mdd), above_drawdown_reference=mdd>DRAWDOWN_REFERENCE,
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
                existing_risk = sum(stop_risk(x['q']*p.open[ti,k], p.open[ti,k], x['stop']) for k,x in positions.items())
                # Include entry slippage and fee in the planned loss budget.
                distance = genes[gi].stop_distance + .00060005
                budget = min(target * nav - existing, manager.position_cap * nav - existing,
                             cash - manager.reserve * nav,
                             risk_budget(nav, manager.risk_cap, existing_risk, distance))
                if edge_mode:
                    sector_value = sum(x['q'] * p.open[ti,k] for k,x in positions.items()
                                       if sectors[k] == sectors[j])
                    sector_budget = max(0., manager.sector_cap*nav-sector_value)
                    if sector_budget < budget:
                        audit['sector_rejections'] += 1
                    budget = min(budget, sector_budget)
                if budget <= 1 or (j not in positions and len(positions) >= manager.slots):
                    audit['competition'] += 1
                    if existing_risk >= manager.risk_cap * nav:
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
                    pos['stop'] = max(pos['stop'], execution*(1-genes[gi].stop_distance))
                    pos['added'] = True
                else:
                    planned = genes[gi].hold_sessions
                    if horizon_mix is not None:
                        ho
FILE ga9/risk.py
"""Defined stop loss-at-risk; gaps can exceed this planned loss."""
import math
MAX_DRAWDOWN = 1.0  # research validity boundary, not a discovery drawdown gate
DRAWDOWN_REFERENCE = .08
PORTFOLIO_RISK_CAP = .02

def risk_feasible(max_drawdown):
    return bool(math.isfinite(max_drawdown) and 0 <= max_drawdown <= MAX_DRAWDOWN)

def stop_risk(value, price, stop):
    if not all(math.isfinite(x) for x in (value, price, stop)) or value < 0 or price <= 0 or stop < 0:
        raise ValueError('Invalid risk mark')
    return value * max(0., 1-stop/price)

def risk_budget(nav, cap, existing_risk, stop_distance):
    if not 0 <= cap <= PORTFOLIO_RISK_CAP or not 0 < stop_distance <= 1:
        raise ValueError('Risk cap must remain within 2%; positive stop distance required')
    return max(0., cap*nav-existing_risk)/stop_distance

FILE ga9/objective.py
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

FILE ga9/opportunity.py
"""GA9-A: causal stock opportunity distributions and a GA9-B adapter.

All return fields are fractions, net of 5bp slippage + 1bp fees per side.
Forecast labels use next-open entry and next-open exit after the horizon.
"""
from dataclasses import asdict, dataclass, replace
import numpy as np
import pandas as pd
from .execution import Panel, Gene, Manager, replay, scores

ENTRY = 1.0005 * 1.0001
EXIT = .9995 * .9999
BOUNDARIES = [-1., 0., .5, 1., 2.]


def discovery(close, eligible, top_k=150):
    """Refresh rolling discovery daily; rank is a discovery filter only."""
    c = pd.DataFrame(close)
    parts = [c/c.shift(h)-1 for h in (20, 60, 120)]
    score = sum(x.where(eligible).rank(axis=1, pct=True) for x in parts)/3
    valid = eligible & np.isfinite(score.to_numpy())
    rank = score.where(valid).rank(axis=1, ascending=False, method='first')
    return score.to_numpy(), rank.le(top_k).to_numpy()


def load_synthetic(prices, membership):
    """Read the existing synthetic scenario; rebuild features from raw prices."""
    d = pd.read_parquet(prices)
    m = pd.read_parquet(membership, columns=['date','ticker','eligible','sector_id'])
    d = d.merge(m, on=['date','ticker'], validate='one_to_one')
    dates = pd.DatetimeIndex(sorted(pd.to_datetime(d.date).unique()))
    symbols = sorted(d.ticker.unique())
    def wide(key):
        return d.pivot(index='date',columns='ticker',values=key).reindex(index=dates,columns=symbols)
    c, o, v = wide('close'), wide('open'), wide('volume')
    if not np.isfinite(c).all().all() or not np.isfinite(o).all().all() or (c<=0).any().any() or (o<=0).any().any():
        raise ValueError('Complete positive synthetic execution marks required')
    eligible = wide('eligible').eq(True).to_numpy()
    r = c.pct_change(); trend=c/c.rolling(50).mean()-1; mom=c/c.shift(20)-1
    vol=r.rolling(20).std(); breadth=(trend.gt(0)&eligible).sum(axis=1)/pd.DataFrame(eligible,index=c.index).sum(axis=1).replace(0,np.nan)
    f=dict(trend=trend/.05,momentum=mom/.08,volatility=(.025-vol)/.015,
           volume=v/v.rolling(20).mean()-1,recursive=(c/c.ewm(span=20,min_periods=50).mean()-1)/.04,
           relative_strength=(c/c.shift(60)-1).where(eligible).rank(axis=1,pct=True)*2-1,
           breadth=pd.DataFrame(np.repeat(((breadth-.5)*2).to_numpy()[:,None],len(symbols),axis=1),index=c.index,columns=c.columns))
    score,pool=discovery(c.to_numpy(),eligible)
    sectors=tuple(str(d[d.ticker==s].sector_id.iloc[0]) for s in symbols)
    return Panel(dates,symbols,o.to_numpy(),c.to_numpy(),np.zeros(c.shape),r.to_numpy(),
                 {k:x.to_numpy() for k,x in f.items()},np.zeros(c.shape,dtype=int),breadth.to_numpy(),
                 sectors=sectors,eligible=eligible,screen_score=score,screen_mask=pool,synthetic_benchmark_fixture=True)


@dataclass(frozen=True)
class Strategy:
    family: str = 'momentum'
    horizon: int = 20
    threshold: float = 0.
    add: float = .008
    reduce: float = -.008
    trailing: float = .05
    def gene(self):
        return Gene(self.family,threshold=0.,hold_sessions=self.horizon-1,add=self.add,reduce=self.reduce,
                    trailing=self.trailing,exit_threshold=-1e30,hold_threshold=-1e30,weight=.06)


def outcomes(p, h, cutoff):
    """Only fully matured labels; path downside includes every intervening close."""
    n,k=p.close.shape
    y=np.full((n,k),np.nan); down=y.copy()
    for t in range(min(n-h-1,cutoff-h-1)):
        entry=p.open[t+1]*ENTRY
        y[t]=p.open[t+h+1]*EXIT/entry-1
        down[t]=np.minimum(0,np.minimum(p.close[t+1:t+h+1].min(axis=0),p.open[t+h+1])*EXIT/entry-1)
    return y,down



def strategy_outcomes(p, strategy, cutoff):
    """Isolated committed-capital sleeves executing the stock action rules.

    Two thirds enters next open; one third is reserved for one add. Reductions
    and exits execute after the triggering close. Portfolio funding is B's job.
    """
    n,k=p.close.shape; h=strategy.horizon
    y=np.full((n,k),np.nan); downside=y.copy()
    for t in range(min(n-h-1,cutoff-h-1)):
        base=p.open[t+1]; q=(2/3)/(base*ENTRY); cash=np.full(k,1/3.)
        peak=base*1.0005; entry=base*1.0005
        added=np.zeros(k,bool); reduced=added.copy(); worst=np.ones(k)
        for step in range(1,h+1):
            day=t+step; px=p.close[day]; peak=np.maximum(peak,px)
            worst=np.minimum(worst,cash+q*px)
            gain=px/entry-1; active=q>0
            exit_now=active & ((gain<=-.02)|(px<peak*(1-strategy.trailing))|~p.eligible[day]|(step==h))
            reduce=active & ~exit_now & ~reduced & (gain<=strategy.reduce)
            add=active & ~exit_now & ~reduce & ~added & (gain>=strategy.add)
            execution=p.open[day+1]
            sold=np.where(exit_now,q,np.where(reduce,q/2,0.))
            cash+=sold*execution*EXIT; q-=sold; reduced|=reduce
            z=p.features[strategy.family][day]
            add &= np.isfinite(z)&(z>=strategy.threshold)&p.eligible[day+1]
            bought=np.where(add,cash/(execution*ENTRY),0.)
            entry=np.where(bought>0,(entry*q+execution*1.0005*bought)/np.maximum(q+bought,1e-30),entry)
            cash-=bought*execution*ENTRY;q+=bought;added|=add
            worst=np.minimum(worst,cash+q*execution)
        y[t]=cash-1; downside[t]=np.minimum(0,worst-1)
    return y,downside


def fit(p, strategy, train_end=504, calibration_end=756):
    z=p.features[strategy.family]; ix=np.digitize(z,BOUNDARIES)
    y,down=strategy_outcomes(p,strategy,calibration_end)
    valid=p.eligible & p.screen_mask & np.isfinite(z) & (z>=strategy.threshold)
    rows=[]
    for b in range(6):
        mask=valid & (ix==b) & np.isfinite(y)
        train=mask.copy(); train[train_end-strategy.horizon-1:]=False
        cal=mask.copy(); cal[:train_end]=False
        # Separate later calibration dates; shrink small date samples to train mean.
        a=y[train]; c=y[cal]; days=int(np.count_nonzero(cal.any(axis=1)))
        weight=days/(days+30) if len(c) else 0.
        mean=(1-weight)*(float(a.mean()) if len(a) else 0.)+weight*(float(c.mean()) if len(c) else 0.)
        sample=y[mask]; adverse=down[mask]
        rows.append(dict(expected_net_return=mean,downside_p10=float(np.quantile(adverse,.1)) if len(adverse) else None,
                         probability_positive=float(np.mean(sample>0)) if len(sample) else None,
                         confidence=min(1.,days/max(1,3*strategy.horizon)),calibration_dates=days,
                         samples=len(sample),supported=bool(len(a)>=100 and days>=20)))
    return dict(label_basis='stock_policy_committed_capital_2_3_entry_1_3_add_reserve',strategy=asdict(strategy),cutoff=str(p.dates[calibration_end].date()),bins=rows)


def arrays(p, model):
    s=Strategy(**model['strategy']); z=p.features[s.family]; ix=np.digitize(z,BOUNDARIES)
    mean=np.array([r['expected_net_return'] for r in model['bins']])[ix]
    supported=np.array([r['supported'] for r in model['bins']])[ix]
    valid=np.isfinite(z)&supported&(z>=s.threshold)&p.eligible
    # Existing capital avoids charging the sunk entry cost again.
    hold=np.where(valid,((mean+1)*ENTRY-1)/s.horizon,np.nan)
    signal=np.where(valid & (mean>0),mean/s.horizon,-np.inf)
    return signal[None],hold[None]


def allocate(p, model, start, end, detail=True):
    """GA9-B compatibility: absolute net expected return/session competes for cash.

    A emits no portfolio weights. B owns slots, correlation, settlement and caps.
    """
    s=Strategy(**model['strategy']); signal,hold=arrays(p,model)
    return replay(p,[s.gene()],Manager(slots=10,reserve=.1,risk_cap=.008,replacement=.0001),
                  p.dates[start],p.dates[end-1]+pd.Timedelta(days=1),detail=detail,
                  signal=signal,hold_signal=hold,edge_mode=True,absolute_edges=True)


def opportunity(p, model, t, j):
    s=Strategy(**model['strategy']); z=p.features[s.family][t,j]
    row=model['bins'][int(np.digitize(z,BOUNDARIES))]
    return dict(as_of=str(p.dates[t].date()),ticker=p.symbols[j],strategy=asdict(s),
                execution='NEXT_SESSION_OPEN',horizon_sessions=s.horizon,return_unit='fraction_of_committed_capital',
                confidence_basis='calibration_date_support_not_probability_of_profit',**row,
                entry_eligible=bool(p.eligible[t,j] and p.screen_mask[t,j] and np.isfinite(z) and z>=s.threshold and row['supported'] and row['expected_net_return']>0),
                action_policy=dict(entry='positive supported net forecast in discovery pool',
                                   hold='positive remaining net forecast; original horizon expiry applies',
                                   add=f'gain >= {s.add}; positive new-capital forecast; once per position',
                                   reduce=f'gain <= {s.reduce}; half position once',
                                   exit='nonpositive remaining forecast, horizon, membership, 2% loss or trailing stop'))

FILE ga9/benchmarks.py
"""Predeclared market benchmark policy and independent PIT universe diagnostic."""
from dataclasses import dataclass, replace
from pathlib import Path
import numpy as np
import pandas as pd
from .execution import Panel, load_panel
from .input_audit import inspect_prices

DEFAULT_SPY = Path('/opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet')
SECONDARY = 'equal_weight_buy_and_hold_complete_PIT_universe'


@dataclass(frozen=True)
class BenchmarkPolicy:
    universe_profile: str = 'broad_us'

    def __post_init__(self):
        if self.universe_profile not in ('broad_us','nasdaq'):
            raise ValueError('Universe profile must be broad_us or nasdaq')

    @property
    def primary(self):
        return 'QQQ' if self.universe_profile == 'nasdaq' else 'SPY'

    def record(self):
        return dict(universe_profile=self.universe_profile,primary=self.primary,secondary=SECONDARY,
                    selection='declared before training and forward; no outcome-based switching')


def align(panel, dates):
    ix=panel.dates.get_indexer(dates)
    if (ix<0).any():
        missing=dates[ix<0].strftime('%Y-%m-%d').tolist()
        raise ValueError(f'Benchmark missing strategy sessions: {missing[:5]}')
    return replace(panel,dates=dates,open=panel.open[ix],close=panel.close[ix],
                   dividends=panel.dividends[ix],returns=panel.returns[ix],
                   features={k:v[ix] for k,v in panel.features.items()},
                   niche=panel.niche[ix],breadth=panel.breadth[ix],
                   eligible=panel.eligible[ix] if panel.eligible is not None else None,
                   screen_score=panel.screen_score[ix] if panel.screen_score is not None else None,
                   screen_mask=panel.screen_mask[ix] if panel.screen_mask is not None else None)


def load_primary(path, policy, end, dates):
    if path is None:
        raise FileNotFoundError(f'{policy.primary} requires --benchmark-data with verified OHLC/dividends; no benchmark fallback')
    path=Path(path)
    d=pd.read_parquet(path)
    # A one-instrument file without ticker must identify the declared ETF in its name.
    if 'ticker' not in d:
        if path.stem.upper().split('_')[0] != policy.primary:
            raise ValueError(f'Unidentified single-instrument file: expected {policy.primary} filename or ticker column')
        d['ticker']=policy.primary
    d=d[d.ticker==policy.primary].copy()
    if d.empty:
        raise ValueError(f'Required primary {policy.primary} is absent; no benchmark fallback')
    d['date']=pd.to_datetime(d.date)
    d=d[(d.date>='2022-01-01')&(d.date<end)].sort_values('date')
    required={'dividends','stock_splits'}
    if not required.issubset(d.columns):
        raise ValueError(f'{policy.primary} missing explicit dividends or split data')
    audit=inspect_prices(d)
    if not audit['usable'] or not np.isfinite(d.dividends).all() or (d.dividends<0).any():
        raise ValueError(f'Invalid {policy.primary} OHLC/dividend data')
    jumps=d.close/d.close.shift(1)
    if (((jumps<.5)|(jumps>1.8)) & (d.stock_splits>0)).any():
        raise ValueError('Ambiguous ETF split normalization')
    c=d.close.to_numpy()[:,None];o=d.open.to_numpy()[:,None];div=d.dividends.to_numpy()[:,None]
    returns=(c+div)/np.vstack([np.full((1,1),np.nan),c[:-1]])-1
    panel=Panel(pd.DatetimeIndex(d.date),[policy.primary],o,c,div,returns,{},
                np.zeros_like(c,dtype=int),np.zeros(len(d)))
    panel=align(panel,dates)
    if not np.isfinite(panel.open).all() or not np.isfinite(panel.close).all():
        raise ValueError('Primary ETF requires every strategy session; no cash substitution')
    return panel,audit


def attach_primary(panel, path, policy, end):
    primary,audit=load_primary(path,policy,end,panel.dates)
    return replace(panel,primary_benchmark=primary),audit


def load_universe(path, symbols, end, dates, membership=None):
    panel,audit=load_panel(path,end=end,sample=symbols,membership=membership)
    return align(panel,dates),audit


def primary_name(panel):
    if panel.primary_benchmark is not None:
        return panel.primary_benchmark.symbols[0]
    if panel.synthetic_benchmark_fixture:
        return 'synthetic_equal_weight_fixture'
    raise ValueError('Primary SPY/QQQ benchmark must be attached; equal-weight fallback is forbidden')


def selection_benchmark(panel,start,end):
    from .objective import benchmark
    name=primary_name(panel)
    source=panel.primary_benchmark if panel.primary_benchmark is not None else panel
    result=benchmark(source,start,end)
    result['benchmark_id']=name
    return result
