"""Bounded fixed-share research contract v1; no policy or broker certification.

Tuple order is execution priority. BUY/SELL quantities are absolute, never targets.
All-or-none orders: cash, owner inventory or total-share capacity failure rejects
that order without mutation. Sells create net T+1 receivables; no same-open reuse.
Marks are the execution OPEN (never a future close). No corporate actions supported.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

D = Decimal

@dataclass(frozen=True)
class Position:
    owner: str
    ticker: str
    shares: int
    raw_entry: Decimal
    fee_basis: Decimal
    age: int
    peak: Decimal

@dataclass(frozen=True)
class Receivable:
    due: str
    amount: Decimal
    owner: str

@dataclass(frozen=True)
class Order:
    decision: str
    execution: str
    owner: str
    ticker: str
    side: str
    shares: int

@dataclass(frozen=True)
class Open:
    session: str
    prices: tuple[tuple[str, Decimal], ...]
    observed: str
    event_coverage: tuple[str, ...]
    corporate_actions: tuple = ()

@dataclass(frozen=True)
class Tape:
    version: str
    calendar: tuple[str, ...]
    cash: Decimal
    positions: tuple[Position, ...]
    receivables: tuple[Receivable, ...]
    orders: tuple[Order, ...]
    opens: tuple[Open, ...]
    fee_rate: Decimal
    settlement: str
    max_total_shares: int

@dataclass(frozen=True)
class Event:
    session: str
    kind: str
    owner: str
    ticker: str
    shares: int
    price: Decimal
    fee: Decimal
    cash: Decimal
    receivables: tuple[Receivable, ...]
    positions: tuple[Position, ...]
    nav: Decimal


def validate(t):
    """Validate the entire immutable tape before either executor creates state."""
    def require(ok, message):
        if not ok:
            raise ValueError(message)
    def number(x, positive=False):
        return type(x) is D and x.is_finite() and (x > 0 if positive else x >= 0)
    def integer(x, minimum):
        return type(x) is int and x >= minimum
    def identity(x):
        return type(x) is str and bool(x.strip()) and x == x.strip()
    require(type(t) is Tape, 'Tape required')
    require(t.version == 'fixed-shares-v1' and t.settlement == 'T+1', 'unsupported version/settlement')
    require(all(type(x) is tuple for x in (t.calendar,t.positions,t.receivables,t.orders,t.opens)), 'immutable tuples required')
    require(3 <= len(t.calendar) <= 66 and len(t.opens) <= 64 and len(t.orders) <= 4096, 'bounded tape required')
    for day in t.calendar:
        require(type(day) is str and date.fromisoformat(day).isoformat() == day, 'invalid ISO date')
    require(tuple(sorted(set(t.calendar))) == t.calendar, 'invalid calendar')
    require(number(t.cash) and number(t.fee_rate) and t.fee_rate < 1, 'invalid cash/fee')
    require(integer(t.max_total_shares,1), 'invalid capacity')
    require(bool(t.opens), 'missing opens')
    require(all(type(x) is Open for x in t.opens), 'Open records required')
    sessions = tuple(x.session for x in t.opens)
    require(sessions == t.calendar[1:1+len(sessions)] and len(sessions)+1 < len(t.calendar), 'contiguous next-open coverage and settlement tail required')
    keys = set()
    held = set()
    for p in t.positions:
        require(type(p) is Position and identity(p.owner) and identity(p.ticker), 'ambiguous ownership')
        require((p.owner,p.ticker) not in keys, 'duplicate position')
        keys.add((p.owner,p.ticker)); held.add(p.ticker)
        require(integer(p.shares,1) and integer(p.age,0) and number(p.raw_entry,True) and number(p.fee_basis,True) and p.fee_basis >= p.raw_entry and number(p.peak,True) and p.peak >= p.raw_entry, 'invalid position')
    for r in t.receivables:
        require(type(r) is Receivable and identity(r.owner) and number(r.amount,True) and r.due in t.calendar and r.due >= sessions[0], 'invalid receivable')
    require(all(type(o) is Order for o in t.orders), 'Order records required')
    require(tuple(sorted(t.orders, key=lambda o:o.execution)) == t.orders, 'orders must be chronological')
    for o in t.orders:
        require(type(o) is Order and identity(o.owner) and identity(o.ticker), 'ambiguous order owner')
        require(o.execution in sessions and o.decision == t.calendar[t.calendar.index(o.execution)-1], 'decision must precede next open')
        require(o.side in ('BUY','SELL') and integer(o.shares,1), 'unsupported operation or noninteger shares')
    # Exact conservative symbol coverage, including positions that might be sold.
    for bar in t.opens:
        require(type(bar) is Open and type(bar.prices) is tuple and type(bar.event_coverage) is tuple and type(bar.corporate_actions) is tuple, 'immutable open required')
        require(bar.observed == bar.session and not bar.corporate_actions, 'noncausal prices or unsupported corporate actions')
        needed = held | {o.ticker for o in t.orders if o.execution <= bar.session}
        require(all(type(pair) is tuple and len(pair) == 2 for pair in bar.prices), 'immutable quote pairs required')
        prices = dict(bar.prices)
        require(len(prices) == len(bar.prices) and set(prices) == needed and set(bar.event_coverage) == needed and len(bar.event_coverage) == len(needed), 'missing/partial price or event coverage')
        require(all(identity(k) and number(v,True) for k,v in bar.prices), 'invalid opening price')


def event(session, kind, owner, ticker, shares, price, fee, cash, receivables, positions, nav):
    """Output formatting only; neither engine delegates accounting to this helper."""
    ps = tuple(sorted(positions, key=lambda p:(p.owner,p.ticker)))
    rs = tuple(sorted(receivables, key=lambda r:(r.due,r.owner,r.amount)))
    return Event(session,kind,owner,ticker,shares,price,fee,cash,rs,ps,nav)
