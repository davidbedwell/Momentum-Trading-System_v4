"""Causal, fee-aware fixed-horizon shadow trade reconstruction.
Research baseline for GA6 entry signals, NOT authentic GA6 exit outcomes.
Uses next-session open for both entry and horizon exit. Each signal is a
separate hypothetical shadow trade; never asserts simultaneous funding.
"""
from collections import defaultdict
from math import isfinite
from .causal_calibration import TradeOutcome


def reconstruct(signal_rows,price_rows,*,horizon=10,fee=0.001):
    if not isinstance(horizon,int) or horizon<1 or not 0<=fee<1:
        raise ValueError('invalid shadow horizon or fee')
    by_ticker=defaultdict(list)
    for r in price_rows:
        date,ticker,opening=r
        if not isfinite(opening) or opening<=0:raise ValueError('invalid price')
        by_ticker[ticker].append((date,float(opening)))
    global_dates=sorted({date for rows in by_ticker.values() for date,_ in rows})
    global_session={date:i for i,date in enumerate(global_dates)}
    indices={}
    for ticker,rows in by_ticker.items():
        rows.sort()
        dates=[x[0] for x in rows]
        if len(set(dates))!=len(dates):raise ValueError('duplicate ticker session')
        indices[ticker]={date:i for i,date in enumerate(dates)}
    outcomes=[];unmatured=0;missing=0
    for date,ticker,chromosome in signal_rows:
        rows=by_ticker.get(ticker)
        index=indices.get(ticker,{}).get(date)
        if rows is None or index is None:
            missing+=1;continue
        entry=index+1
        exit_index=entry+horizon
        if exit_index>=len(rows):
            unmatured+=1;continue
        buy_date,buy=rows[entry]
        sell_date,sell=rows[exit_index]
        if not date<buy_date<sell_date:raise ValueError('noncausal shadow trade')
        # Decision and maturity indices use the shared global market calendar.
        outcome=TradeOutcome(chromosome,('GA6_ENTRY',),global_session[date],global_session[sell_date],
                             (sell*(1-fee))/(buy*(1+fee))-1.,'shadow')
        outcomes.append((date,buy_date,sell_date,ticker,outcome))
    return {'outcomes':outcomes,'unmatured':unmatured,'missing':missing,
            'horizon':horizon,'fee':fee,'limitations':'fixed-horizon hypothetical shadow outcomes, not native GA6 exits; global market session indices'}
