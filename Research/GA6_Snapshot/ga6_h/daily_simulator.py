"""Chronological daily GA6-H simulation; close-t signals, next-open orders."""
from collections import defaultdict
from datetime import datetime, timezone
from math import isfinite
import pandas as pd
from portfolio_execution import Portfolio, Order, quantity_for_weight, entry_permitted


def simulate(bars, ranks, schedules, verified_tickers, initial_cash=100000, hold_sessions=20, weight=.03, max_positions=30, cost_bps=10, price_adjustment_type=None, discovery_end_date=None, entry_threshold=float("-inf"), stop_loss=None, trailing_stop=None, replace_threshold=None):
    """bars: date,symbol,Open,Close,tradable_bar. ranks: date,symbol,score.
    Missing verified historical earnings schedule prevents buys; sells unaffected.
    No dividends/split accounting yet; diagnostic only on adjusted-for-splits data.
    """
    if price_adjustment_type not in ('unadjusted_with_actions', 'backward_adjusted_verified'):
        raise ValueError('explicit verified price accounting mode required')
    if price_adjustment_type == 'unadjusted_with_actions':
        if not {'Stock Splits','Dividends'}.issubset(bars.columns):
            raise ValueError('unadjusted execution requires split/dividend columns')
        if bars[['Stock Splits','Dividends']].isna().any().any():
            raise ValueError('missing corporate actions')
    for threshold in (stop_loss,trailing_stop):
        if threshold is not None and (not isfinite(threshold) or not 0 < threshold <= 1):
            raise ValueError('invalid stop threshold')
    if replace_threshold is not None and (not isfinite(replace_threshold) or replace_threshold<0):
        raise ValueError('invalid replacement threshold')
    if not 1 <= hold_sessions <= 40: raise ValueError('holding period must be 1-40 sessions')
    if not 0 < weight <= .10: raise ValueError('invalid position weight')
    if not isfinite(entry_threshold) and entry_threshold != float('-inf'):
        raise ValueError('invalid entry threshold')
    bars=bars.copy(); ranks=ranks.copy()
    bars['date']=pd.to_datetime(bars.date).dt.normalize()
    ranks['date']=pd.to_datetime(ranks.date).dt.normalize()
    if discovery_end_date is not None:
        limit=pd.Timestamp(discovery_end_date).normalize()
        if bars.date.max()>limit or ranks.date.max()>limit:
            raise ValueError('evaluation crosses discovery boundary')
    dates=sorted(bars.date.unique())
    sessions=[pd.Timestamp(x).date() for x in dates]
    perday={d:g.set_index('symbol') for d,g in bars.groupby('date')}
    signals={d:g.sort_values(['score','symbol'],ascending=[False,True]) for d,g in ranks.groupby('date')}
    p=Portfolio(float(initial_cash),{},{}); marks={}; pending=[]; history=[]; trades=[]; entry_prices={}; high_marks={}
    for i,dt in enumerate(dates):
        day=perday[dt]
        # Apply split ratios effective at today's open, before order execution.
        if price_adjustment_type == 'unadjusted_with_actions':
            for symbol,qty in list(p.shares.items()):
                if symbol not in day.index:raise ValueError('missing held-security corporate-action row')
                ratio=float(day.loc[symbol,'Stock Splits'])
                if not isfinite(ratio) or ratio<0:raise ValueError('invalid split ratio')
                if ratio>0:
                    new_qty=qty*ratio
                    if abs(new_qty-round(new_qty))>1e-8:raise ValueError('fractional split requires cash-in-lieu ledger')
                    p.shares[symbol]=round(new_qty)
                    entry_prices[symbol]/=ratio
                    high_marks[symbol]/=ratio
                    if symbol in marks:marks[symbol]/=ratio
        if price_adjustment_type == 'unadjusted_with_actions':
            for symbol,qty in p.shares.items():
                if symbol not in day.index:raise ValueError('missing held-security dividend row')
                dividend=float(day.loc[symbol,'Dividends'])
                if not isfinite(dividend) or dividend<0:raise ValueError('invalid dividend')
                p.cash+=qty*dividend
        # Execute prior close's orders at today's open. Sells precede buys.
        deferred_sells=[]
        for order in sorted(pending,key=lambda x:0 if x[0]=='sell' else 1):
            side,symbol,signal_i=order
            if symbol not in day.index:
                if side=='sell': deferred_sells.append(order)
                continue
            bar=day.loc[symbol]; op=float(bar.Open)
            if not bool(bar.tradable_bar) or not isfinite(op) or op<=0:
                if side=='sell': deferred_sells.append(order)
                continue
            if side=='sell':
                q=p.shares.get(symbol,0)
                if q and p.fill(Order(symbol,q,'sell'),op,cost_bps):
                    trades.append((str(dt.date()),symbol,'sell',q,op));entry_prices.pop(symbol,None);high_marks.pop(symbol,None)
            else:
                # Decision timestamp is previous day's close; no future schedule publication.
                signal_dt=pd.Timestamp(dates[signal_i])
                decision_at=signal_dt.tz_localize('America/New_York').replace(hour=16).tz_convert('UTC').isoformat()
                if not entry_permitted(symbol,dt.date(),schedules,sessions,decision_at,verified_tickers):continue
                if symbol in p.shares or len(p.shares)>=max_positions:continue
                equity=p.equity(marks)
                q=quantity_for_weight(p.cash,equity,op,weight,cost_bps)
                if q and p.fill(Order(symbol,q,'buy'),op,cost_bps):
                    p.entry_session[symbol]=i;entry_prices[symbol]=op;high_marks[symbol]=op
                    trades.append((str(dt.date()),symbol,'buy',q,op))
        for symbol,row in day.iterrows():
            close=float(row.Close)
            if isfinite(close) and close>0: marks[symbol]=close
        pending=deferred_sells
        history.append((str(dt.date()),p.equity(marks),p.cash,len(p.shares)))
        if i==len(dates)-1:break
        # Signals evaluated at close t; stops execute at the next tradable open.
        queued_exits={symbol for side,symbol,_ in pending if side=='sell'}
        # No intraday stop-price fill is assumed.
        for symbol,entered in p.entry_session.items():
            close=marks.get(symbol)
            if close is not None and isfinite(close) and close>0:
                high_marks[symbol]=max(high_marks[symbol],close)
            age=i+1-entered
            stop_hit=(stop_loss is not None and close is not None and close<=entry_prices[symbol]*(1-stop_loss))
            trail_hit=(trailing_stop is not None and close is not None and close<=high_marks[symbol]*(1-trailing_stop))
            if (age>=hold_sessions or stop_hit or trail_hit) and symbol not in queued_exits:
                pending.append(('sell',symbol,i))
        exiting={s for side,s,_ in pending if side=='sell'}
        candidates=signals.get(dt)
        # Optional relative-score replacement: sell the lowest-ranked incumbent
        # only when a new candidate exceeds it by the chromosome's margin.
        # Both orders execute at the following open, sells first.
        if replace_threshold is not None and candidates is not None and p.shares:
            ranked={str(row.symbol):float(row.score) for row in candidates.itertuples(index=False) if isfinite(float(row.score))}
            eligible_new=[(symbol,score) for symbol,score in ranked.items()
                          if symbol not in p.shares and score>=entry_threshold]
            held=[(symbol,ranked.get(symbol,float('-inf'))) for symbol in p.shares if symbol not in exiting]
            if eligible_new and held:
                best_new=max(eligible_new,key=lambda x:(x[1],x[0]))
                worst_held=min(held,key=lambda x:(x[1],x[0]))
                if best_new[1]>worst_held[1]+replace_threshold:
                    pending.append(('sell',worst_held[0],i))
                    exiting.add(worst_held[0])
        if candidates is not None:
            for row in candidates.itertuples(index=False):
                planned_sells=sum(side=='sell' for side,_,_ in pending)
                if len(p.shares)-planned_sells+sum(side=='buy' for side,_,_ in pending)>=max_positions:break
                if row.symbol in p.shares or row.symbol in exiting:continue
                if not isfinite(float(row.score)) or float(row.score)<entry_threshold:continue
                pending.append(('buy',row.symbol,i))
    return pd.DataFrame(history,columns=['date','equity','cash','positions']),pd.DataFrame(trades,columns=['date','symbol','side','quantity','open_price'])
