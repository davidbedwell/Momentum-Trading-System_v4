"""GA5 guarded chronological research evaluator. NOT certified without verified PIT inputs."""
import pandas as pd
from ga5_feature_adapter import extract
from ga5_chromosome_decisions import signal,PositionState
from ga5_earnings_entry_embargo import entry_allowed
from mts_next_open_ledger_v1 import Order
from settlement_ledger import SettledLedger
from fast_decision import evaluate as fast_signal
from math import isfinite
from ga5_feature_adapter import LEGACY
from shadow_signals import ShadowBook
from exit_objectives import metrics as exit_metrics,calmar

class PreparedSessions:
 """Immutable per-session rows built once per worker, reused across genomes."""
 def __init__(self,frame):
  if not {"dividends","stock_splits"}.issubset(frame.columns):raise ValueError("Corporate action columns required")
  if frame.duplicated(["date","ticker"]).any():raise ValueError("Duplicate price bars")
  d=frame.sort_values(["date","ticker"])
  self.sessions=[]
  self.membership_keys=set()
  self.dates=set()
  for day,part in d.groupby("date",sort=True):
   ds=str(day)[:10]
   rows={r.ticker:r._asdict() for r in part.itertuples(index=False)}
   opens={t:float(r["open"]) for t,r in rows.items()}
   closes={t:float(r["close"]) for t,r in rows.items()}
   self.sessions.append((ds,rows,opens,closes))
   self.dates.add(ds)
   self.membership_keys.update((ds,t) for t in rows)

def evaluate(frame,genome,*,blocked,membership,risk_veto,starting_cash=100000,fee=.001,max_positions=None,annual_cash_yield=None,niche_labels=None):
 if not genome.valid():raise ValueError("Invalid genome")
 if max_positions is None:max_positions=79
 if not 1<=max_positions<=79:raise ValueError("Invalid portfolio capacity")
 if annual_cash_yield is None:raise ValueError("Explicit cash proxy yield required")
 if any(x is None for x in (blocked,membership,risk_veto)):raise ValueError("Required PIT policies missing")
 if not isinstance(blocked,dict) or not isinstance(membership,dict) or not isinstance(risk_veto,dict):raise TypeError("PIT policies must be mappings")
 prepared=frame if isinstance(frame,PreparedSessions) else PreparedSessions(frame)
 if niche_labels is not None and not prepared.membership_keys.issubset(niche_labels):raise ValueError("Incomplete niche label coverage")
 ledger=SettledLedger(starting_cash,fee,price_basis="split_adjusted")
 shadow=ShadowBook(genome,fee)
 trace={"feature_valid":0,"feature_missing":0,"signal_enter":0,"niche_match":0,"niche_reject":0,"scheduled_entries":0,"executed_buys":0,"executed_sells":0}
 pending=None;positions={};nav=[];last={};scale_fills={"in":0,"out":0};rejected={"earnings":0,"membership":0,"veto":0,"unsettled":0,"no_cash":0,"lot_too_expensive":0,"below_minimum_allocation":0,"capacity":0}
 fields=(genome.entry_feature,genome.hold_feature,genome.exit_feature,genome.regime_feature,genome.sizing_feature,genome.replace_feature)
 if not prepared.dates.issubset(risk_veto):raise ValueError("Missing independent risk decisions")
 if not prepared.membership_keys.issubset(membership):raise ValueError("Incomplete PIT membership snapshot")
 for i,(ds,rows,opens,closes) in enumerate(prepared.sessions):
  ledger.start_session(ds,i,annual_cash_yield)
  shadow.start(ds,opens,blocked,membership,risk_veto,{t:{"dividends":r.get("dividends",0),"stock_splits":r.get("stock_splits",0)} for t,r in rows.items()})
  for t,r in rows.items():
   if r.get("dividends",0) or r.get("stock_splits",0):
    ledger.apply_ex_date(ds,t,float(r.get("stock_splits",0)),float(r.get("dividends",0)))
  if pending:
   decision,exits,entries,adjustments=pending
   # A previously scheduled entry cannot bypass a defensive transition.
   # Defensive state liquidates existing holdings at the next available open.
   if risk_veto[ds] is not True:
    exits=list(dict.fromkeys(list(exits)+[t for t,q in ledger.holdings.items() if q>0]))
    entries=[];adjustments=[]
   for t in exits:
    qty=ledger.holdings.get(t,0)
    if qty and t in opens:
     ledger.execute_open(Order(decision,t,"SELL",qty),ds,opens[t])
     positions.pop(t,None)
   # Process reductions before increases; no same-day reversal or unverified entry.
   for t,action,amount in sorted(adjustments,key=lambda x:0 if x[1]=='SCALE_OUT' else 1):
    held=ledger.holdings.get(t,0)
    if not held or t not in opens or t in exits:continue
    if action=='SCALE_OUT':
     qty=min(held,max(1,int(held*amount)))
     ledger.execute_open(Order(decision,t,'SELL',qty),ds,opens[t])
     scale_fills['out']+=1
     if qty==held:positions.pop(t,None)
     else:
      prev=positions[t];positions[t]=PositionState(held-qty,prev.entry_price,prev.peak_price,prev.sessions_held)
    elif action=='SCALE_IN':
     if not membership.get((ds,t),False) or not entry_allowed(t,ds,blocked) or risk_veto.get(decision) is not True or risk_veto.get(ds) is not True:continue
     equity=ledger.cash+sum(q*opens.get(k,last.get(k,0)) for k,q in ledger.holdings.items())
     headroom=max(0.,equity*genome.max_weight-held*opens[t])
     qty=min(int(equity*amount/(opens[t]*(1+fee))),int(headroom/(opens[t]*(1+fee))),int(ledger.available_cash()/(opens[t]*(1+fee))))
     if qty>0:
      ledger.execute_open(Order(decision,t,'BUY',qty),ds,opens[t])
      prev=positions[t];positions[t]=PositionState(held+qty,(prev.entry_price*held+opens[t]*qty)/(held+qty),max(prev.peak_price,opens[t]),prev.sessions_held)
      scale_fills['in']+=1
   for t,weight in entries:
    if t not in opens or ledger.holdings.get(t,0)>0:continue
    if not membership.get((ds,t),False):rejected["membership"]+=1;continue
    if not entry_allowed(t,ds,blocked):rejected["earnings"]+=1;continue
    if risk_veto.get(decision) is not True or risk_veto.get(ds) is not True:
     rejected["veto"]+=1;continue
    if sum(q>0 for q in ledger.holdings.values())>=max_positions:
     rejected["capacity"]+=1
     break
    price=opens[t]
    equity=ledger.cash+sum(q*opens.get(k,last.get(k,0)) for k,q in ledger.holdings.items())
    target_qty=int(equity*min(weight,genome.max_weight)/(price*(1+fee)))
    cash=ledger.available_cash()
    affordable_qty=int(cash/(price*(1+fee)))
    if affordable_qty<=0:
     rejected["no_cash" if cash<=0 else "lot_too_expensive"]+=1
     if cash<=0:break
     continue
    qty=min(target_qty,affordable_qty)
    if qty<=0:
     rejected["below_minimum_allocation"]+=1
     continue
    # Do not create accidental dust positions from residual cash.
    if qty<max(1,int(target_qty*.25)):
     rejected["below_minimum_allocation"]+=1
     break
    ledger.execute_open(Order(decision,t,"BUY",qty),ds,price)
    positions[t]=PositionState(qty,price,price,0)
  if any(q>0 and t not in closes for t,q in ledger.holdings.items()):
   raise ValueError("Missing held-security close")
  # Independently replay executed fills into inventory; split-adjusted prices
  # require no additional share conversion on corporate-action dates.
  if i==0:replayed_inventory={};replayed_fill_cursor=0
  for fill in ledger.fills[replayed_fill_cursor:]:
   t=fill['security'];direction=1 if fill['side']=='BUY' else -1
   replayed_inventory[t]=replayed_inventory.get(t,0)+direction*fill['shares']
   if replayed_inventory[t]<0:raise ValueError('Replayed inventory went short')
  replayed_fill_cursor=len(ledger.fills)
  if {t:q for t,q in replayed_inventory.items() if q}!={t:q for t,q in ledger.holdings.items() if q}:
   raise ValueError('Trade inventory reconciliation failed')
  last.update(closes);nav.append((ds,ledger.nav(closes)))
  shadow.finish(ds,rows,closes,blocked,membership,risk_veto)
  exits=[];entries=[];adjustments=[]
  for t,r in rows.items():
   p=positions.get(t,PositionState())
   if p.shares:
    p=PositionState(p.shares,p.entry_price,max(p.peak_price,closes[t]),p.sessions_held+1)
    positions[t]=p
   f=extract(r,fields)
   if f is None:
    trace["feature_missing"]+=1
    continue
   trace["feature_valid"]+=1
   action,weight=fast_signal(genome,f,p,closes[t])
   if p.shares and action in ("EXIT","REPLACE_CANDIDATE"):exits.append(t)
   elif p.shares and action in ("SCALE_IN","SCALE_OUT"):adjustments.append((t,action,weight))
   elif not p.shares and action=="ENTER":
    trace["signal_enter"]+=1
    if niche_labels is None or niche_labels.get((ds,t))==genome.niche:
     trace["niche_match"]+=1
     entries.append((t,weight,f[genome.entry_feature]))
    else:trace["niche_reject"]+=1
  trace["scheduled_entries"]+=len(entries)
  entries.sort(key=lambda x:(-x[2],x[0]))
  # Fail closed if a risk decision or membership snapshot is absent.
  if risk_veto[ds] is not True:
   exits=list(dict.fromkeys(exits+[t for t,q in ledger.holdings.items() if q>0]))
   entries=[];adjustments=[]
  pending=(ds,exits,[(t,w) for t,w,_ in entries],adjustments)
 if not nav:raise ValueError("No sessions")
 trace["executed_buys"]=sum(f["side"]=="BUY" for f in ledger.fills)
 trace["executed_sells"]=sum(f["side"]=="SELL" for f in ledger.fills)
 # Independent accounting identity: cash flows + marked positions = reported NAV.
 gross_buy=sum(f['shares']*f['price'] for f in ledger.fills if f['side']=='BUY')
 gross_sell=sum(f['shares']*f['price'] for f in ledger.fills if f['side']=='SELL')
 fees=sum(f['fee'] for f in ledger.fills)
 closing_holdings_value=sum(q*last[t] for t,q in ledger.holdings.items() if q)
 expected_nav=starting_cash-gross_buy+gross_sell-fees+ledger.dividend_cash+ledger.cash_yield_total+closing_holdings_value
 if abs(expected_nav-nav[-1][1])>max(.01,abs(nav[-1][1])*1e-9):raise ValueError('Portfolio cash-flow/NAV reconciliation failed')
 peak=starting_cash;mdd=0.
 for _,v in nav:
  peak=max(peak,v);mdd=min(mdd,v/peak-1)
 years=max((pd.Timestamp(nav[-1][0])-pd.Timestamp(nav[0][0])).days/365.25,1/365.25)
 return {"status":"GUARDED_RESEARCH_ONLY","sessions":len(nav),"fills":len(ledger.fills),"signal_trace":trace,
         "corporate_actions":len(ledger.action_log),"scale_fills":scale_fills,"cash_yield_earned":ledger.cash_yield_total,"cash_proxy_annual_yield":annual_cash_yield,"rejections":rejected,"shadow":{k:v for k,v in shadow.summary().items() if k!='trades'},
         "reconciliation":{"portfolio_basis":"cash_constrained_realized_and_mark_to_market","shadow_basis":"independent_unit_notional_including_signals_not_portfolio_filled","shadow_portfolio_pnl_comparable":False,"portfolio_trade_count":len(ledger.fills),"shadow_closed_trade_count":len(shadow.closed),"cash_flow_nav_error":expected_nav-nav[-1][1],"gross_buy_notional":gross_buy,"gross_sell_notional":gross_sell,"fees":fees,"dividend_cash":ledger.dividend_cash,"cash_yield":ledger.cash_yield_total,"closing_holdings_value":closing_holdings_value},"final_nav":nav[-1][1],"cagr_diagnostic":(nav[-1][1]/starting_cash)**(1/years)-1,
         "mdd_diagnostic":mdd,"calmar_diagnostic":calmar((nav[-1][1]/starting_cash)**(1/years)-1,mdd),"exit_objectives":exit_metrics(shadow.closed),"first_date":nav[0][0],"last_date":nav[-1][0]}
