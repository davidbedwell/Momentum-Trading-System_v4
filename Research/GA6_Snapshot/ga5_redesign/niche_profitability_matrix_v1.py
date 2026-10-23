import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
R=Path('/opt/mts/ga5_redesign');O=R/'niche_profitability_matrix_v1';O.mkdir(exist_ok=True);m=json.load(open(R/'chronological_memory_corrected_v2/memory.json'));ck=json.load(open(R/'stocks31_40_corrected_v2/checkpoint.json'));F=m['features'];cent=np.asarray(ck['centers']);mu=np.asarray(m['median']);sc=np.asarray(m['scale']);p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');p=p[p.ticker.isin(ck['accepted'])].copy();p.date=pd.to_datetime(p.date);parts=[]
for t,g in p.groupby('ticker'):
 g=g.sort_values('date').copy();c=g.adj_close.astype(float);delta=c.diff();flip=((np.sign(delta)*np.sign(delta.shift(1)))<0).astype(float)
 for w in (10,20,40):
  net=(c-c.shift(w)).abs();g[f'efficiency_{w}']=(net/delta.abs().rolling(w).sum().replace(0,np.nan)).clip(0,1);g[f'reversal_rate_{w}']=flip.rolling(w).mean();g[f'net_to_volatility_{w}']=net/(delta.abs().rolling(w).std()*np.sqrt(w)).replace(0,np.nan)
 ratio=g.adj_close/g.close.replace(0,np.nan);g['range_width_20']=((g.high*ratio).rolling(20).max()-(g.low*ratio).rolling(20).min())/c.replace(0,np.nan);g=g.replace([np.inf,-np.inf],np.nan).dropna(subset=F);x=np.clip((g[F].to_numpy()-mu)/sc,-5,5);dist=np.linalg.norm(x[:,None,:]-cent[None,:,:],axis=2);g['niche']=dist.argmin(axis=1);g['distance']=dist.min(axis=1)
 # Conservative next-session open entry and open exit; signal available only after today's close.
 op=g.open.astype(float);adjfactor=g.adj_close/g.close.replace(0,np.nan);adjopen=op*adjfactor
 for h in [1,2,3,5,10,15,20,30,40,63]:
  g[f'forward_{h}']=adjopen.shift(-(h+1))/adjopen.shift(-1)-1
 parts.append(g)
p=pd.concat(parts);p=p[p.date>='2023-01-01'];rows=[]
for n,h,g in ((n,h,p.loc[p[f'forward_{h}'].notna() & (p.niche==n)]) for n in range(len(cent)) for h in [1,2,3,5,10,15,20,30,40,63]):
 v=g[f'forward_{h}'].to_numpy(float);v=v[np.isfinite(v)];N=len(v)
 if not N:continue
 for direction in ['long','short']:
  net=v*(1 if direction=='long' else -1)-.001;rows.append({'niche':ck['ids'][n],'horizon_sessions':h,'direction':direction,'observations':N,'stocks':int(g.ticker.nunique()),'mean_net_return':float(net.mean()),'median_net_return':float(np.median(net)),'win_rate':float((net>0).mean()),'std_net_return':float(net.std()),'naive_se':float(net.std()/np.sqrt(N)),'years':int(g.date.dt.year.nunique())})
q=pd.DataFrame(rows);q.to_csv(O/'matrix.csv',index=False);summary=[]
for n,g in q.groupby('niche'):
 e=g[(g.observations>=100)&(g.stocks>=5)].sort_values('mean_net_return',ascending=False);summary.append({'niche':n,'qualified_combinations':len(e),'best_descriptive':e.iloc[0][['direction','horizon_sessions','mean_net_return','win_rate','observations','stocks']].to_dict() if len(e) else None})
report={'status':'EXPLORATORY_DESCRIPTIVE_NOT_CERTIFIED','stock_count':int(p.ticker.nunique()),'rows':len(p),'niches':len(cent),'matrix_rows':len(q),'best_by_niche':summary,'assumptions':['Niche assigned using final adapted memory (retrospective, not online walk-forward)','Entry next-session adjusted open, exit open after specified sessions','10 bps round-trip cost','Overlapping returns and shared market dates; naive SE invalid for inference','Short returns omit borrow fees and short availability','2023-2026 data repeatedly inspected; not independent holdout','Source features PIT provenance and stock partition eligibility unverified','No forward-return optimization, sizing, or deployment approval from this descriptive matrix']};(O/'report.json').write_text(json.dumps(report,indent=2,default=str));print(json.dumps({'stocks':report['stock_count'],'rows':report['rows'],'niches':report['niches'],'matrix_rows':report['matrix_rows'],'best':summary},default=str))
