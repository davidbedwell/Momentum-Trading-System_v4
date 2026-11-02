"""Independent native-style integer reference, NOT native endogenous replay."""
from dataclasses import replace
from decimal import Decimal as D
from .share_order_contract import Position, Receivable, event, validate


def execute(tape):
    validate(tape)
    cash = tape.cash
    holdings = {(p.owner,p.ticker):p for p in tape.positions}
    pending = list(tape.receivables)
    journal = []
    for bar in tape.opens:
        prices = dict(bar.prices)
        def record(kind, owner='', ticker='', shares=0, price=D(0), fee=D(0)):
            nav = cash + sum((r.amount for r in pending),D(0)) + sum((p.shares*prices[p.ticker] for p in holdings.values()),D(0))
            journal.append(event(bar.session,kind,owner,ticker,shares,price,fee,cash,pending,holdings.values(),nav))
        for r in tuple(pending):
            if r.due <= bar.session:
                cash += r.amount
                pending.remove(r)
                record('SETTLE',r.owner)
        for order in tape.orders:
            if order.execution != bar.session:
                continue
            key = (order.owner,order.ticker)
            old = holdings.get(key)
            price = prices[order.ticker]
            gross = order.shares*price
            fee = gross*tape.fee_rate
            if order.side == 'BUY':
                if gross+fee > cash or sum(p.shares for p in holdings.values())+order.shares > tape.max_total_shares:
                    record('REJECT',order.owner,order.ticker,order.shares,price)
                    continue
                cash -= gross+fee
                count = (old.shares if old else 0)+order.shares
                raw = ((old.raw_entry*old.shares if old else D(0))+gross)/count
                basis = ((old.fee_basis*old.shares if old else D(0))+gross+fee)/count
                holdings[key] = Position(*key,count,raw,basis,old.age if old else 0,max(old.peak if old else price,price))
            else:
                if old is None or old.shares < order.shares:
                    record('REJECT',order.owner,order.ticker,order.shares,price)
                    continue
                remaining = old.shares-order.shares
                if remaining:
                    holdings[key] = replace(old,shares=remaining)
                else:
                    del holdings[key]
                due = tape.calendar[tape.calendar.index(bar.session)+1]
                pending.append(Receivable(due,gross-fee,order.owner))
            record(order.side,order.owner,order.ticker,order.shares,price,fee)
        holdings = {k:replace(p,age=p.age+1,peak=max(p.peak,prices[p.ticker])) for k,p in holdings.items()}
        record('MARK')
    return tuple(journal)
