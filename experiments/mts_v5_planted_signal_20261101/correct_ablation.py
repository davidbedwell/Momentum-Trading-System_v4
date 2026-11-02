#!/usr/bin/env python3
"""One-time bounded correction of admission-confounded initial shuffle ablation.

Primary run.py already contains the correction for clean reproductions.
This executes exactly 48 replacements, then stops; never searches parameters.
"""
import hashlib
import json
import statistics as st
import time
from collections import Counter

import run as m


def main():
    start = time.monotonic()
    report = json.loads((m.OUT/'report.json').read_text())
    if 'execution_correction' in report:
        raise SystemExit('Correction already executed; refusing extra simulations.')
    import csv
    rows = list(csv.DictReader((m.OUT/'runs.csv').open()))
    # Restore original scalar types from the CSV to avoid mixing strings/numbers.
    for row in rows:
        for k, v in list(row.items()):
            if k in ('quality', 'variant'):
                continue
            row[k] = None if v == '' else (v == 'True' if v in ('True', 'False') else float(v))
        row['seed'] = int(row['seed'])
    calibration, bins = [], []
    count = 0
    for seed in m.SEEDS:
        days, tapes, returns = m.generate(seed)
        for quality, tape in tapes.items():
            cal, bb = m.calibration(seed, quality, tape, returns)
            calibration.append(cal)
            bins.extend(bb)
            classify, eligible, native, ev, counts = m.callback_factory(tape, quality, 'rank_shuffle', seed)
            candidates = [m.Candidate(t, 'GA7', 'synthetic', .02, m.GAPS[j]) for j, t in enumerate(m.TICKERS)]
            result = m.run_slice(days, candidates, classify=classify, eligible=eligible, native=native,
                                 conditional_ev=ev, max_sessions=m.N, max_stocks=m.K,
                                 retain_audit=True, mdd_limit=.20, **m.COSTS)
            mm, daily = m.measure(result, days)
            reasons = Counter(a.get('funding_reason') for a in result['decisions'] if a.get('funding_reason'))
            replacement = dict(seed=seed, quality=quality, variant='rank_shuffle', **mm,
                               signal_exits=counts['EXIT'], switch_exit_decisions=counts['signal_switch_exit'],
                               denied_queue_increases=reasons['NO_SETTLED_CASH_OR_RISK_BUDGET'])
            position = next(i for i, r in enumerate(rows) if (r['seed'], r['quality'], r['variant']) == (seed, quality, 'rank_shuffle'))
            rows[position] = replacement
            prefix = f'{seed}_{quality}_rank_shuffle'
            m.write_csv(prefix+'_daily.csv', daily)
            fills_path = m.OUT/(prefix+'_fills.csv')
            if fills_path.exists():
                fills_path.unlink()
            m.write_csv(prefix+'_fills.csv', [dict(date=f[0], ticker=f[1], side=f[2], quantity=f[3], price=f[4], fee=f[5]) for f in result['ledger']])
            if seed == m.SEEDS[0]:
                (m.OUT/(prefix+'_audit.json')).write_text(json.dumps(dict(decisions=result['decisions'], risk=result['risk_audit'],
                                                                         mdd_policy=result['mdd_policy']), separators=(',', ':')))
            count += 1
        print(f'corrected seed={seed} replacement_runs={count}', flush=True)
    aggregates = []
    for q in m.QUALITIES:
        for v in m.VARIANTS:
            rr = [r for r in rows if r['quality'] == q and r['variant'] == v]
            agg = dict(quality=q, variant=v, runs=len(rr))
            for key in ('cagr', 'mdd', 'calmar', 'exposure', 'turnover', 'fills', 'signal_exits'):
                values = [r[key] for r in rr if r[key] is not None]
                for label, fn in (('mean', st.mean), ('min', min), ('max', max)):
                    agg[key+'_'+label] = fn(values) if values else None
            agg['mdd_latch_count'] = sum(r['mdd_latched'] for r in rr)
            aggregates.append(agg)
    paired = []
    for q in m.QUALITIES:
        for v in m.VARIANTS[1:]:
            deltas = []
            for seed in m.SEEDS:
                a = next(r for r in rows if (r['seed'], r['quality'], r['variant']) == (seed, q, 'baseline'))
                b = next(r for r in rows if (r['seed'], r['quality'], r['variant']) == (seed, q, v))
                deltas.append(b['cagr']-a['cagr'])
            paired.append(dict(quality=q, variant=v, n=len(deltas), mean_cagr_delta_vs_baseline=st.mean(deltas),
                               sd_across_seeds=st.stdev(deltas), wins=sum(d > 0 for d in deltas)))
    m.write_csv('runs.csv', rows)
    m.write_csv('aggregate.csv', aggregates)
    m.write_csv('paired.csv', paired)
    m.write_csv('calibration.csv', calibration)
    m.write_csv('calibration_bins.csv', bins)
    report.update(aggregates=aggregates, paired=paired, calibration=calibration)
    report['original_runner_sha256'] = report['runner_sha256']
    report['runner_sha256'] = hashlib.sha256((m.OUT/'run.py').read_bytes()).hexdigest()
    report['execution_correction'] = dict(reason='Preserve positive-EV admission mask in rank shuffle; collapse tied null EV calibration to one bin.',
                                           replacement_runs=count, discarded_runs=count, total_manager_runs_executed=384,
                                           retained_runs=336, elapsed_seconds=time.monotonic()-start,
                                           original_shuffled_results_excluded=True, portfolio_parameter_search=False)
    report['methodology'] = dict(dgp=dict(phi=m.PHI, alpha=m.ALPHA, sigma=m.SIGMA, log_drift=m.DRIFT,
                                          cluster_epsilon_loading=.6, market_epsilon_loading=.3,
                                          idiosyncratic_epsilon_loading='.55**.5', predictor_rho=m.QUALITIES),
                                signal_horizon_sessions=1, execution='close t decision, open t+1 fill, open t+2 forward markout',
                                calibration_sessions=250, calibration_net_cost='Subtract fixed 30bp round-trip allowance from both expected and realized one-session simple returns.',
                                exit_rule='gross EV < -15bp, or rank below top 10 and top-10 cutoff exceeds incumbent by 40bp with positive entrant net EV.',
                                gap_risk='Fixed synthetic stress estimates 3%,6%,12%,24%; not fitted to or validated by the price DGP.',
                                rank_shuffle='Permute positive scores among positive candidates at each close; preserve all admission masks and native signal rules.',
                                exposure='Mean daily close equity / NAV', turnover='Sum absolute executed dollar notional / same-day close NAV; buys and sells both count.',
                                costs='Illustrative small-liquid-trade assumptions, not a fitted liquidity or cost model.',
                                controls='Cash and buy-hold use the same actual run_slice/Replay.day path; same dates, tapes, settlement, costs and risk policies.')
    report['limits'].append('Correctly calibrated null EV is always negative after costs, so null abstention does not test robustness to positive EV miscalibration.')
    (m.OUT/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False))
    print(json.dumps(report['execution_correction'], indent=2))


if __name__ == '__main__':
    main()
