"""Translate executed GA7-owned positions into native daily decision state.
Only confirmed fills may create ownership; no signal-only phantom holdings.
"""

def held_state(shares,owners,entry_prices,stops,nav,bars,chromosome_id):
    if nav<=0:raise ValueError('invalid equity')
    result={}
    for ticker,qty in shares.items():
        if owners.get(ticker)!=('GA7',chromosome_id):continue
        if ticker not in bars or ticker not in entry_prices:
            raise ValueError('missing held-position evidence')
        close=float(bars[ticker].close)
        entry=float(entry_prices[ticker])
        stop=float(stops[ticker])
        weight=float(qty)*close/nav
        if entry<=0 or close<=0 or qty<=0 or not 0<stop<=.02 or not 0<weight<=1.:
            raise ValueError('invalid native position')
        result[ticker]={'entry':entry,'initial_stop':stop,'weight':weight}
    return result
