"""Independent owner portfolios under an explicit research funding contract.

T+N is an input contract, not inferred brokerage parity. Sale proceeds never
fund same-open purchases, including under T+0. No cross-owner capital transfers.
"""
from math import isfinite
from .causal_calibration import TradeOutcome


class FundedShadow:
    def __init__(self, owners, *, sessions, capital=100000., fee=.001, settlement_sessions=1):
        if not isfinite(capital) or capital <= 0 or not isfinite(fee) or not 0 <= fee < 1:
            raise ValueError('invalid funding contract')
        if type(settlement_sessions) is not int or not 0 <= settlement_sessions <= 2:
            raise ValueError('explicit bounded settlement session lag required')
        owners = tuple(owners)
        if not owners or len(owners) > 64 or len(set(owners)) != len(owners):
            raise ValueError('require distinct bounded owners')
        if any(f not in ('GA6', 'GA7', 'HORIZONS') or not cid for f, cid in owners):
            raise ValueError('funded owner lacks executable native contract (GA4 blocked)')
        from .first_year_manifest import day
        self.sessions = tuple(day(d) for d in sessions)
        if not self.sessions or self.sessions != tuple(sorted(set(self.sessions))):
            raise ValueError('ordered explicit session calendar required')
        self.cash = dict.fromkeys(owners, float(capital))
        self.unsettled = {o: [] for o in owners}
        self.positions = {}
        self.pending = {}
        self.outcomes = []
        self.fills = []
        self.rejections = []
        self.fee = fee
        self.lag = settlement_sessions
        self.session = -1
        self.closed = False
        self.nav_history = []

    @property
    def completed(self):
        return self.outcomes

    def nav(self, owner, bars, field='close'):
        return (self.cash[owner] + sum(v for _, v in self.unsettled[owner]) +
                sum(p['shares'] * float(getattr(bars[k[2]], field))
                    for k, p in self.positions.items() if k[:2] == owner))

    def open_session(self, session, bars):
        if type(session) is not int or session >= len(self.sessions) or session != self.session + 1 or (self.session >= 0 and not self.closed):
            raise ValueError('cannot skip/repeat sessions or omit close')
        for bar in bars.values():
            if not all(isfinite(float(v)) for v in (bar.open, bar.close, bar.split, bar.dividend)) or min(bar.open, bar.close, bar.split) <= 0 or bar.dividend < 0:
                raise ValueError('invalid market/corporate action')
        if {k[2] for k in (*self.positions, *self.pending)} - set(bars):
            raise ValueError('missing shadow execution/held bar')
        self.session, self.closed = session, False
        for owner in self.cash:
            self.cash[owner] += sum(v for due, v in self.unsettled[owner] if due <= session)
            self.unsettled[owner] = [(d, v) for d, v in self.unsettled[owner] if d > session]
        for key, p in self.positions.items():
            bar = bars[key[2]]
            p['shares'] *= bar.split
            for field in ('basis', 'entry_price', 'peak'):
                p[field] /= bar.split
            dividend = p['shares'] * bar.dividend
            p['realized'] += dividend
            self.cash[key[:2]] += dividend
        equity = {o: self.nav(o, bars, 'open') for o in self.cash}
        matured = []
        fill_start = len(self.fills)
        # Sales first, but settlement is deferred until a later session advance.
        for key, (action, target) in sorted(self.pending.items(), key=lambda x: (x[1][0] not in ('EXIT', 'REDUCE'), x[0])):
            owner = key[:2]
            price = float(bars[key[2]].open)
            p = self.positions.get(key)
            current = p['shares'] if p else 0.
            desired = target * equity[owner] / price
            if action in ('ENTER', 'ADD'):
                qty = min(max(0., desired-current), self.cash[owner]/(price*(1+self.fee)))
                if qty <= 1e-12:
                    self.rejections.append((session, key, 'insufficient settled cash or no increase'))
                    continue
                cost = qty*price*(1+self.fee)
                self.cash[owner] -= cost
                if p is None:
                    p = dict(shares=0., basis=0., entry_price=0., peak=price,
                             entry=session, initial_cost=0., realized=0.)
                    self.positions[key] = p
                p['basis'] = (p['basis']*current+cost)/(current+qty)
                p['entry_price'] = (p['entry_price']*current+qty*price)/(current+qty)
                p['shares'] += qty
                p['initial_cost'] += cost
                side = 'BUY'
            else:
                qty = current if action == 'EXIT' else max(0., current-desired)
                if qty <= 1e-12:
                    continue
                proceeds = qty*price*(1-self.fee)
                self.unsettled[owner].append((session+max(1, self.lag), proceeds))
                p['realized'] += proceeds-qty*p['basis']
                p['shares'] -= qty
                side = 'SELL'
                if p['shares'] <= 1e-10:
                    outcome = TradeOutcome(key[1], (key[0]+'_ENTRY',), p['entry'], session,
                                           p['realized']/p['initial_cost'], 'shadow')
                    matured.append(outcome)
                    self.outcomes.append(outcome)
                    del self.positions[key]
            self.fills.append((session, key, side, qty, price, qty*price*self.fee))
        for owner in self.cash:
            fees = sum(f[-1] for f in self.fills[fill_start:] if f[1][:2] == owner)
            if self.cash[owner] < -1e-8 or abs(self.nav(owner, bars, 'open') - (equity[owner]-fees)) > 1e-7:
                raise ValueError('independent shadow cash/NAV reconciliation failed')
            self.nav_history.append((session, owner, self.cash[owner],
                                     sum(v for _, v in self.unsettled[owner]), self.nav(owner, bars)))
        self.pending.clear()
        return matured

    def close_session(self, session, proposals):
        if session != self.session or self.closed:
            raise ValueError('close must follow current open exactly once')
        pending = {}
        seen = set()
        for p in proposals:
            key = (p.family, p.chromosome_id, p.ticker)
            if p.decision_date != self.sessions[session]:
                raise ValueError('shadow proposal date mismatch')
            if key[:2] not in self.cash or key in seen:
                raise ValueError('unknown owner or duplicate shadow action')
            seen.add(key)
            if p.action not in ('ENTER', 'ADD', 'HOLD', 'REDUCE', 'EXIT') or not isfinite(p.target_weight) or not 0 <= p.target_weight <= 1:
                raise ValueError('invalid shadow target/action')
            held = key in self.positions
            if (p.action == 'ENTER') == held:
                raise ValueError('shadow action inconsistent with executed holdings')
            if p.action == 'EXIT' and p.target_weight != 0:
                raise ValueError('exit target must be zero')
            if p.action in ('ENTER', 'ADD') and p.target_weight > .30:
                raise ValueError('new risk exceeds native cap')
            if p.action != 'HOLD':
                pending[key] = (p.action, p.target_weight)
        self.pending = pending
        self.closed = True

    def native_states(self, bars):
        result = {}
        for key, p in self.positions.items():
            p['peak'] = max(p['peak'], bars[key[2]].close)
            result.setdefault(key[:2], {})[key[2]] = dict(
                entry=p['entry_price'], peak=p['peak'], entry_session=p['entry'],
                shares=p['shares'], weight=p['shares']*bars[key[2]].close/self.nav(key[:2], bars),
                owner=key[:2])
        return result
