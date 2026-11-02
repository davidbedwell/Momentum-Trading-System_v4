"""Native-adjacent fixed-share research adapter, NOT authentic replay_requests.

Native source slices execute cost/cash/inventory and TradeAccount operations.
Workspace code supplies fixed quantities, owner keys, feasibility, opening state,
settlement, age/peak and output. Native float arithmetic is retained. This seam
cannot certify endogenous native policy, priority, risk sizing or native outcomes.
"""
from decimal import Decimal as D
from math import isfinite
from types import SimpleNamespace
from .ga7_native_kernels import load
from .share_order_contract import Position, Receivable, event, validate


def execute(tape):
    validate(tape)  # entire tape before loading or constructing mutable state
    # v1 permits Decimal scales beyond native binary floats. Reject unsupported
    # ranges rather than emit infinities, zero-price fills or borrowed cash.
    values = [tape.cash,tape.fee_rate]
    values += [x for p in tape.positions for x in (p.raw_entry,p.fee_basis,p.peak,p.fee_basis*p.shares)]
    values += [r.amount for r in tape.receivables]
    values += [v for b in tape.opens for _,v in b.prices]
    share_bound = sum(p.shares for p in tape.positions)+sum(o.shares for o in tape.orders)
    values += [v*share_bound for b in tape.opens for _,v in b.prices]
    try:
        supported = all(isfinite(float(x)) and (x == 0 or float(x)>0) for x in values)
    except OverflowError:
        supported = False
    if not supported:
        raise ValueError('outside native float range')
    scope, kernels = load()
    Account, NativePosition = scope['TradeAccount'], scope['Position']
    positions = {}
    for p in tape.positions:
        account = Account()
        # Imported opening book value is not historical cumulative capital/R.
        account.buy(float(p.fee_basis)*p.shares, .02)
        positions[p.owner,p.ticker] = NativePosition(p.shares,float(p.raw_entry),
            account.open_cost,-p.age,float(p.raw_entry),0,high=float(p.peak),account=account)
    env = dict(scope, positions=positions, cash=float(tape.cash), fee=float(tape.fee_rate),
               unsettled=[(tape.calendar.index(r.due),float(r.amount),r.owner) for r in tape.receivables],
               cash_flow=[])
    journal = []
    def dec(x):
        return D(str(x))
    for bar in tape.opens:
        i = tape.calendar.index(bar.session)
        prices = {t:float(p) for t,p in bar.prices}
        def record(kind, owner='', ticker='', shares=0, price=0., fee=0.):
            ps = [Position(o,t,p.shares,dec(p.entry),dec(p.cost/p.shares),
                           i-p.entered-(kind != 'MARK'),dec(p.high)) for (o,t),p in positions.items()]
            rs = [Receivable(tape.calendar[d],dec(amount),o) for d,amount,o in env['unsettled']]
            nav = env['cash'] + sum(a for _,a,_ in env['unsettled']) + sum(p.shares*prices[t] for (o,t),p in positions.items())
            journal.append(event(bar.session,kind,owner,ticker,shares,dec(price),dec(fee),dec(env['cash']),rs,ps,dec(nav)))
        for due, amount, owner in tuple(env['unsettled']):
            if due <= i:
                env['cash'] += amount
                env['unsettled'].remove((due,amount,owner))
                record('SETTLE',owner)
        for order in tape.orders:
            if order.execution != bar.session:
                continue
            key = (order.owner,order.ticker)
            old = positions.get(key)
            price = prices[order.ticker]
            qty = order.shares
            fee = qty*price*env['fee']
            if order.side == 'BUY':
                reject = qty*price*(1+env['fee']) > env['cash'] or sum(p.shares for p in positions.values())+qty > tape.max_total_shares
                action = 'ADD' if old else 'ENTER'
            else:
                reject = old is None or old.shares < qty
                action = 'EXIT' if old and old.shares == qty else 'REDUCE'
            if reject:
                record('REJECT',*key,qty,price)
                continue
            # Native kernels operate on opaque keys; tuple keys provide owner
            # isolation here. Native replay itself supports ticker keys only.
            env.update(ticker=key,pos=old,qty=qty,price=price,i=i,
                       proposal=SimpleNamespace(session=i-1),stop=.02,fill_genome=None,
                       bars={key:{'sector':'UNKNOWN'}})
            before = len(env['unsettled'])
            exec(kernels[action], env)
            # Native sales append (index, net proceeds); attach owner separately.
            if len(env['unsettled']) > before:
                due, amount = env['unsettled'][-1]
                env['unsettled'][-1] = (due,amount,order.owner)
            if action == 'REDUCE' and positions[key].shares == 0:
                raise ArithmeticError('full exit must use native EXIT kernel')
            # Fixed contract age includes completed opens. Native entered uses
            # zero at the execution index; translate only that metadata.
            if action == 'ENTER':
                positions[key].entered = i-1
            if order.side == 'BUY':
                positions[key].high = max(positions[key].high,price)
            record(order.side,*key,qty,price,fee)
        for (owner,ticker), p in positions.items():
            p.high = max(p.high,prices[ticker])
        record('MARK')
    return tuple(journal)
