"""Independent fill-journal accounting interpreter for bounded research books."""
from math import isfinite


def funded_shadow(*, owners, sessions, bars, fills, nav_history, capital=100000.,
                  fee=.001, settlement_sessions=1):
    """Rebuild cash, receivables, splits, dividends and NAV from public journals.

    Does not read the book's internal cash or positions. This proves the stated
    convention's accounting identity, not native/broker convention equivalence.
    """
    owners = tuple(owners)
    cash = dict.fromkeys(owners, capital)
    receivables = {o: [] for o in owners}
    shares = {o: {} for o in owners}
    expected = {(s, o): (c, u, n) for s, o, c, u, n in nav_history}
    if len(expected) != len(nav_history) or len(expected) != len(sessions)*len(owners):
        raise ValueError('incomplete or duplicate owner NAV journal')
    journal = {i: [] for i in range(len(sessions))}
    for fill in fills:
        s, key, side, qty, price, paid = fill
        if s not in journal or key[:2] not in cash or side not in ('BUY', 'SELL'):
            raise ValueError('invalid journal attribution')
        if not all(isfinite(v) for v in (qty, price, paid)) or min(qty, price) <= 0 or abs(paid-qty*price*fee)>1e-7:
            raise ValueError('journal fill/fee mismatch')
        journal[s].append(fill)
    worst = 0.
    for i, date in enumerate(sessions):
        market = bars[date]
        for o in owners:
            cash[o] += sum(v for due,v in receivables[o] if due <= i)
            receivables[o] = [(d,v) for d,v in receivables[o] if d > i]
            for t in shares[o]:
                shares[o][t] *= market[t].split
                cash[o] += shares[o][t]*market[t].dividend
        for _, key, side, qty, price, paid in journal[i]:
            o, t = key[:2], key[2]
            if abs(price-market[t].open)>1e-10:
                raise ValueError('fill is not the dated next open')
            direction = 1 if side == 'BUY' else -1
            shares[o][t] = shares[o].get(t, 0.)+direction*qty
            if side == 'BUY':cash[o] -= qty*price+paid
            else:receivables[o].append((i+max(1,settlement_sessions),qty*price-paid))
            if cash[o] < -1e-7 or shares[o][t] < -1e-7:
                raise ValueError('journal borrowed settled cash or shares')
        for o in owners:
            unsettled = sum(v for _,v in receivables[o])
            nav = cash[o]+unsettled+sum(q*market[t].close for t,q in shares[o].items())
            residual = max(abs(a-b) for a,b in zip((cash[o],unsettled,nav),expected[i,o]))
            worst = max(worst,residual)
            if residual > 1e-7:raise ValueError('independent owner ledger mismatch')
    return dict(owner_sessions=len(expected),fills=len(fills),max_residual=worst,
                status='RESEARCH_JOURNAL_RECONCILED',native_ledger_parity=False)
