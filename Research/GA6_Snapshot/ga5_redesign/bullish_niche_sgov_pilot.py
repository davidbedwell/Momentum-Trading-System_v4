import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');o=r/'stock_rank_final_diagnostic';p=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet');p.date=pd.to_datetime(p.date);p=p[p.date>='2015-01-01'].sort_values(['ticker','date']);p['px']=p.open*p.adj_close/p.close
# All signals use lagged prior closes, no forward returns or retrospective niche labels.
p['ma200']=p.groupby('ticker').adj_close.transform(lambda x:x.rolling(200,min_periods=200).mean());p['ma50']=p.groupby('ticker').adj_close.transform(lambda x:x.rolling(50,min_periods=50).mean());p['r63']=p.groupby('ticker').adj_close.pct_change(63,fill_method=None);p['r20']=p.groupby('ticker').adj_close.pct_change(20,fill_method=None)
p['bull']=(p.adj_close>p.ma200)&(p.ma50>p.ma200)&(p.r63>0);p['bear']=(p.adj_close<p.ma200)&(p.r63<0)
b=p.groupby('date').agg(bull_breadth=('bull','mean'),bear_breadth=('bear','mean'),median_63=('r63','median'));p=p[p.date>='2017-01-01'];days=sorted(p.date.unique());market={d:g.set_index('ticker').px.to_dict() for d,g in p.groupby('date')};bull={d:g.set_index('ticker').bull.to_dict() for d,g in p.groupby('date')};a=pd.read_csv(o/'nonoverlap_predictions.csv',parse_dates=['date']);pred={h:{d:g.sort_values('score',ascending=False).ticker.tolist() for d,g in a[a.horizon==h].groupby('date')} for h in (20,63)}
results=[]
for h in (20,63):
 for gate in ('stock_bull','breadth40','breadth50','breadth60','combined50'):
  cash=100000.;hold={};last={};nav=[];fees=0;trades=0;pending=False;target=[];exposure=0;anchor=pred[h];prior_breadth=0
  for i,d in enumerate(days):
   prices=market[d];last.update(prices)
   if pending:
    equity=cash+sum(q*prices.get(t,last.get(t,0)) for t,q in hold.items())
    for t,q in list(hold.items()):
     if t in prices:cash+=q*prices[t]*.999;fees+=q*prices[t]*.001;del hold[t]
    eligible=[t for t in target if t in prices and bull.get(signal_date,{}).get(t,False)]
    if gate=='stock_bull':picks=eligible[:20]
    elif gate=='combined50':picks=eligible[:20] if prior_breadth>=.5 else []
    else:picks=[t for t in target if t in prices][:20] if prior_breadth>=float(gate[-2:])/100 else []
    allocation=equity/len(picks) if picks else 0
    for t in picks:
     q=min(int(allocation/(prices[t]*1.001)),int(cash/(prices[t]*1.001)))
     if q>0:cash-=q*prices[t]*1.001;fees+=q*prices[t]*.001;hold[t]=q;trades+=1
    pending=False
   # Cash/SGOV 3% fixed annual carry proxy, daily accrual (not historical SGOV price).
   cash*=1+.03/252
   equity=cash+sum(q*prices.get(t,last.get(t,0)) for t,q in hold.items());nav.append(equity)
   if d in anchor:target=anchor[d];prior_breadth=float(b.loc[d,'bull_breadth']);signal_date=d;pending=True
  v=np.array(nav);years=(days[-1]-days[0]).days/365.25;z={'horizon':h,'gate':gate,'cagr':float((v[-1]/100000)**(1/years)-1),'mdd':float(np.min(v/np.maximum.accumulate(v)-1)),'ending':float(v[-1]),'fees':float(fees),'buys':trades};results.append(z);print('RESULT',z,flush=True)
(o/'bullish_niche_sgov_pilot.json').write_text(json.dumps({'status':'EXPLORATORY_BULLISH_FILTER_PILOT','results':results,'limitations':['These are forward-known deterministic bullish filters, not the learned 13 niches','Portfolio only changes stock exposure at scheduled 20/63-session rebalance','3% constant annual cash carry proxy, not actual historical SGOV (launched 2020)','79-stock exploratory universe may be survivorship biased','No earnings embargo, PIT verification, or blind validation','Parameter variants examined on already exposed sample']},indent=2))
