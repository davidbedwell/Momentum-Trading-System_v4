import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');o=r/'stock_rank_final_diagnostic';a=pd.read_csv(o/'nonoverlap_predictions.csv',parse_dates=['date']);p=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet');p.date=pd.to_datetime(p.date);p=p[p.date>='2017-01-01'].copy();p['px']=p.open*p.adj_close/p.close;p=p.sort_values(['date','ticker']);days=sorted(p.date.unique());market={d:g.set_index('ticker').px.to_dict() for d,g in p.groupby('date')};pred={h:{d:g.sort_values('score',ascending=False).ticker.tolist() for d,g in a[a.horizon==h].groupby('date')} for h in [20,63]}
# Predicted ranks available on anchor close; buy on next session open; hold until next rebalance; 10 bps each side.
reports=[];allnav=[]
for h in [20,63]:
 for method in ['rank_top','equal_universe']:
  cash=100000.;hold={};last={};nav=[];fees=0.;buys=0;sells=0;anchor=pred[h];target=[];nextday=False
  for i,d in enumerate(days):
   prices=market[d];last.update(prices)
   if nextday:
    equity=cash+sum(q*prices.get(t,last.get(t,0)) for t,q in hold.items())
    for t,q in list(hold.items()):
     if t in prices:cash+=q*prices[t]*.999;fees+=q*prices[t]*.001;sells+=1;del hold[t]
    # Positions equally weighted, no leverage, all capital deployed up to 20 positions.
    picks=[t for t in target if t in prices][:(20 if method=='rank_top' else 1000)];allocation=min(cash/len(picks),equity/len(picks)) if picks else 0
    for t in picks:
     q=int(allocation/(prices[t]*1.001))
     if q>0 and q*prices[t]*1.001<=cash:cash-=q*prices[t]*1.001;fees+=q*prices[t]*.001;hold[t]=q;buys+=1
    nextday=False
   equity=cash+sum(q*prices.get(t,last.get(t,0)) for t,q in hold.items());nav.append((d,equity))
   if d in anchor:
    target=anchor[d] if method=='rank_top' else sorted(prices)
    nextday=True
  v=pd.DataFrame(nav,columns=['date','nav']);v['peak']=v.nav.cummax();mdd=float((v.nav/v.peak-1).min());years=(days[-1]-days[0]).days/365.25;cagr=float((v.nav.iloc[-1]/100000)**(1/years)-1)
  reports.append({'horizon':h,'method':method,'cagr':cagr,'mdd':mdd,'end_nav':float(v.nav.iloc[-1]),'fees':fees,'buys':buys,'sells':sells,'years':years});v[['date','nav']].assign(horizon=h,method=method).to_csv(o/f'portfolio_{h}_{method}_nav.csv',index=False);print('RESULT',reports[-1],flush=True)
(o/'portfolio_comparison.json').write_text(json.dumps({'status':'EXPLORATORY_NOT_CERTIFIED','results':reports,'limitations':['Stock selection based on same 79 exploratory names with possible survivorship bias','Rank-top rebalance uses year-specific nonoverlap anchors; equal universe benchmark uses same anchors','Equal-universe benchmark equally weights all available stocks, but historical membership remains unaudited','No regime or earnings gate, no settlement, approximate dividend/split treatment','No independent PIT audit or untouched blind sample']},indent=2))
