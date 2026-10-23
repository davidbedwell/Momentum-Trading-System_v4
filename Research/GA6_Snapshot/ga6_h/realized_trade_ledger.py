"""FIFO long-only realized PnL from execution fills and ex-date corporate actions.
Reject unmatched fills, fractional splits, and open positions for completed-trade EV.
"""
from collections import defaultdict
from math import isfinite

def realized_trades(fills, actions=(), cost_bps=10):
    if not 0 <= cost_bps < 10000:raise ValueError('invalid costs')
    events=[]
    for n,f in enumerate(fills):
        date,symbol,side,quantity,price=f
        events.append((str(date),1,n,'fill',(symbol,side,quantity,price)))
    for n,a in enumerate(actions):
        date,symbol,kind,value=a
        events.append((str(date),0,n,'action',(symbol,kind,value)))
    lots=defaultdict(list);completed=[]
    for date,_,__,typ,data in sorted(events):
        if typ=='action':
            sym,kind,value=data
            if not isfinite(float(value)):raise ValueError('invalid action')
            if kind=='split':
                if value<=0:raise ValueError('invalid split')
                for lot in lots[sym]:
                    if abs(lot[0]*value-round(lot[0]*value))>1e-8:raise ValueError('fractional split')
                    lot[0]=round(lot[0]*value)
            elif kind=='dividend':
                if value<0:raise ValueError('negative dividend')
                for lot in lots[sym]:lot[2]+=lot[0]*value
            else:raise ValueError('unknown corporate action')
            continue
        sym,side,qty,price=data
        if not isinstance(qty,int) or qty<=0 or not isfinite(float(price)) or price<=0:raise ValueError('invalid fill')
        if side=='buy':lots[sym].append([qty,qty*price*(1+cost_bps/10000),0.0,date]);continue
        if side!='sell':raise ValueError('invalid side')
        remaining=qty
        while remaining:
            if not lots[sym]:raise ValueError('sell without open lot')
            lot=lots[sym][0];n=min(remaining,lot[0]);fraction=n/lot[0]
            basis=lot[1]*fraction;div=lot[2]*fraction
            proceeds=n*price*(1-cost_bps/10000)
            completed.append({'symbol':sym,'entry_date':lot[3],'exit_date':date,'quantity':n,'net_pnl':proceeds-basis+div,'net_return':(proceeds+div)/basis-1})
            lot[0]-=n;lot[1]-=basis;lot[2]-=div;remaining-=n
            if not lot[0]:lots[sym].pop(0)
    return completed,{sym:sum(lot[0] for lot in entries) for sym,entries in lots.items() if entries}
