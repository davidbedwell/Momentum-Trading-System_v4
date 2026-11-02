"""Observed portfolio fitness for paired defense paths."""
from math import isfinite

def metrics(nav, annual_sessions=252):
    values = [float(row[1]) for row in nav]
    if len(values) < 2 or any(not isfinite(v) or v <= 0 for v in values):
        raise ValueError('invalid portfolio NAV')
    peak = values[0]
    drawdown = 0.
    for value in values:
        peak = max(peak, value)
        drawdown = max(drawdown, 1-value/peak)
    cagr = (values[-1]/values[0])**(annual_sessions/(len(values)-1))-1
    return {'cagr':cagr, 'mdd':drawdown, 'calmar':cagr/drawdown if drawdown else None}

def paired(replay, benchmark_cagr, mdd_limit=.20):
    if not isfinite(benchmark_cagr): raise ValueError('invalid benchmark')
    outcomes = {}
    for enabled in (False, True):
        result = replay(enabled)
        if result is None: raise ValueError('missing defense replay')
        outcome = metrics(result['nav'])
        outcome['excess_cagr_pp'] = 100*(outcome['cagr']-benchmark_cagr)
        outcome['risk_eligible'] = outcome['mdd'] <= mdd_limit
        outcomes['on' if enabled else 'off'] = outcome
    return outcomes
