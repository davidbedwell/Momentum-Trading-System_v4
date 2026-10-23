"""Chronological policy fit: frozen pre-2021 memory, fit 2021-22, score 2023+. Research only."""
import json
from pathlib import Path
import numpy as np,pandas as pd
R=Path('/opt/mts/ga5_redesign');O=R/'forward_only_niche_policy_v1';O.mkdir(exist_ok=True)
m=json.load(open(R/'chronological_memory_corrected_v2/memory.json'));F=m['features'];cent=np.array(m['centers']);mu=np.array(m['median']);sc=np.array(m['scale']);p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');stocks=json.load(open(R/'stocks31_40_corrected_v2/checkpoint.json'))['accepted'];p=p[p.ticker.isin(stocks)].copy();p.date=pd.to_datetime(p.date);parts=[];H=[5,10,20,40,63]
for t,g in p.groupby('ticker'):
 g=g.sort_values('date').copy();c=g.adj_close.astype(float);delta=c.diff();flip=((np.sign(delta)*np.sign(delta.shift(1)))<0).astype(float)
 for w in [10,20,40]:
  net=(c-c.shift(w)).abs();g[f'efficiency_{w}']=(net/delta.abs().rolling(w).sum().replace(0,np.nan)).clip(0,1);g[f'reversal_rate_{w}']=flip.rolling(w).mean();g[f'net_to_volatility_{w}']=net/(delta.abs().rolling(w).std()*np.sqrt(w)).replace(0,np.nan)
 ratio=g.adj_close/g.close.replace(0,np.nan);g['range_width_20']=((g.high*ratio).rolling(20).max()-(g.low*ratio).rolling(20).min())/c.replace(0,np.nan);g=g.replace([np.inf,-np.inf],np.nan).dropna(subset=F);x=np.clip((g[F].to_numpy()-mu)/sc,-5,5);g['niche']=np.linalg.norm(x[:,None,:]-cent[None,:,:],axis=2).argmin(axis=1);ao=g.open*(g.adj_close/g.close.replace(0,np.nan))
 for h in H:g[f'r{h}']=ao.shift(-(h+1))/ao.shift(-1)-1
 parts.append(g[['ticker','date','niche']+[f'r{h}' for h in H]])
p=pd.concat(parts);cal=p[(p.date>='2021-01-01')&(p.date<'2023-01-01')].copy();test=p[p.date>='2023-01-01'].copy();pol=[];out=[]
# Training labels require full exit by 2022-12-31, preventing 2023 information from informing policies.
for h in H:
 enddate=cal.date+pd.to_timedelta(int(h*1.6+8),unit='D');cut=cal[(enddate<'2023-01-01')&cal[f'r{h}'].notna()].copy();future=test[test[f'r{h}'].notna()].copy()
 # fixed, interpretable policy: invest in niche iff calibration expected long net return exceeds pooled calibration return + 1pp and 40 samples.
 baseline=cut[f'r{h}'].mean();policy={};
 for n in range(len(cent)):
  v=cut[cut.niche==n][f'r{h}'];policy[n]=bool(len(v)>=40 and v.mean()-.001>baseline+.01);pol.append({'horizon':h,'niche':m['ids'][n],'calibration_obs':len(v),'calibration_gross_mean':float(v.mean()) if len(v) else None,'trade':policy[n]})
 future['trade']=future.niche.map(policy);v=future[f'r{h}'];gross=v.where(future.trade,0);net=gross-future.trade.astype(float)*.001;by_date=future.groupby('date')[f'r{h}'].mean();benchmark=future.date.map(by_date);out.append({'horizon':h,'calibration_rows':len(cut),'test_rows':len(future),'test_stocks':future.ticker.nunique(),'active_niches':[m['ids'][n] for n in range(len(cent)) if policy[n]],'trade_rate':float(future.trade.mean()),'mean_policy_net_per_opportunity':float(net.mean()),'mean_all_long_net_per_opportunity':float((v-.001).mean()),'mean_cash':0.,'mean_trade_net_conditional':float(net[future.trade].mean()) if future.trade.any() else None,'mean_date_matched_excess_while_trading':float((v[future.trade]-benchmark[future.trade]).mean()) if future.trade.any() else None})
pd.DataFrame(pol).to_csv(O/'calibration_policies.csv',index=False);pd.DataFrame(out).to_csv(O/'forward_results.csv',index=False);report={'status':'EXPLORATORY_FORWARD_POLICY_NOT_CERTIFIED','memory_train_end':'2020-12-31','policy_fit':'2021-2022','evaluation':'2023-2026','memory_niches':len(cent),'calibration_stocks':cal.ticker.nunique(),'test_stocks':test.ticker.nunique(),'results':out,'limitations':['Memory frozen from pre-2021, but feature PIT provenance unverified','2023+ previously inspected by other studies, not pristine independent blind','Calibration includes stocks not used in niche memory learning; 2021-22 labels censored conservatively','Single entry signal at every stock-date; overlapping positions not portfolio implementable','Portfolio capital limits, realistic exits, borrow, slippage beyond 10 bps not modeled','Niche 0013 does not exist in this frozen 2020 memory; testing 12 niches only','Fixed 1 percentage point hurdle across horizons is a provisional baseline, not optimized']};(O/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'niches':len(cent),'results':out},indent=2))
