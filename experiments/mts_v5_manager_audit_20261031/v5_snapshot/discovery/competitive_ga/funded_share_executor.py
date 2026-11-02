"""Independent funded-shadow fixed-share bridge with one explicit funded bank.

Owners attribute inventory; they do not imply additional segregated bankrolls.
This opt-in executor does not change the legacy fractional FundedShadow policy.
"""
from decimal import Decimal
from .share_order_contract import Position, Receivable, event, validate


def execute(request):
    validate(request)
    balance = request.cash
    # Mutable row representation deliberately independent of reference holdings.
    rows = [[p.owner,p.ticker,p.shares,p.raw_entry,p.fee_basis,p.age,p.peak] for p in request.positions]
    credits = [(r.due,r.amount,r.owner) for r in request.receivables]
    output = []
    for opening in request.opens:
        quotes = dict(opening.prices)
        def emit(action, owner='', symbol='', quantity=0, cost=Decimal(0), commission=Decimal(0)):
            marked = balance
            for credit in credits:
                marked += credit[1]
            for row in rows:
                marked += quotes[row[1]]*row[2]
            output.append(event(opening.session,action,owner,symbol,quantity,cost,commission,balance,
                                [Receivable(*r) for r in credits],[Position(*r) for r in rows],marked))
        matured = [r for r in credits if r[0] <= opening.session]
        for credit in matured:
            balance = balance + credit[1]
            credits.remove(credit)
            emit('SETTLE',credit[2])
        todays = [o for o in request.orders if o.execution == opening.session]
        for instruction in todays:
            row = next((r for r in rows if r[:2] == [instruction.owner,instruction.ticker]),None)
            n = instruction.shares
            quote = quotes[instruction.ticker]
            commission = (n*quote)*request.fee_rate
            rejected = False
            if instruction.side == 'SELL':
                if row is None or n > row[2]:
                    rejected = True
                else:
                    row[2] -= n
                    if row[2] == 0:
                        rows.remove(row)
                    next_day = request.calendar[request.calendar.index(opening.session)+1]
                    credits += [(next_day,n*quote-commission,instruction.owner)]
            else:
                debit = n*quote+commission
                room = request.max_total_shares-sum(r[2] for r in rows)
                if balance < debit or room < n:
                    rejected = True
                else:
                    balance = balance-debit
                    if row is None:
                        rows.append([instruction.owner,instruction.ticker,n,quote,debit/n,0,quote])
                    else:
                        total = row[2]+n
                        row[3] = (row[3]*row[2]+n*quote)/total
                        row[4] = (row[4]*row[2]+debit)/total
                        row[2] = total
                        row[6] = max(row[6],quote)
            emit('REJECT' if rejected else instruction.side,instruction.owner,instruction.ticker,n,quote,
                 Decimal(0) if rejected else commission)
        for row in rows:
            row[5] += 1
            row[6] = max(row[6],quotes[row[1]])
        emit('MARK')
    return tuple(output)
