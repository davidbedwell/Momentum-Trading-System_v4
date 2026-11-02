"""Read-only ordered observations of the ORIGINAL hash-locked native replay.

No frame-local writes, fill reconstruction engine, policy overrides or code
patching. Inventory deltas at proposal boundaries expose actual fills. A trace
is process-global: refuse existing hooks and restore on every exit.
"""
import inspect
import sys
from pathlib import Path
from .ga7_native_kernels import ROOT, sources


def observe(fn, genome, panels, passes):
    source = sources()['request_replay.py']
    if Path(inspect.getfile(fn)).resolve() != ROOT/'request_replay.py' or fn.__name__ != 'replay_requests' or sys.gettrace() is not None:
        raise ValueError('unsupported original native journal contract')
    lines = source.splitlines()
    def anchor(text):
        found = [i+1 for i,line in enumerate(lines) if line.strip() == text]
        if len(found) != 1:
            raise ValueError('unsupported native journal anchor: '+text)
        return found[0]
    begin = anchor('ticker = proposal.ticker')
    end = next(i+1 for i,line in enumerate(lines) if line == '            for ticker, pos in list(positions.items()):')
    mark = anchor('nav.append(cash + sum(amount for _, amount in unsettled) + sum(p.shares * bars[t]["close"] for t,p in positions.items()))')
    sizing = {i+1 for i,line in enumerate(lines) if line.strip() == 'qty = int(budget / (price * (1+fee)))'}
    orders = []; daily = []; active = None
    def state(v):
        return dict(cash=v['cash'],receivables=[list(x) for x in v['unsettled']],
                    positions={t:dict(shares=p.shares,entry=p.entry,cost=p.cost,
                                      invested=p.account.invested,open_cost=p.account.open_cost,
                                      realized=p.account.realized) for t,p in v['positions'].items()})
    def finish(v):
        nonlocal active
        if active is None:
            return
        after = state(v); t = active['ticker']
        old = active['before']['positions'].get(t,{}).get('shares',0)
        new = after['positions'].get(t,{}).get('shares',0)
        delta = new-old
        price = v['bars'][t]['open'] if t in v['bars'] else None
        active.update(after=after,filled_shares=abs(delta),
                      side='BUY' if delta>0 else 'SELL' if delta<0 else None,
                      price=price,fee=abs(delta)*price*v['fee'] if delta else 0.,
                      outcome='FILL' if delta else 'NO_FILL')
        orders.append(active); active = None
    def trace(frame,event,arg):
        nonlocal active
        if frame.f_code is not fn.__code__:
            return None
        if event == 'line':
            v = frame.f_locals; line = frame.f_lineno
            if line == begin:
                finish(v)
                p=v['proposal']
                active=dict(session=v['i'],date=v['day'],ticker=p.ticker,action=p.action,
                            request=dict(vars(p)),before=state(v),sizing=None)
            elif line == end:
                finish(v)
            elif line in sizing and active is not None:
                active['sizing'] = dict(budget=v['budget'],equity=v['equity'],
                                        price=v['price'],fee=v['fee'])
            elif line == mark:
                daily.append(dict(session=v['i'],date=v['day'],state=state(v),
                                  marked_nav=v['cash']+sum(a for _,a in v['unsettled'])+
                                  sum(p.shares*v['bars'][t]['close'] for t,p in v['positions'].items())))
        return trace
    sys.settrace(trace)
    try:
        result,ledger=fn(genome,panels,passes,cash_yield=0.,record_pass=True)
    finally:
        sys.settrace(None)
    if active is not None or len(daily) != len(panels):
        raise ValueError('incomplete native journal')
    return result,ledger,orders,daily
