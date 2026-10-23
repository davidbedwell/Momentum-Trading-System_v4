import pandas as pd,numpy as np,json
from pathlib import Path
o=Path('/opt/mts/ga5_redesign/stock_rank_final_diagnostic');windows={'covid_peak_trough':('2020-02-06','2020-03-23'),'covid_extended':('2020-02-06','2020-04-30'),'covid_calendar':('2020-01-01','2020-12-31')};out=[]
for h in (20,63):
 for method in ('rank_top','equal_universe'):
  x=pd.read_csv(o/f'portfolio_{h}_{method}_nav.csv',parse_dates=['date']).sort_values('date');x['r']=x.nav.pct_change().fillna(0);all_years=(x.date.iloc[-1]-x.date.iloc[0]).days/365.25
  for name,(start,end) in windows.items():
   mask=x.date.between(start,end);r=x.loc[~mask,'r'];equity=100000*(1+r).cumprod();dd=(equity/equity.cummax()-1).min();years=all_years-mask.sum()/252;result={'horizon':h,'method':method,'window':name,'excluded_sessions':int(mask.sum()),'cagr_excluding_window':float((equity.iloc[-1]/100000)**(1/years)-1),'mdd_excluding_window':float(dd),'ending_hypothetical':float(equity.iloc[-1]),'excluded_window_compounded_return':float((1+x.loc[mask,'r']).prod()-1)};out.append(result);print(result,flush=True)
(o/'ex_crash_counterfactual.json').write_text(json.dumps({'status':'RETROSPECTIVE_CRASH_WINDOW_RETURN_EXCISION','results':out,'limitations':['Removes realized daily portfolio returns in selected crash window and compounds remaining returns; NOT a tradable exit/reentry strategy','Window selection informed by hindsight','Portfolio ranks and subsequent positions still derived from original continuous historical replay','Excludes window time from annualization; comparisons remain within same data universe']},indent=2))
