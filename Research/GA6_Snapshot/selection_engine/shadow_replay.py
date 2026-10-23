"""Independent single-symbol chromosome shadow fills, research-only.
Every candidate has its own position and capital. No shared portfolio, defense,
earnings or membership policy yet: do NOT treat results as certified GA6 replay.
"""
from dataclasses import dataclass
from math import isfinite
from ga5_chromosome_decisions import PositionState
from niche_signal_adapter import evaluate_all

@dataclass
class ShadowPosition:
 shares:int=0
 entry_price:float=0.
 peak_price:float=0.
 entry_index:int=-1
 entry_date:str=''
 entry_decision_id:str=''
 cash:float=100000.
 realized:float=0.

def replay_symbol(rows,candidates,niche_by_date,*,fee=.001,max_sessions=40,starting_cash=100000):
 """rows sorted date, with open/close/adj_close, all features; returns completed trades.
 Decisions at close execute at next open. Conservative no same-open reversal.
 All trade returns are entry-notional based after buy and sell commissions.
 """
 if not 1<=max_sessions<=40:raise ValueError('invalid hold cap')
 if not 0<=fee<1:raise ValueError('invalid fee')
 states={i:ShadowPosition(cash=starting_cash) for i in range(len(candidates))}
 pending={};trades=[];decisions=[]
 for day_index,row in enumerate(rows):
  ds=str(row['date'])[:10];symbol=row['ticker']
  open_price=float(row['open']);close=float(row['adj_close'])
  if not(isfinite(open_price) and isfinite(close) and open_price>0 and close>0):raise ValueError('bad price')
  # GA6 datasets carry split-adjusted open in adj_open if available.
  if 'adj_open' in row and row['adj_open'] is not None:
   open_price=float(row['adj_open'])
  else:
   open_price*=close/float(row['close'])
  if not isfinite(open_price) or open_price<=0:raise ValueError('invalid adjusted open')
  # Orders queued at prior close fill at current open.
  for i,(action,weight,decision_id) in sorted(pending.items()):
   st=states[i]
   if action in ('EXIT','REPLACE_CANDIDATE') and st.shares:
    proceeds=st.shares*open_price*(1-fee)
    cost=st.shares*st.entry_price*(1+fee)
    pnl=proceeds-cost
    st.cash+=proceeds;st.realized+=pnl
    held=day_index-st.entry_index
    if held>max_sessions:raise RuntimeError('holding cap violated')
    trades.append(dict(chromosome=i,symbol=symbol,entry_date=st.entry_date,exit_date=ds,entry_decision_id=st.entry_decision_id,exit_decision_id=decision_id,entry_price=st.entry_price,exit_price=open_price,shares=st.shares,holding_sessions=held,net_return=pnl/cost,realized_pnl=pnl,exit_reason=action))
    st.shares=0;st.entry_index=-1;st.entry_decision_id=''
   elif action=='ENTER' and not st.shares:
    target=min(float(weight),float(candidates[i].genome.max_weight),.10)
    qty=int(min(st.cash/(open_price*(1+fee)),starting_cash*target/(open_price*(1+fee))))
    if qty>0:
     st.cash-=qty*open_price*(1+fee)
     st.shares=qty;st.entry_price=open_price;st.peak_price=open_price
     st.entry_index=day_index;st.entry_date=ds;st.entry_decision_id=decision_id
  pending={}
  # Hard holding cap: exit on first available open at session 40.
  # In the current prototype this triggers at today's open only if the prior
  # session scheduled an exit. If an open-date cap is reached unexpectedly,
  # fail rather than silently violate the contract.
  for i,st in states.items():
   if st.shares and day_index-st.entry_index>=max_sessions:
    proceeds=st.shares*open_price*(1-fee);cost=st.shares*st.entry_price*(1+fee)
    pnl=proceeds-cost;st.cash+=proceeds;st.realized+=pnl
    trades.append(dict(chromosome=i,symbol=symbol,entry_date=st.entry_date,exit_date=ds,entry_decision_id=st.entry_decision_id,exit_decision_id='',entry_price=st.entry_price,exit_price=open_price,shares=st.shares,holding_sessions=day_index-st.entry_index,net_return=pnl/cost,realized_pnl=pnl,exit_reason='MAX_40_OPEN'))
    st.shares=0;st.entry_index=-1;st.entry_decision_id=''
  label=niche_by_date.get(ds)
  if label is None:continue
  for i,st in states.items():
   if st.shares:st.peak_price=max(st.peak_price,close)
  positions={i:PositionState(st.shares,st.entry_price,st.peak_price,day_index-st.entry_index) for i,st in states.items() if st.shares}
  result=evaluate_all(asof=ds,symbol=symbol,market_features=row,recognized_niches={label},niche_evidence_cutoff=ds,candidates=candidates,position_by_chromosome=positions,close_price=close)
  for d in result['decisions']:
   i=d['chromosome'];action=d['action'];st=states[i]
   did=f'{symbol}|{ds}|{i}'
   decisions.append(dict(decision_id=did,asof=ds,symbol=symbol,chromosome=i,niche=d['niche'],action=action,features=d['features'],weight=d['raw_weight']))
   if st.shares:
    if action in ('EXIT','REPLACE_CANDIDATE'):pending[i]=(action,0.,did)
    elif day_index-st.entry_index>=max_sessions-1:pending[i]=('EXIT',0.,did)
   elif action=='ENTER':pending[i]=('ENTER',d['raw_weight'],did)
 return dict(decisions=decisions,trades=trades,open_positions=sum(s.shares>0 for s in states.values()),status='RESEARCH_ONLY_SHADOW_NO_GA6_POLICY')
