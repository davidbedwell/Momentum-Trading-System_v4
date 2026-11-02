#!/usr/bin/env python3
"""Stage 1 synthetic diagnostics. Standard library only; no GA or source patching."""
import csv
import hashlib
import inspect
import json
import math
import random
import statistics as st
import time
import traceback
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from discovery.competitive_ga.functional_niche_manager import Candidate, NicheObservation, run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar, Replay, Signal

OUT = Path(__file__).resolve().parent
SEEDS = tuple(range(1101, 1113))
N = 252
K = 24
INITIAL = 100000.
PHI = .85
ALPHA = .006
SIGMA = .008
DRIFT = .0002
COSTS = dict(fees=.0005, spread=.001, slippage=.0003, impact=.0002)
FRICTION = .001
ROUND_TRIP = .003
QUALITIES = dict(oracle=None, strong=.85, weak=.25, null=0.)
VARIANTS = ('baseline', 'risk_score', 'cluster_score', 'rank_shuffle', 'equal_eligible', 'buy_hold', 'cash')
TICKERS = tuple(f'SYN{j:02}' for j in range(K))
GAPS = tuple((.03, .06, .12, .24)[j % 4] for j in range(K))


def write_csv(name, rows):
    if not rows:
        return
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def dates():
    d = date(2030, 1, 2)
    result = []
    while len(result) < N:
        if d.weekday() < 5:
            result.append(d.isoformat())
        d += timedelta(days=1)
    return result


DATES = dates()


def generate(seed):
    """Joint generative law; returns NEVER captured by callback factory."""
    rng = random.Random(seed)
    z = [rng.gauss(0, 1) for _ in TICKERS]
    noise = [rng.gauss(0, 1) for _ in TICKERS]
    predictors = {q: [] for q in QUALITIES}
    returns = []
    for i in range(N):
        # Four correlated groups of six assets; independent latent alpha paths.
        cluster = [rng.gauss(0, 1) for _ in range(4)]
        common = rng.gauss(0, 1)
        rr = []
        pp = {q: [] for q in QUALITIES}
        for j in range(K):
            z[j] = PHI*z[j] + math.sqrt(1-PHI**2)*rng.gauss(0, 1)
            noise[j] = PHI*noise[j] + math.sqrt(1-PHI**2)*rng.gauss(0, 1)
            eps = .3*common + .6*cluster[j//6] + math.sqrt(.55)*rng.gauss(0, 1)
            logret = DRIFT + ALPHA*z[j] + SIGMA*eps
            rr.append(math.expm1(logret))
            for q, rho in QUALITIES.items():
                # Oracle is deliberately a clairvoyant synthetic upper-bound input.
                # It is still handed over as a predictor, never as a return argument.
                p = logret if rho is None else rho*z[j] + math.sqrt(1-rho*rho)*noise[j]
                pp[q].append(p)
        returns.append(tuple(rr))
        for q in QUALITIES:
            predictors[q].append(tuple(pp[q]))
    prices = [100.+j for j in range(K)]
    days = []
    for i, d in enumerate(DATES):
        # close i -> execute open i+1 -> earn forward return i at open i+2.
        if i >= 2:
            prices = [p*(1+r) for p, r in zip(prices, returns[i-2])]
        days.append((d, {t: Bar(prices[j], prices[j]) for j, t in enumerate(TICKERS)}))
    return days, {q: tuple(v) for q, v in predictors.items()}, tuple(returns)


def expected(p, quality):
    rho = QUALITIES[quality]
    if rho is None:
        return math.expm1(p)
    # Exact one-session conditional expected simple return under the DGP.
    variance = ALPHA**2*(1-rho*rho) + SIGMA**2
    return math.expm1(DRIFT + ALPHA*rho*p + .5*variance)


def ranks(values):
    ordered = sorted(range(len(values)), key=lambda j: values[j])
    r = [0.]*len(values)
    i = 0
    while i < len(values):
        end = i+1
        while end < len(values) and values[ordered[end]] == values[ordered[i]]:
            end += 1
        for k in range(i, end):
            r[ordered[k]] = (i+end-1)/2
        i = end
    return r


def corr(a, b):
    am, bm = st.mean(a), st.mean(b)
    va = sum((x-am)**2 for x in a)
    vb = sum((x-bm)**2 for x in b)
    return sum((x-am)*(y-bm) for x, y in zip(a, b))/math.sqrt(va*vb) if va*vb else None


def calibration(seed, quality, tape, returns):
    daily_ic = [corr(ranks(p), ranks(r)) for p, r in zip(tape[:-2], returns[:-2])]
    pairs = [(expected(p, quality)-ROUND_TRIP, r-ROUND_TRIP)
             for pp, rr in zip(tape[:-2], returns[:-2]) for p, r in zip(pp, rr)]
    x, y = zip(*pairs)
    xm, ym = st.mean(x), st.mean(y)
    xx = sum((v-xm)**2 for v in x)
    slope = sum((a-xm)*(b-ym) for a, b in pairs)/xx if xx > 1e-20 else None
    ordered = sorted(pairs, key=lambda pair: pair[0])
    bins = []
    bin_count = 1 if max(x)-min(x) < 1e-15 else 5
    for k in range(bin_count):
        subset = ordered[len(pairs)*k//bin_count:len(pairs)*(k+1)//bin_count]
        bins.append(dict(seed=seed, quality=quality, bin=k+1, n=len(subset),
                         predicted_net=st.mean(a for a, b in subset), realized_net=st.mean(b for a, b in subset)))
    return dict(seed=seed, quality=quality, mean_daily_rank_ic=st.mean(daily_ic),
                pooled_ev_bias=ym-xm, calibration_slope=slope,
                calibration_intercept=ym-slope*xm if slope is not None else None,
                rmse=math.sqrt(st.mean((a-b)**2 for a, b in pairs)),
                positive_ev_fraction=st.mean(a > 0 for a in x)), bins


def callback_factory(tape, quality, variant, seed):
    """Only predictor matrix is accepted. No bars/returns/price path in closures."""
    gross = tuple(tuple(expected(p, quality) for p in row) for row in tape)
    net = tuple(tuple(v-ROUND_TRIP for v in row) for row in gross)
    score = [list(row) for row in net]
    if variant == 'rank_shuffle':
        rng = random.Random(seed+700000)
        for row in score:
            # Preserve positive-EV admission masks; destroy only queue ranking.
            positions = [j for j, v in enumerate(row) if v > 0]
            values = [row[j] for j in positions]
            rng.shuffle(values)
            for j, v in zip(positions, values):
                row[j] = v
    elif variant == 'risk_score':
        score = [[v/(max(.02, GAPS[j])+ROUND_TRIP) for j, v in enumerate(row)] for row in net]
    elif variant == 'cluster_score':
        # Static opportunity-crowding penalty, recomputed per close from predictors.
        # No iterative funded-portfolio marginal score recomputation is claimed.
        score = [[v/(1+sum(x > 0 for x in row[(j//6)*6:(j//6+1)*6])) for j, v in enumerate(row)] for row in net]
    index = {d: i for i, d in enumerate(DATES)}
    counts = Counter()

    def classify(t, d):
        return NicheObservation(d, '2029-12-31', 'SYNTHETIC_JOINT_DGP', (('synthetic', .1),))

    def eligible(c, t, d):
        return c.chromosome_id == t

    def native(c, t, d, held):
        i, j = index[d], int(t[3:])
        if variant == 'cash':
            return None
        if variant == 'buy_hold':
            action = 'HOLD' if held else ('ENTER' if i == 0 else None)
        elif held:
            # Liquidate only when signals justify paying a one-way sale cost,
            # or when a positive entrant beats incumbent by full switching cost
            # plus a 10bp buffer. No age/periodic/terminal liquidation rule.
            others = sorted(gross[i], reverse=True)
            displaced = gross[i][j] < others[9]
            switch = displaced and others[9] > ROUND_TRIP and others[9]-gross[i][j] > ROUND_TRIP+.001
            action = 'EXIT' if gross[i][j] < -.0015 or switch else 'HOLD'
            if action == 'EXIT':
                counts['signal_switch_exit' if switch else 'negative_signal_exit'] += 1
        else:
            action = 'ENTER' if net[i][j] > 0 else None
        if action is None:
            return None
        target = 0. if action == 'EXIT' else (held['weight'] if held else .10)
        if action == 'ENTER' and variant == 'buy_hold':
            target = 1/K
        elif action == 'ENTER' and variant == 'equal_eligible':
            target = min(.10, 1/max(1, sum(v > 0 for v in net[i])))
        counts[action] += 1
        return NativeProposal(d, t, c.family, c.chromosome_id, action, target,
                              gross[i][j], 'net_return_fraction', 'SYNTHETIC_NOT_NATIVE_ALPHA',
                              f'PREDICTOR_ONLY_{seed}_{quality}_{d}_{t}', '2029-12-31')

    def ev(c, t, d, *args):
        if variant in ('equal_eligible', 'buy_hold'):
            return 1.  # allocation score only; never reported as an EV estimate
        return score[index[d]][int(t[3:])]

    return classify, eligible, native, ev, counts


def measure(result, days):
    """Independently reconstruct cash, T+1, quantities and mark NAV from fills."""
    cash, shares, due = INITIAL, {}, []
    by_date = {d: [] for d, _ in days}
    for fill in result['ledger']:
        by_date[fill[0]].append(fill)
    rows = []
    peak, mdd, turnover, maxerr = INITIAL, 0., 0., 0.
    fills = 0
    for i, ((d, bars), reported) in enumerate(zip(days, result['nav'])):
        cash += sum(v for k, v in due if k <= i)
        due = [(k, v) for k, v in due if k > i]
        notional = 0.
        for _, t, side, q, p, fee in by_date[d]:
            fills += 1
            assert i > 0
            assert abs(p-bars[t].open*(1+FRICTION if side == 'BUY' else 1-FRICTION)) < 1e-7
            assert abs(fee-q*p*COSTS['fees']) < 1e-7
            notional += q*p
            if side == 'BUY':
                assert q*p+fee <= cash+1e-7, 'unsettled cash spent'
                cash -= q*p+fee
                shares[t] = shares.get(t, 0.)+q
            else:
                assert q <= shares.get(t, 0.)+1e-7
                shares[t] -= q
                due.append((i+1, q*p-fee))
        equity = sum(q*bars[t].close for t, q in shares.items())
        receivable = sum(v for _, v in due)
        nav = cash+receivable+equity
        maxerr = max(maxerr, abs(nav-reported[1]), abs(cash-reported[2]),
                     max((abs(q-reported[3].get(t, 0.)) for t, q in shares.items()), default=0.))
        assert cash >= -1e-7
        peak = max(peak, nav)
        mdd = max(mdd, 1-nav/peak)
        turnover += notional/nav
        rows.append(dict(date=d, nav=nav, cash=cash, receivable=receivable, exposure=equity/nav,
                         gross_traded_notional=notional, holdings=sum(q > 1e-8 for q in shares.values())))
    assert maxerr < 1e-6
    risk = max((x['modeled_equity_loss'] for x in result['risk_audit']), default=0.)
    assert risk <= .02+1e-10
    cagr = (nav/INITIAL)**(252/N)-1
    return dict(final_nav=nav, cagr=cagr, mdd=mdd, calmar=cagr/mdd if mdd else None,
                exposure=st.mean(r['exposure'] for r in rows), turnover=turnover,
                annualized_turnover=turnover*252/N, fills=fills,
                max_reconciliation_error=maxerr, max_modeled_trade_loss=risk,
                mdd_latched=result['admission_halted'], pending_orders=len(result['pending'])), rows


def policy_probes():
    bars = {'A': Bar(100, 100), 'B': Bar(100, 100)}
    r = Replay(cash=0, shares={'A': 1000}, high_water=INITIAL, settlement_sessions=1, **COSTS)
    r.pending = [Signal('A', 'GA7', 'a', 0), Signal('B', 'GA7', 'b', .1, stop_distance=.02, gap_risk=.03)]
    r.day('2030-01-02', bars)
    assert not r.shares and r.cash == 0 and r.unsettled
    r.pending = [Signal('B', 'GA7', 'b', .1, stop_distance=.02, gap_risk=.03)]
    r.day('2030-01-03', bars)
    assert 'B' in r.shares and not r.unsettled
    r = Replay(**COSTS)
    r.pending = [Signal('A', 'GA7', 'a', .1, stop_distance=.02, gap_risk=.8)]
    r.day('2030-01-02', bars)
    assert r.risk_audit[-1]['allowed'] < .1 and r.risk_audit[-1]['modeled_equity_loss'] <= .02+1e-12
    r = Replay(cash=20000, shares={'A': 800}, high_water=INITIAL, **COSTS)
    r.pending = [Signal('B', 'GA7', 'b', .1, stop_distance=.02, gap_risk=.03)]
    r.day('2030-01-02', {'A': Bar(50, 50), 'B': bars['B']})
    assert r.admission_halted and 'B' not in r.shares
    r.pending = [Signal('A', 'GA7', 'a', 0)]
    r.day('2030-01-03', bars)
    assert not r.shares
    return dict(settlement='PASS', loss_clipping='PASS', gap_mdd_latch_and_exits='PASS')


def main():
    start = time.monotonic()
    source_paths = sorted(Path(inspect.getsourcefile(o)) for o in (run_slice, Replay.day))
    assert all(str(p).startswith('/opt/Momentum-Trading-System_v5-alpha/') for p in source_paths)
    sources = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    summary, calibration_rows, bins, failures, tape_hashes = [], [], [], [], []
    candidates = [Candidate(t, 'GA7', 'synthetic', .02, GAPS[j]) for j, t in enumerate(TICKERS)]
    probes = policy_probes()
    for seed in SEEDS:
        if time.monotonic()-start > 900:
            failures.append(dict(reason='900 second internal hard budget reached', seed=seed))
            break
        days, tapes, returns = generate(seed)
        tape_rows = []
        for quality, tape in tapes.items():
            cal, bb = calibration(seed, quality, tape, returns)
            calibration_rows.append(cal)
            bins.extend(bb)
            for i, row in enumerate(tape):
                for j, p in enumerate(row):
                    tape_rows.append(dict(seed=seed, quality=quality, date=DATES[i], ticker=TICKERS[j],
                                          cluster=j//6, gap_estimate=GAPS[j], predictor=p,
                                          predicted_gross=expected(p, quality), forward_return=returns[i][j],
                                          realized_within_replay=i < N-2))
            tape_hashes.append(dict(seed=seed, quality=quality,
                                    sha256=hashlib.sha256(json.dumps(tape).encode()).hexdigest()))
            for variant in VARIANTS:
                try:
                    classify, eligible, native, ev, counts = callback_factory(tape, quality, variant, seed)
                    result = run_slice(days, candidates, classify=classify, eligible=eligible,
                                       native=native, conditional_ev=ev, max_sessions=N, max_stocks=K,
                                       retain_audit=True, mdd_limit=.20, **COSTS)
                    mm, daily = measure(result, days)
                    reasons = Counter(a.get('funding_reason') for a in result['decisions'] if a.get('funding_reason'))
                    summary.append(dict(seed=seed, quality=quality, variant=variant, **mm,
                                        signal_exits=counts['EXIT'], switch_exit_decisions=counts['signal_switch_exit'],
                                        denied_queue_increases=reasons['NO_SETTLED_CASH_OR_RISK_BUDGET']))
                    prefix = f'{seed}_{quality}_{variant}'
                    write_csv(prefix+'_daily.csv', daily)
                    write_csv(prefix+'_fills.csv', [dict(date=f[0], ticker=f[1], side=f[2], quantity=f[3], price=f[4], fee=f[5]) for f in result['ledger']])
                    # One full seed's decisions retained for concise functional inspection.
                    if seed == SEEDS[0]:
                        (OUT/(prefix+'_audit.json')).write_text(json.dumps(dict(decisions=result['decisions'], risk=result['risk_audit'],
                                                                                mdd_policy=result['mdd_policy']), separators=(',', ':')))
                except Exception:
                    failures.append(dict(seed=seed, quality=quality, variant=variant, reason=traceback.format_exc()))
        write_csv(f'{seed}_joint_tape.csv', tape_rows)
        print(f'seed={seed} completed runs={len(summary)} failures={len(failures)} elapsed={time.monotonic()-start:.1f}s', flush=True)
    aggregates = []
    for quality in QUALITIES:
        for variant in VARIANTS:
            rr = [r for r in summary if r['quality'] == quality and r['variant'] == variant]
            if not rr:
                continue
            agg = dict(quality=quality, variant=variant, runs=len(rr))
            for key in ('cagr', 'mdd', 'calmar', 'exposure', 'turnover', 'fills', 'signal_exits'):
                values = [r[key] for r in rr if r[key] is not None]
                agg[key+'_mean'] = st.mean(values) if values else None
                agg[key+'_min'] = min(values) if values else None
                agg[key+'_max'] = max(values) if values else None
            agg['mdd_latch_count'] = sum(r['mdd_latched'] for r in rr)
            aggregates.append(agg)
    paired = []
    for q in QUALITIES:
        for v in ('risk_score', 'cluster_score', 'rank_shuffle', 'equal_eligible', 'buy_hold', 'cash'):
            deltas = []
            for seed in SEEDS:
                a = next((r for r in summary if (r['seed'], r['quality'], r['variant']) == (seed, q, 'baseline')), None)
                b = next((r for r in summary if (r['seed'], r['quality'], r['variant']) == (seed, q, v)), None)
                if a and b:
                    deltas.append(b['cagr']-a['cagr'])
            if deltas:
                paired.append(dict(quality=q, variant=v, n=len(deltas), mean_cagr_delta_vs_baseline=st.mean(deltas),
                                   sd_across_seeds=st.stdev(deltas), wins=sum(d > 0 for d in deltas)))
    write_csv('runs.csv', summary)
    write_csv('aggregate.csv', aggregates)
    write_csv('calibration.csv', calibration_rows)
    write_csv('calibration_bins.csv', bins)
    write_csv('paired.csv', paired)
    for p in source_paths:
        assert sources[str(p)] == hashlib.sha256(p.read_bytes()).hexdigest(), 'source changed'
    report = dict(stage='Stage 1 bounded synthetic diagnostic; NO CERTIFICATION; NO HISTORICAL ALPHA',
                  completed_runs=len(summary), planned_runs=len(SEEDS)*len(QUALITIES)*len(VARIANTS),
                  seeds=SEEDS, sessions=N, assets=K, elapsed_seconds=time.monotonic()-start,
                  source_sha256=sources, runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  policy_probes=probes, costs=COSTS, round_trip_allowance=ROUND_TRIP,
                  initial_entry_cap=.10, modeled_trade_loss_limit=.02, mdd_admission_limit=.20,
                  aggregates=aggregates, calibration=calibration_rows, paired=paired,
                  tape_hashes=tape_hashes, failures=failures,
                  limits=['Synthetic callbacks, not repaired native model alpha.',
                          'Alternate scores deliberately replace conditional_ev ranking input; no true portfolio marginal recomputation.',
                          'Cluster penalty uses current positive-opportunity count, not funded holdings or fitted covariance.',
                          'Rank shuffle permutes queue scores only; native entry/exit signals stay fixed.',
                          'Equal eligible requests min(10%, 1/positive-EV-count) on entry with alphabetical cash rationing; not continuous equal-weight rebalance.',
                          'Buy-hold requests 1/24 in every asset on first close, subject to identical cash/risk gates and costs.',
                          '20% MDD latch blocks new risk, does not guarantee 20% realized maximum loss.',
                          'Modeled trade risk gate is per position, not aggregate portfolio risk.',
                          'Oracle intentionally encodes the exact forward move as its creation-time predictor.',
                          'Last two predictor observations have no in-window markout and are excluded from calibration.',
                          'One synthetic year; CAGR is annualized scenario arithmetic; correlated observations are not independent trials.'])
    (OUT/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False))
    print(json.dumps(dict(completed_runs=len(summary), failures=failures, elapsed_seconds=report['elapsed_seconds']), indent=2))


if __name__ == '__main__':
    main()
