import json
from pathlib import Path
import numpy as np,pandas as pd
R=Path('/opt/mts/ga5_redesign');O=R/'niche_excess_return_audit_v1';O.mkdir(exist_ok=True);m=json.load(open(R/'chronological_memory_corrected_v2/memory.json'));ck=json.load(open(R/'stocks31_40_corrected_v2/checkpoint.json'));F=m['features'];cent=np.array(ck['centers']);mu=np.array(m['median']);sc=np.array(m['scale']);p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');p=p[p.ticker.isin(ck['accepted'])].copy();p.date=pd.to_datetime(p.date);parts=[];H=[1,2,3,5,10,15,20,30,40,63]
for t,g in p.groupby('ticker'):
 g=g.sort_values('date').copy();c=g.adj_close.astype(float);delta=c.diff();flips=((np.sign(delta)*np.sign(delta.shift(1)))<0).astype(float)
 for w in (10,20,40):
  net=(c-c.shift(w)).abs();g[f'efficiency_{w}']=(net/delta.abs().rolling(w).sum().replace(0,np.nan)).clip(0,1);g[f'reversal_rate_{w}']=flips.rolling(w).mean();g[f'net_to_volatility_{w}']=net/(delta.abs().rolling(w).std()*np.sqrt(w)).replace(0,np.nan)
 ratio=g.adj_close/g.close.replace(0,np.nan);g['range_width_20']=((g.high*ratio).rolling(20).max()-(g.low*ratio).rolling(20).min())/c.replace(0,np.nan);g=g.replace([np.inf,-np.inf],np.nan).dropna(subset=F);x=np.clip((g[F].to_numpy()-mu)/sc,-5,5);g['niche']=np.linalg.norm(x[:,None,:]-cent[None,:,:],axis=2).argmin(axis=1);adjopen=g.open*(g.adj_close/g.close.replace(0,np.nan))
 for h in H:g[f'r{h}']=adjopen.shift(-(h+1))/adjopen.shift(-1)-1
 parts.append(g[['ticker','date','niche']+[f'r{h}' for h in H]])
p=pd.concat(parts);p=p[p.date>='2023-01-01'].copy();out=[];overall=[]
for h in H:
 c=f'r{h}';v=p[p[c].notna()].copy();dateavg=v.groupby('date')[c].mean();stockavg=v.groupby('ticker')[c].mean();v['market_same_date']=v.date.map(dateavg);v['stock_period_avg']=v.ticker.map(stockavg);v['excess_date']=v[c]-v.market_same_date;v['excess_stock']=v[c]-v.stock_period_avg
 overall.append({'horizon':h,'unconditional_avg_pct':round(float(v[c].mean()*100),3),'avg_date_dispersion_pct':round(float(v.groupby('date')[c].std().mean()*100),3)})
 for n,g in v.groupby('niche'):
  # Date matched comparator is leave-one-out average of other stocks on same date.
  date_sum=v.groupby('date')[c].transform('sum');date_count=v.groupby('date')[c].transform('count');v['leave_one_out']=(date_sum-v[c])/(date_count-1).replace(0,np.nan)
  g=v[v.niche==n];valid=g['leave_one_out'].notna();ex=(g.loc[valid,c]-g.loc[valid,'leave_one_out']);out.append({'niche':ck['ids'][int(n)],'horizon':h,'obs':len(g),'stocks':g.ticker.nunique(),'absolute_mean_pct':round(float(g[c].mean()*100),3),'date_matched_excess_pct':round(float(ex.mean()*100),3) if len(ex) else None,'stock_average_excess_pct':round(float(g.excess_stock.mean()*100),3),'positive_date_matched_share':round(float((ex>0).mean()),3) if len(ex) else None})
q=pd.DataFrame(out);q.to_csv(O/'excess_matrix.csv',index=False);long=q[q.horizon==63].sort_values('date_matched_excess_pct',ascending=False);report={'status':'EXPLORATORY_NOT_CERTIFIED','stocks':int(p.ticker.nunique()),'rows':len(p),'unconditional_by_horizon':overall,'horizon63_niches':long.to_dict('records'),'limitations':['Date-matched benchmark uses other available study stocks, not independent SPY','Final adapted memory is retrospectively applied; not walk-forward','Overlapping forward returns and correlated market dates','Unverified PIT predictor lineage and universe partitions','Same previously used 2023-2026 sample; descriptive comparisons only','No statistical significance or multiple-testing correction']};(O/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'unconditional':overall,'horizon63':long.to_dict('records')},indent=2))
