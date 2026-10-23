import json,pathlib,collections
import pandas as pd
P=pathlib.Path('/opt/mts/ga6/runs/post_v3_comparison_20261022');a=[json.loads(x) for x in (P/'dev87_drawdown_autopsy.jsonl').open()];assert len(a)==53
rows=[]
for rec in a:
 h=rec['hash'];peak=rec['trough']['peak_date'];trough=rec['trough']['trough_date'];nav={x['date']:x for x in rec['daily']};p=nav.get(peak,{'holdings':{}});q=nav.get(trough,{'holdings':{}})
 tickers=set(p['holdings'])|set(q['holdings'])
 for t in rec['trades']:
  if any(peak<f['execution_date']<=trough for f in t['fills']):tickers.add(t['ticker'])
 for ticker in tickers:
  start=p['holdings'].get(ticker);end=q['holdings'].get(ticker)
  value0=(start['shares']*start['close']) if start else 0.;value1=(end['shares']*end['close']) if end else 0.
  flows=0.;fee=0.;related=[]
  for trade in rec['trades']:
   if trade['ticker']!=ticker:continue
   for f in trade['fills']:
    if peak<f['execution_date']<=trough:
     flows+=(f['shares']*f['price'] if f['side']=='SELL' else -f['shares']*f['price']);fee+=f['fee'];related.append(trade)
  pnl=value1-value0+flows-fee
  if pnl!=0:rows.append({'chromosome':h,'ticker':ticker,'peak_date':peak,'trough_date':trough,'peak_nav':rec['trough']['peak_nav'],'trough_nav':rec['trough']['trough_nav'],'ticker_peak_trough_pnl':pnl,'portfolio_peak_trough_loss':rec['trough']['trough_nav']-rec['trough']['peak_nav'],'pnl_as_peak_nav_pct':pnl/rec['trough']['peak_nav'],'position_at_peak':bool(start),'position_at_trough':bool(end),'related_completed_trades':len(set(x['entry_date'] for x in related))})
d=pd.DataFrame(rows);d.to_csv(P/'dev87_peak_trough_ticker_contributions.csv',index=False)
print('peak-trough ticker contributions',len(d),'negative',sum(d.ticker_peak_trough_pnl<0));print(d.nsmallest(12,'pnl_as_peak_nav_pct')[['chromosome','ticker','peak_date','trough_date','pnl_as_peak_nav_pct']].to_string(index=False))
