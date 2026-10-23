import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');o=r/'stock_rank_final_diagnostic';a=pd.read_csv(o/'nonoverlap_predictions.csv',parse_dates=['date']);p=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet');p.date=pd.to_datetime(p.date);p=p[p.date>='2017-01-01'].copy();p['px']=p.open*p.adj_close/p.close;p=p.sort_values(['date','ticker']);days=sorted(p.date.unique());market={d:g.set_index('ticker').px.to_dict() for d,g in p.groupby('date')};pred={h:{d:g.sort_values('score',ascending=False).ticker.tolist() for d,g in a[a.horizon==h].groupby('date')} for h in [20,63]}
# Signal at close of anchor, execution next open. Exposure policy based only on previous closes; fixed parameter sweep exploratory.
results=[]
for h in [20,63]:
 for mode in ['full','trend200','trend100','vol20','vol30','half']:
  cash=100000.;hold={};last={};nav=[];fees=0.;buys=0;sells=0;target=[];pending=False;anchor=pred[h];prev_equity=100000.;hist=[]
  for i,d in enumerate(days):
   prices=market[d];last.update(prices)
   if pending:
    equity=cash+sum(q*prices.get(t,last.get(t,0)) for t,q in hold.items())
    for t,q in list(hold.items()):
     if t in prices:cash+=q*prices[t]*.999;fees+=q*prices[t]*.001;sells+=1;del hold[t]
    vals=np.array(hist,dtype=float);exposure=1.
    if mode=='half':exposure=.5
    elif mode.startswith('trend'):
     w=int(mode[5:]);exposure=1. if len(vals)<w else (1. if vals[-1]>vals[-w:].mean() else 0.)
    elif mode.startswith('vol'):
     w=int(mode[3:]);rets=np.diff(np.log(vals[-(w+1):])) if len(vals)>w else np.array([]);exposure=1. if len(rets)==w and np.std(rets)*np.sqrt(252)<.28 else 0.
    picks=[t for t in target if t in prices][:20];allocation=equity*exposure/len(picks) if picks else 0
    for t in picks:
     q=min(int(allocation/(prices[t]*1.001)),int(cash/(prices[t]*1.001)))
     if q>0:cash-=q*prices[t]*1.001;fees+=q*prices[t]*.001;hold[t]=q;buys+=1
    pending=False
   equity=cash+sum(q*prices.get(t,last.get(t,0)) for t,q in hold.items());nav.append(equity);hist.append(equity)
   if d in anchor:target=anchor[d];pending=True
  v=np.array(nav);peak=np.maximum.accumulate(v);mdd=float(np.min(v/peak-1));years=(days[-1]-days[0]).days/365.25;cagr=float((v[-1]/100000)**(1/years)-1);z={'horizon':h,'mode':mode,'cagr':cagr,'mdd':mdd,'ending':float(v[-1]),'fees':fees,'buys':buys,'sells':sells};results.append(z);print('RESULT',z,flush=True)
(o/'risk_sweep.json').write_text(json.dumps({'status':'EXPLORATORY_SWEEP_NOT_VALIDATION','results':results,'limitations':['Risk gate computed on portfolio NAV at previous rebalance and is path dependent','Gates evaluated only on rebalance dates; may miss intra-horizon drawdowns','Same repeatedly exposed historical years; no independent validation','79-stock exploratory universe not PIT certified','No earnings embargo, regime model, or settlement accounting','Fixed 28% annualized volatility threshold and 100/200-session trends not calibrated independently']},indent=2))
