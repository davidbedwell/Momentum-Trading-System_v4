"""Independent fixed-request GA7 ledger; not a second native policy implementation.

Only a single frozen genome, empty opening holdings, adjusted prices and ex-date
cash dividends are supported. Raw split accounting and pay-date dividends need
another contract. Requests remain fixed in counterfactual convention comparisons.
"""
from math import isfinite
from types import SimpleNamespace


def replay(genome, sessions, requests, *, capital=100000., fee=.001,
           fractional=False, capacity_limits=True, receivables_in_equity=False,
           terminal_liquidation=True):
    if not isfinite(capital) or capital <= 0 or not 0 <= fee < 1:
        raise ValueError('invalid opening cash/fee')
    if len(sessions) < 2 or len(sessions) > 504:
        raise ValueError('bounded sessions required')
    dates = [d for d, _, _ in sessions]
    if dates != sorted(set(dates)):
        raise ValueError('ordered unique sessions required')
    if not 0 < genome.stop_pct <= 1 or genome.capacity < 1:
        raise ValueError('invalid native sizing contract')
    tape = {}
    seen = set()
    for p in requests:
        p = SimpleNamespace(**p) if isinstance(p, dict) else p
        if type(p.session) is not int or not 0 <= p.session < len(sessions)-1:
            raise ValueError('request outside decision interval')
        if p.action not in ('ENTER', 'INCREASE', 'EXIT', 'REDUCE', 'HOLD', 'PASS'):
            raise ValueError('unsupported native action')
        if (p.session, p.ticker) in seen:
            raise ValueError('duplicate request')
        seen.add((p.session, p.ticker))
        if p.chromosome_id != genome.identity():
            raise ValueError('single frozen genome required')
        if not all(isfinite(v) for v in (p.requested_weight, p.probability,
                                         p.expected_net_return, p.downside_risk, p.confidence)):
            raise ValueError('nonfinite request')
        if not 0 <= p.requested_weight <= .30:
            raise ValueError('invalid requested weight')
        tape.setdefault(p.session, []).append(p)
    # Validate before any ledger mutation; no absent action coverage is invented.
    for _, bars, _ in sessions:
        for b in bars.values():
            if not all(isfinite(b[k]) and b[k] > 0 for k in ('open', 'close')):
                raise ValueError('invalid market price')
            if b.get('split', 1.) != 1.:
                raise ValueError('raw split event unsupported: adjusted prices required')
            if not isfinite(b.get('dividend', 0.)) or b.get('dividend', 0.) < 0:
                raise ValueError('invalid dividend')
    cash = capital
    holdings = {}
    unsettled = []
    journal = []
    fills = []
    daily = []
    rejected = []
    priority = {'EXIT': 0, 'REDUCE': 1, 'HOLD': 2, 'INCREASE': 3, 'ENTER': 4, 'PASS': 5}
    def key(p):
        utility = p.probability*p.expected_net_return-(1-p.probability)*p.downside_risk
        return priority[p.action], -utility, -p.confidence, p.ticker, p.chromosome_id
    def credit(i, kind, amount):
        nonlocal cash
        cash += amount
        journal.append((i, kind, amount))
    def sell(i, t, qty, price, terminal=False):
        amount = qty*price*(1-fee)
        if terminal:
            credit(i, 'TERMINAL_SELL', amount)
        else:
            unsettled.append((i+1, amount))
        holdings[t]['shares'] -= qty
        fills.append((i, t, 'SELL', qty, price, qty*price*fee))
        if holdings[t]['shares'] <= 1e-12:
            del holdings[t]
    for i, (date, bars, defense) in enumerate(sessions):
        missing = set(holdings)-set(bars)
        if missing:
            raise ValueError('missing held bar')
        due = sum(v for release, v in unsettled if release <= i)
        unsettled = [(release, v) for release, v in unsettled if release > i]
        credit(i, 'SETTLEMENT', due)
        for t, p in holdings.items():
            credit(i, 'DIVIDEND', p['shares']*bars[t].get('dividend', 0.))
        for p in sorted(tape.get(i-1, []), key=key):
            t = p.ticker
            if t not in bars:
                rejected.append((i, t, 'missing candidate bar'))
                continue
            b = bars[t]
            price = b['open']
            held = holdings.get(t)
            if p.action in ('EXIT', 'REDUCE') and held:
                qty = held['shares'] if p.action == 'EXIT' else (
                    held['shares']/2 if fractional else max(1, held['shares']//2))
                sell(i, t, qty, price)
            elif p.action in ('ENTER', 'INCREASE'):
                if defense or sessions[i-1][2] or not b['eligible']:
                    rejected.append((i, t, 'defense/eligibility'))
                    continue
                if not held and capacity_limits and (len(holdings) >= genome.capacity or
                    sum(v['sector'] == b.get('sector', 'UNKNOWN') for v in holdings.values()) >= 3):
                    rejected.append((i, t, 'capacity/sector'))
                    continue
                equity = cash+sum(v['shares']*bars[s]['open'] for s, v in holdings.items())
                if receivables_in_equity:
                    equity += sum(v for _, v in unsettled)
                if held and p.action == 'INCREASE':
                    exposure = held['shares']*price
                    budget = min(cash, max(0., equity*.30-exposure),
                                 equity*p.requested_weight, max(0., equity*.02/genome.stop_pct-exposure))
                elif not held:
                    budget = min(cash, equity*p.requested_weight, equity*.02/genome.stop_pct)
                else:
                    continue
                qty = budget/(price*(1+fee))
                if not fractional:
                    qty = int(qty)
                if qty <= 0:
                    rejected.append((i, t, 'cash/rounding/risk'))
                    continue
                credit(i, 'BUY', -qty*price*(1+fee))
                holdings.setdefault(t, dict(shares=0., sector=b.get('sector', 'UNKNOWN')))['shares'] += qty
                fills.append((i, t, 'BUY', qty, price, qty*price*fee))
        receivable = sum(v for _, v in unsettled)
        # Independently reconstruct cash plus receivables from executions.
        flow = sum((1 if side == 'SELL' else -1)*q*price-f
                   for _, _, side, q, price, f in fills)
        dividends = sum(v for _, kind, v in journal if kind == 'DIVIDEND')
        residual = cash+receivable-(capital+flow+dividends)
        if cash < -1e-7 or abs(residual) > 1e-7:
            raise ArithmeticError('bridge cashflow mismatch')
        daily.append(dict(date=date, cash=cash, receivable=receivable,
                          holdings={t: p['shares'] for t, p in holdings.items()},
                          nav=cash+receivable+sum(p['shares']*bars[t]['close'] for t,p in holdings.items()),
                          cashflow_residual=residual))
    terminal_fee = sum(p['shares']*sessions[-1][1][t]['close']*fee for t,p in holdings.items())
    if terminal_liquidation:
        for t, p in list(holdings.items()):
            sell(len(sessions)-1, t, p['shares'], sessions[-1][1][t]['close'], True)
        credit(len(sessions)-1, 'TERMINAL_SETTLEMENT', sum(v for _, v in unsettled))
        unsettled = []
    final_nav = cash+sum(v for _, v in unsettled)+sum(p['shares']*sessions[-1][1][t]['close'] for t,p in holdings.items())
    total_flow = sum((1 if side == 'SELL' else -1)*q*price-f
                     for _, _, side, q, price, f in fills)
    total_dividends = sum(v for _, kind, v in journal if kind == 'DIVIDEND')
    terminal_residual = cash+sum(v for _,v in unsettled)-(capital+total_flow+total_dividends)
    if abs(terminal_residual) > 1e-7:
        raise ArithmeticError('terminal cashflow mismatch')
    return dict(final_nav=final_nav, daily=daily, fills=fills, journal=journal,
                terminal_cashflow_residual=terminal_residual,
                rejected=rejected, terminal_fee=terminal_fee,
                max_cashflow_residual=max(abs(d['cashflow_residual']) for d in daily))
