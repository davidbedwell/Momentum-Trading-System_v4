import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');o=r/'dev79_historical_comparison_20261020';p=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet');p.date=pd.to_datetime(p.date);p=p[p.date>='2017-01-01'].copy();p['px']=p.open*p.adj_close/p.close;p=p.sort_values(['date','ticker']);days=sorted(p.date.unique());bydate={d:g.set_index('ticker') for d,g in p.groupby('date')};a=pd.read_csv(r/'stock_rank_final_diagnostic/nonoverlap_predictions.csv',parse_dates=['date']);res=[]
for h in (20,63):
 anchors={d:g.sort_values('score',ascending=False).ticker.tolist() for d,g in a[a.horizon==h].groupby('date')};cash=100000.;holds={};ledger=[];nav=[];pending=False;target=[];signal_date=None;last={}
 for i,d in enumerate(days):
  frame=bydate[d];prices=frame.px.to_dict();last.update(prices)
  if pending:
   for t,v in list(holds.items()):
    if t not in prices:continue
    px=prices[t];gross=v['shares']*(px-v['entry_price']);fee=v['entry_fee']+v['shares']*px*.001;cash+=v['shares']*px*.999
    path=p[(p.ticker==t)&(p.date>=v['entry_date'])&(p.date<=d)].px.to_numpy();entry=v['entry_price'];mae=float(np.min(path/entry-1)) if len(path) else np.nan;mfe=float(np.max(path/entry-1)) if len(path) else np.nan
    ledger.append(dict(strategy='ranking_reference_'+str(h),ticker=t,signal_date=str(v['signal_date'].date()),entry_date=str(v['entry_date'].date()),entry_price=entry,exit_date=str(d.date()),exit_price=px,shares=v['shares'],entry_fee=v['entry_fee'],exit_fee=v['shares']*px*.001,total_fees=fee,net_pnl=gross-fee,return_pct=100*(gross-fee)/(v['shares']*entry+v['entry_fee']),holding_sessions=i-v['entry_i'],mae_pct=mae*100,mfe_pct=mfe*100,exit_reason='scheduled_rebalance',outcome='LOSS' if gross-fee<0 else 'WIN'))
    del holds[t]
   picks=[t for t in target if t in prices][:20];allocation=cash/len(picks) if picks else 0
   for t in picks:
    px=prices[t];qty=int(allocation/(px*1.001))
    if qty>0 and qty*px*1.001<=cash:cash-=qty*px*1.001;holds[t]=dict(shares=qty,entry_price=px,entry_date=d,entry_i=i,entry_fee=qty*px*.001,signal_date=signal_date)
   pending=False
  equity=cash+sum(v['shares']*prices.get(t,last.get(t,0)) for t,v in holds.items());nav.append((d,equity))
  if d in anchors:target=anchors[d];signal_date=d;pending=True
 if holds:
  d=days[-1];prices=bydate[d].px.to_dict()
  for t,v in holds.items():
   px=prices.get(t,last.get(t));gross=v['shares']*(px-v['entry_price']);fee=v['entry_fee']+v['shares']*px*.001;path=p[(p.ticker==t)&(p.date>=v['entry_date'])&(p.date<=d)].px.to_numpy();ledger.append(dict(strategy='ranking_reference_'+str(h),ticker=t,signal_date=str(v['signal_date'].date()),entry_date=str(v['entry_date'].date()),entry_price=v['entry_price'],exit_date=str(d.date()),exit_price=px,shares=v['shares'],entry_fee=v['entry_fee'],exit_fee=v['shares']*px*.001,total_fees=fee,net_pnl=gross-fee,return_pct=100*(gross-fee)/(v['shares']*v['entry_price']+v['entry_fee']),holding_sessions=len(days)-1-v['entry_i'],mae_pct=100*(min(path)/v['entry_price']-1),mfe_pct=100*(max(path)/v['entry_price']-1),exit_reason='end_of_data_mark_to_market',outcome='LOSS' if gross-fee<0 else 'WIN'))
 df=pd.DataFrame(ledger);df.to_csv(o/f'reference_{h}_dated_trade_ledger.csv',index=False);df[df.outcome=='LOSS'].to_csv(o/f'reference_{h}_failed_trades.csv',index=False);v=np.array([z[1] for z in nav]);years=(days[-1]-days[0]).days/365.25;res.append(dict(strategy='ranking_reference_'+str(h),cagr=(v[-1]/100000)**(1/years)-1,mdd=float((v/np.maximum.accumulate(v)-1).min()),trades=len(df),losers=int((df.outcome=='LOSS').sum()),net_trade_pnl=float(df.net_pnl.sum()),ending_nav=float(v[-1])));print(res[-1],flush=True)
(o/'reference_results.json').write_text(json.dumps({'results':res,'caveat':'REFERENCE RANKING MODEL ONLY; not recovered GA original strategy; marks open positions at end; 10bps each side; approximate adjusted opens; DEV79 survivorship uncertainty; no earnings blackout; no SGOV carry; no blind validation'},indent=2))
