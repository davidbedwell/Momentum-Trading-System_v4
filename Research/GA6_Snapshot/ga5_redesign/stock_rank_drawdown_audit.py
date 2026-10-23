import pandas as pd,numpy as np,json
from pathlib import Path
o=Path('/opt/mts/ga5_redesign/stock_rank_final_diagnostic');out=[]
for h in [20,63]:
 for method in ['rank_top','equal_universe']:
  p=pd.read_csv(o/f'portfolio_{h}_{method}_nav.csv',parse_dates=['date']);p['year']=p.date.dt.year;p['peak']=p.nav.cummax();p['dd']=p.nav/p.peak-1;trough=p.dd.idxmin();peak=p.loc[:trough,'nav'].idxmax();annual=[]
  for y,g in p.groupby('year'):
   prior=p[p.date<g.date.iloc[0]];start=prior.nav.iloc[-1] if len(prior) else 100000
   annual.append({'year':int(y),'return':float(g.nav.iloc[-1]/start-1),'worst_drawdown_from_alltime_peak':float(g.dd.min())})
  z={'horizon':h,'method':method,'worst_drawdown':float(p.dd.min()),'peak_date':str(p.date.iloc[peak].date()),'trough_date':str(p.date.iloc[trough].date()),'drawdown_sessions':int(trough-peak),'annual':annual};out.append(z)
  print('AUDIT',h,method,'peak',z['peak_date'],'trough',z['trough_date'],'annual',[(x['year'],round(x['return'],3)) for x in annual],flush=True)
(o/'drawdown_annual_audit.json').write_text(json.dumps(out,indent=2))
