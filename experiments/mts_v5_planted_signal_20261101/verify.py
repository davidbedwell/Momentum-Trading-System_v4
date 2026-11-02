#!/usr/bin/env python3
"""Verify persisted evidence without executing any additional portfolios."""
import csv
import hashlib
import inspect
import json
import math
import statistics as st
import sys

import run as m


def read(name):
    with (m.OUT/name).open() as f:
        return list(csv.DictReader(f))


def near(a, b, tolerance=1e-9):
    assert abs(float(a)-float(b)) < tolerance, (a, b)


def main():
    report = json.loads((m.OUT/'report.json').read_text())
    runs = read('runs.csv')
    assert len(runs) == 336
    assert len({(r['seed'], r['quality'], r['variant']) for r in runs}) == 336
    assert len({r['seed'] for r in runs}) == 12
    assert not report['failures']
    for path, sha in report['source_sha256'].items():
        assert hashlib.sha256(m.Path(path).read_bytes()).hexdigest() == sha
    assert hashlib.sha256((m.OUT/'run.py').read_bytes()).hexdigest() == report['runner_sha256']
    validated_observations = 0
    callback_closure_names = set()
    for seed in m.SEEDS:
        days, tapes, returns = m.generate(seed)  # DGP regeneration, no replay
        saved = read(f'{seed}_joint_tape.csv')
        assert len(saved) == m.N*m.K*4
        for row in saved:
            i = m.DATES.index(row['date'])
            j = int(row['ticker'][3:])
            near(row['predictor'], tapes[row['quality']][i][j])
            near(row['forward_return'], returns[i][j])
            near(row['predicted_gross'], m.expected(float(row['predictor']), row['quality']))
            if i < m.N-2:
                # Independent economic timing identity: held from next open to next-next open.
                marked = days[i+2][1][row['ticker']].open/days[i+1][1][row['ticker']].open-1
                near(marked, row['forward_return'])
            validated_observations += 1
        m.write_csv(f'{seed}_input_prices.csv', [dict(date=d, ticker=t, open=b.open, close=b.close)
                                               for d, bars in days for t, b in bars.items()])
        for q, tape in tapes.items():
            base = m.callback_factory(tape, q, 'baseline', seed)
            shuffled = m.callback_factory(tape, q, 'rank_shuffle', seed)
            for callback in (*base[:4], *shuffled[:4]):
                closure = inspect.getclosurevars(callback).nonlocals
                assert not {'returns', 'days', 'bars', 'forward_return'} & set(closure)
                callback_closure_names.update(closure)
            for i, d in enumerate(m.DATES):
                candidates = [m.Candidate(t, 'GA7', 'synthetic', .02, m.GAPS[j]) for j, t in enumerate(m.TICKERS)]
                a = [base[3](c, c.chromosome_id, d) for c in candidates]
                b = [shuffled[3](c, c.chromosome_id, d) for c in candidates]
                assert [v > 0 for v in a] == [v > 0 for v in b]
                assert sorted(v for v in a if v > 0) == sorted(v for v in b if v > 0)
        # Same-universe controls must have identical results across qualities.
        for v in ('buy_hold', 'cash'):
            controls = [r for r in runs if int(r['seed']) == seed and r['variant'] == v]
            assert len({r['final_nav'] for r in controls}) == 1
            assert len({r['turnover'] for r in controls}) == 1
    for row in runs:
        prefix = f"{int(row['seed'])}_{row['quality']}_{row['variant']}"
        daily = read(prefix+'_daily.csv')
        assert len(daily) == m.N
        near(daily[-1]['nav'], row['final_nav'])
        near((float(daily[-1]['nav'])/m.INITIAL)**(252/m.N)-1, row['cagr'])
        near(st.mean(float(d['exposure']) for d in daily), row['exposure'])
        near(sum(float(d['gross_traded_notional'])/float(d['nav']) for d in daily), row['turnover'])
        peak, mdd = m.INITIAL, 0.
        for d in daily:
            peak = max(peak, float(d['nav']))
            mdd = max(mdd, 1-float(d['nav'])/peak)
        near(mdd, row['mdd'])
        assert float(row['max_reconciliation_error']) < 1e-6
        assert float(row['max_modeled_trade_loss']) <= .02+1e-10
        if row['quality'] == 'null' and row['variant'] != 'buy_hold':
            assert float(row['fills']) == 0
    bins = read('calibration_bins.csv')
    for seed in m.SEEDS:
        null_bins = [r for r in bins if int(r['seed']) == seed and r['quality'] == 'null']
        assert len(null_bins) == 1 and int(null_bins[0]['n']) == 6000
    dependency_hashes = {}
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and path.startswith('/opt/Momentum-Trading-System_v5-alpha/') and path.endswith('.py'):
            dependency_hashes[path] = hashlib.sha256(m.Path(path).read_bytes()).hexdigest()
    result = dict(status='PASS', retained_portfolios=336, additional_portfolio_runs=0,
                  tape_observations_verified=validated_observations,
                  next_open_forward_timing='PASS', callback_closure_inspection=sorted(callback_closure_names),
                  rank_shuffle_positive_mask_and_multiset='PASS', control_quality_invariance='PASS',
                  daily_metric_recomputation='PASS', source_and_runner_hashes='PASS',
                  note='Closure inspection establishes harness separation, not general proof of arbitrary callback safety. Oracle predictor is intentionally clairvoyant.',
                  runtime_dependency_sha256=dependency_hashes)
    (m.OUT/'verification.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'runtime_dependency_sha256'}, indent=2))


if __name__ == '__main__':
    main()
