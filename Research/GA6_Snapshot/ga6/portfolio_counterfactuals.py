"""Chronological portfolio opportunity accounting; not a certification replay."""
from math import isfinite

def compare(opportunities,capital=100000.,fee=.001,max_positions=10):
    if capital<=0 or fee<0 or max_positions<1:raise ValueError('invalid capital constraints')
    ordered=sorted(opportunities,key=lambda x:(x['decision_date'],0 if x['action']=='EXIT' else 1 if x['action']=='HOLD' else 2,-float(x.get('priority',0)),x['ticker']))
    active={};cash=capital;events=[];rejected=[]
    for o in ordered:
        day=o['decision_date'];ticker=o['ticker'];action=o['action'];price=float(o['next_open'])
        if not isfinite(price) or price<=0:raise ValueError('invalid next-open price')
        if action=='EXIT' and ticker in active:
            qty=active.pop(ticker);cash+=qty*price*(1-fee)
            events.append((day,ticker,'EXIT',qty,price))
        elif action=='ENTER':
            if ticker in active:continue
            if len(active)>=max_positions:rejected.append((day,ticker,'capacity'));continue
            if not o.get('membership',False) or not o.get('earnings_allowed',False) or not o.get('risk_allowed',False):rejected.append((day,ticker,'eligibility'));continue
            target=(cash+sum(q*float(o.get('mark_prices',{}).get(t,price)) for t,q in active.items()))*min(1.,max(0.,float(o.get('weight',.03))))
            qty=int(min(cash,target)/(price*(1+fee)))
            if qty<1:rejected.append((day,ticker,'cash'));continue
            cash-=qty*price*(1+fee);active[ticker]=qty
            events.append((day,ticker,'ENTER',qty,price))
        elif action not in ('ENTER','EXIT','HOLD'):raise ValueError('unknown action')
    return {'cash':cash,'positions':active,'events':events,'rejected':rejected,'executed_entries':sum(x[2]=='ENTER' for x in events),'executed_exits':sum(x[2]=='EXIT' for x in events)}
