"""Chronological next-open GA6 trade-path counterfactuals.
Candidate decisions use only observed closes; fills use following session opens.
The oracle reentry is a diagnostic upper bound, NEVER a deployable policy.
"""
from collections import defaultdict
from ga6.counterfactuals import compare_path,classify

def price_index(prepared):
 by=defaultdict(list)
 for ds,rows,opens,closes in prepared.sessions:
  for ticker,op in opens.items():
   if ticker in closes and op>0 and closes[ticker]>0:
    by[ticker].append((str(ds)[:10],float(op),float(closes[ticker])))
 return dict(by)

def replay(trades,prices,fee=.001,cash_daily=0.,drawdown_trigger=.05,reentry_horizon=10):
 results=[];skipped=0
 for tr in trades:
  path=prices.get(tr['ticker'],[])
  start=str(tr['entry_date'])[:10];end=str(tr['exit_date'])[:10]
  interval=[(i,d,o,c) for i,(d,o,c) in enumerate(path) if start<=d<=end]
  if len(interval)<4:skipped+=1;continue
  peak=interval[0][3]
  for k in range(1,len(interval)-2):
   _,date,op,close=interval[k]
   peak=max(peak,close)
   if close>peak*(1-drawdown_trigger):continue
   # Signal after close k; next-open exit k+1; reentry candidate later.
   exit_i=k+1
   last_i=min(len(interval)-1,exit_i+reentry_horizon)
   if exit_i>=last_i:continue
   entry_open=interval[0][2];exit_open=interval[exit_i][2];final_open=interval[-1][2]
   for j in range(exit_i+1,last_i+1):
    x=compare_path(entry_open,exit_open,interval[j][2],final_open,exit_i,j,fee,cash_daily)
    x.update({'ticker':tr['ticker'],'entry_date':start,'decision_date':date,'exit_fill_date':interval[exit_i][1],'reentry_fill_date':interval[j][1],'trade_end':end,'drawdown_trigger':drawdown_trigger,'oracle_only':True})
    results.append(x)
   break # one initial drawdown event per trade, no hindsight choice of signal
 return {'candidate_count':len(results),'skipped_trades':skipped,'classes':classify(results),'oracle_only':True,'mean_incremental_net':sum(x['incremental_net'] for x in results)/len(results) if results else None}
