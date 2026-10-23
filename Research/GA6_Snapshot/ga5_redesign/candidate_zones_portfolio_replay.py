import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');o=r/'final_predictive_signal_audit_20261020';p=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet');p.date=p.date.astype(str).str[:10];p=p[p.date>='2022-01-01'].sort_values(['date','ticker']);p['px']=p.open*p.adj_close/p.close
sig=pd.read_csv(o/'candidate_zone_signals_2022plus.csv');sig.date=sig.date.astype(str);signals={(d,t):(int(h),n) for d,t,h,n in sig[['date','ticker','horizon','niche']].itertuples(index=False,name=None)}
cal=sorted(p.date.unique());bydate={d:g.set_index('ticker') for d,g in p.groupby('date')};cash=100000.;hold={};pending=[];history=[];fills=[];last={};fee=.001;peak=100000.;maxdd=0.;exposure=[]
for i,d in enumerate(cal):
 day=bydate[d];opens=day.px.to_dict();closes=(day.adj_close).to_dict();last.update(closes)
 # Execute decisions at next available session open, with settlement-conservative next-session sale proceeds.
 for ticker in list(hold):
  z=hold[ticker]
  if i>=z['exit_index'] and ticker in opens:
   proceeds=z['qty']*opens[ticker]*(1-fee);cash+=proceeds;fills.append(('SELL',d,ticker,z['qty'],proceeds));del hold[ticker]
 if i>0:
  for ticker,h,n in pending:
   if ticker in hold or ticker not in opens or len(hold)>=20:continue
   px=opens[ticker];equity=cash+sum(v['qty']*opens.get(k,last.get(k,0)) for k,v in hold.items());qty=min(int(.05*equity/(px*(1+fee))),int(cash/(px*(1+fee))))
   if qty<=0:continue
   cost=qty*px*(1+fee);cash-=cost;hold[ticker]={'qty':qty,'exit_index':i+h,'entry':px,'niche':n};fills.append(('BUY',d,ticker,qty,cost))
 pending=[]
 for ticker in day.index:
  if ticker not in hold and (d,ticker) in signals:
   h,n=signals[(d,ticker)];pending.append((ticker,h,n))
 invested=sum(v['qty']*closes.get(k,last.get(k,0)) for k,v in hold.items());nav=cash+invested;peak=max(peak,nav);maxdd=min(maxdd,nav/peak-1);history.append((d,nav,invested/nav if nav else 0,len(hold)));exposure.append(invested/nav if nav else 0)
nav=pd.DataFrame(history,columns=['date','nav','invested_fraction','positions']);nav.to_csv(o/'candidate_zone_portfolio_nav.csv',index=False);f=pd.DataFrame(fills,columns=['side','date','ticker','qty','cash_flow']);f.to_csv(o/'candidate_zone_portfolio_fills.csv',index=False)
years=(pd.Timestamp(cal[-1])-pd.Timestamp(cal[0])).days/365.25;report={'status':'EXPLORATORY_RETROSPECTIVE_SELECTION','start_cash':100000,'end_nav':float(nav.nav.iloc[-1]),'cagr':float((nav.nav.iloc[-1]/100000)**(1/years)-1),'mdd':float(maxdd),'mean_utilization':float(np.mean(exposure)),'buys':int((f.side=='BUY').sum()),'sells':int((f.side=='SELL').sum()),'open_positions':len(hold),'years':years,'limitations':['Signals selected partly using 2022+ outcomes: in-sample selection bias','Research-only 12 frozen niches, not all 13','Split-adjusted opens and adjusted closes; dividend accounting may be approximate','Cash from sales available same day, settlement not modeled','No earnings embargo or defensive regime gate','No independent out-of-sample certification']};(o/'candidate_zone_portfolio_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
