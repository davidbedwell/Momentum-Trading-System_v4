"""Causal close-time trim proposals; overnight gaps may still exceed cap."""
from engines.portfolio_replay.kernel import Signal

def enforce(signals, shares, bars, nav, owners, cap=.10):
    if nav<=0 or not 0<cap<=1:raise ValueError('invalid portfolio NAV or cap')
    by_ticker={s.ticker:s for s in signals}
    for ticker,qty in shares.items():
        weight=qty*bars[ticker].close/nav
        if weight>cap:
            owner=owners[ticker]
            previous=by_ticker.get(ticker)
            target=min(cap,previous.target_weight) if previous else cap
            by_ticker[ticker]=Signal(ticker,'GA6',owner,target,score=1e6)
    return list(by_ticker.values())
