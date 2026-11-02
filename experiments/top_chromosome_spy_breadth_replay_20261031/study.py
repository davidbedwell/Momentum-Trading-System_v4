"""Bounded chronological cached-fill replay; no writes outside this experiment."""
from pathlib import Path
import sys,json,gzip,hashlib,time,importlib.util
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy.stats import norm,rankdata
R=Path(__file__).resolve().parent; P=R.parent/'breadth_chromosome_entry_20261031'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
multi=module('multi',R.parent/'breadth_chromosome_multihorizon_20261031/study.py')
prior=module('prior',R.parent/'spy_state_predictor_20261031/study.py')
maemod=module('maemod',Path('/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518/ga6_ga7_common_v1_mae_reconstruction_20261028.py'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rank_candidates(nav,dates,cut):
 a=np.asarray(nav)[dates<pd.Timestamp(cut)]; years=(dates[dates<pd.Timestamp(cut)][-1]-dates[0]).days/365.25
 cagr=(a[-1]/100000)**(1/years)-1;dd=abs(min(a/np.maximum.accumulate(np.r_[100000,a])[1:]-1));return cagr,dd,cagr/max(dd,.01)
def corr(g,feat,method='pearson',within=False):
 u=g.dropna(subset=[feat,'net_return']).copy()
 if len(u)<20:return None
 x=u[feat].to_numpy();y=u.net_return.to_numpy()
 if method=='spearman':x=rankdata(x);y=rankdata(y)
 if within:
  keys=[u.chromosome_id,u.year];x=pd.Series(x,index=u.index);y=pd.Series(y,index=u.index)
  x=(x-x.groupby(keys).transform('mean')).to_numpy();y=(y-y.groupby(keys).transform('mean')).to_numpy()
 x=x-x.mean();y=y-y.mean();sx=np.sqrt(np.mean(x*x));sy=np.sqrt(np.mean(y*y))
 if sx<1e-12 or sy<1e-12:return None
 x=x/sx;y=y/sy;r=np.mean(x*y)
 inf=(x*y-r*(x*x+y*y)/2)/len(x)
 scores=pd.Series(inf,index=u.entry_date).groupby(level=0).sum().reindex(pd.bdate_range(u.entry_date.min(),u.exit_date.max()),fill_value=0).to_numpy()
 def se(lag):
  v=np.dot(scores,scores)
  for k in range(1,min(lag,len(scores)-1)+1):v+=2*(1-k/(lag+1))*np.dot(scores[k:],scores[:-k])
  return np.sqrt(max(v,0))
 e=se(63);e2=se(126)
 if len(u)<30 or u.entry_date.nunique()<20:e=e2=np.nan
 return dict(n=len(u),dates=u.entry_date.nunique(),correlation=r,se=e,lo=max(-1,r-1.96*e),hi=min(1,r+1.96*e),se126=e2,p=2*norm.sf(abs(r/e)) if e else np.nan)
def reconstruct(d,bars):
 ev=defaultdict(list)
 for j,e in enumerate(d['fills']):ev[e['ticker']].append({**e,'_ord':j})
 out={}
 for ticker,events in ev.items():
  qty=0;cycle=[]
  for e in events:
   qty+=(1 if e['action']=='BUY' else -1)*e['qty'];cycle.append(e)
   if abs(qty)<1e-6:
    cost=sum(z['cost'] for z in cycle if z['action']=='BUY');mae,risk,pnl=maemod.calc_position(ticker,cycle,bars)
    out[(ticker,cycle[0]['session'],cycle[-1]['session'])]=(cost,mae,pnl);cycle=[];qty=0
 return out
FOLDS=[('F1','2012-01-01','2014-01-01'),('F2','2014-01-01','2016-01-01'),('F3','2016-01-01','2018-01-01')]
def main():
 start=time.monotonic();hashes={};selection=pd.read_csv(P/'selection.csv');inv=pd.read_csv(P/'ledger_inventory.csv');pool=selection[selection.identity_sample].merge(inv[['system','chromosome_id','path']],on=['system','chromosome_id'])
 # fixed identity sample only: no retrospective top-list additions
 meta=json.loads((R.parent/'spy_state_predictor_20261031/run_metadata.json').read_text())['sources'];sp=pd.read_parquet(meta['SPY']['path']);sp['date']=pd.to_datetime(sp.date).dt.tz_localize(None);cal=pd.DatetimeIndex(sp.date).sort_values()
 raw=pd.read_parquet(meta['DEV79']['path']);raw['date']=pd.to_datetime(raw.date).dt.tz_localize(None);prices=raw.pivot(index='date',columns='ticker',values='adj_close').sort_index();f=multi.build(prices,cal);f.index.name='entry_date';f.to_csv(R/'entry_features.csv')
 spy=sp.set_index('date').adj_close.reindex(cal);f['momentum_bin']=(spy/spy.shift(63)-1>0).shift(1);f['vol_bin']=pd.cut(spy.pct_change().rolling(20).std()*np.sqrt(252),[0,.15,.25,np.inf],labels=False).shift(1)
 dates=pd.DatetimeIndex(sorted(pd.read_parquet('/opt/mts/ga6/data/ga6d_defensive_features.parquet',columns=['date']).query("date >= '2009-01-01' and date < '2019-01-01'").date.unique()))
 rankings=[]
 for row in pool.itertuples():
  d=json.load(gzip.open(row.path,'rt'))
  for fold,cut,end in FOLDS:
   n=sum(t['exit_date']<cut for t in d['trades'])
   c,dd,score=rank_candidates(d['nav'],dates,cut)
   rankings.append(dict(fold=fold,system=row.system,chromosome_id=row.chromosome_id,path=row.path,training_start='2009-01-01',training_end=cut,test_end=end,training_closed_trades=n,cagr=c,mdd=dd,score=score))
 rank=pd.DataFrame(rankings);rank['selected']=False
 for _,g in rank[rank.training_closed_trades>=30].groupby(['fold','system']):rank.loc[g.sort_values(['score','chromosome_id'],ascending=[False,True]).head(3).index,'selected']=True
 rank.to_csv(R/'candidate_rankings.csv',index=False);chosen=rank[rank.selected];chosen.to_csv(R/'selection.csv',index=False)
 bars=maemod.load_bars();records=[];audit=[];training={}
 for path,sel in chosen.groupby('path'):
  d=json.load(gzip.open(path,'rt'));hashes[path]=sha(path);cycles=reconstruct(d,bars)
  rows=[]
  for t in d['trades']:
   cost,mae,pnl=cycles[(t['ticker'],t['entry_session'],t['exit_session'])];assert abs(pnl-t['pnl'])<.01
   rows.append(dict(**t,net_return=t['pnl']/cost,acquisition_cost=cost,mae_pnl=mae,mae_return=mae/cost,mae_method='OHLC_LOW_MODEL_FILL_PROXY',system=d['system'],chromosome_id=d['chromosome_id']))
  v=pd.DataFrame(rows);v['entry_date']=pd.to_datetime(v.entry_date);v['exit_date']=pd.to_datetime(v.exit_date);v=v.join(f,on='entry_date');v['year']=v.entry_date.dt.year
  for s in sel.itertuples():
   train=v[v.exit_date<pd.Timestamp(s.training_end)].copy();training[(s.fold,s.system,s.chromosome_id)]=train
   test=v[(v.entry_date>=pd.Timestamp(s.training_end))&(v.entry_date<pd.Timestamp(s.test_end))&(v.exit_date<pd.Timestamp(s.test_end))].copy();test['fold']=s.fold;records.extend(test.to_dict('records'))
   audit.append(dict(fold=s.fold,system=s.system,chromosome_id=s.chromosome_id,training_trades=len(train),test_trades=len(test),boundary_excluded=int(((v.entry_date>=pd.Timestamp(s.training_end))&(v.entry_date<pd.Timestamp(s.test_end))&(v.exit_date>=pd.Timestamp(s.test_end))).sum())))
 t=pd.DataFrame(records)
 # GA8 archived original-cost completed episodes; no invented additional winners or fills.
 g=pd.read_csv(P/'ga8_trades.csv',parse_dates=['entry_date','exit_date']);g=g[['ticker','entry_date','exit_date','pnl','net_return','bought','chromosome_id','year']];g['system']='GA8';g['fold']=g.year.map(lambda y:f'GA8_{y}');g['acquisition_cost']=g.bought;g=g.drop(columns='bought').join(f,on='entry_date')
 maes=[]
 for z in g.itertuples():
  a=prices.loc[z.entry_date:z.exit_date,z.ticker].dropna();maes.append(min(0,float((a/a.iloc[0]-1).min())) if len(a) else np.nan)
 g['mae_return']=maes;g['mae_method']='ADJUSTED_CLOSE_PATH_PROXY_NOT_FILL_MAE';t=pd.concat([t,g],ignore_index=True);t['win']=t.pnl>0;t['breadth_source']='DEV79 retrospective universe proxy';t.to_csv(R/'trades.csv.gz',index=False);pd.DataFrame(audit).to_csv(R/'fold_audit.csv',index=False)
 results=[];dec=[];year=[];matched=[]
 for system,u in t.groupby('system'):
  for feat in [f'b{m}' for m in [10,20,50,100,200]]+['v50_5','a50_5']:
   for method in ['pearson','spearman']:
    for within in [False,True]:
     z=corr(u,feat,method,within)
     if z:results.append(dict(system=system,feature=feat,method=method,within_chromosome_year=within,**z))
   if feat.startswith('b'):
    v=u.copy();v['decile']=(np.ceil(v[feat]*10).clip(1,10)).astype('Int64')
    z=v.groupby('decile').agg(n=('net_return','size'),dates=('entry_date','nunique'),mean_return=('net_return','mean'),win_rate=('win','mean')).reset_index();z['system']=system;z['feature']=feat;dec.extend(z.to_dict('records'))
  for (cid,yr),v in u.groupby(['chromosome_id','year']):
   for method in ['pearson','spearman']:
    z=corr(v,'b50',method)
    if z:year.append(dict(system=system,chromosome_id=cid,year=yr,method=method,**z))
  # Match only entry-known conditions: same chromosome, ticker, year, SPY momentum and volatility.
  v=u.dropna(subset=['b50','momentum_bin','vol_bin']).copy();v=v[(v.b50<.4)|(v.b50>.6)];v['arm']=(v.b50<.4).astype(int);keys=['chromosome_id','ticker','year','momentum_bin','vol_bin'];v=v[v.groupby(keys).arm.transform('nunique')==2]
  if len(v):
   cells=v.groupby(keys+['arm']).net_return.mean().unstack();matched.append(dict(system=system,n=len(v),cells=len(cells),weak_minus_strong=float((cells[1]-cells[0]).mean())))
 pd.DataFrame(matched).to_csv(R/'matched_conditions.csv',index=False)
 z=pd.DataFrame(results);z['q_bh']=prior.bh(z.p);z['p_bonferroni']=(z.p*len(z)).clip(upper=1);z.to_csv(R/'correlations.csv',index=False);pd.DataFrame(dec).to_csv(R/'breadth_deciles.csv',index=False);y=pd.DataFrame(year);y['q_bh']=prior.bh(y.p);y.to_csv(R/'same_chromosome_years.csv',index=False)
 # Fit breadth filter using training completed trades only, choose among 5 MAs x 2 directions at median.
 decisions=[]
 for key,train in training.items():
  fold,system,cid=key;test=t[(t.fold==fold)&(t.system==system)&(t.chromosome_id==cid)];opts=[]
  for m in [10,20,50,100,200]:
   threshold=train[f'b{m}'].median()
   for direction in [-1,1]:
    keep=direction*(train[f'b{m}']-threshold)>=0
    if keep.sum()>=20:opts.append((train.loc[keep,'net_return'].mean(),m,direction,threshold))
  if not opts or test.empty:continue
  _,m,direction,threshold=max(opts);keep=direction*(test[f'b{m}']-threshold)>=0
  decisions.append(dict(fold=fold,system=system,chromosome_id=cid,ma=m,direction=direction,threshold=threshold,n=len(test),kept=int(keep.sum()),base_mean=test.net_return.mean(),kept_mean=test.loc[keep,'net_return'].mean(),skipped_mean=test.loc[~keep,'net_return'].mean(),base_pnl=test.pnl.sum(),kept_pnl=test.loc[keep,'pnl'].sum(),delta_mean=test.loc[keep,'net_return'].mean()-test.net_return.mean()))
 pd.DataFrame(decisions).to_csv(R/'decision_value.csv',index=False)
 for p in [P/'selection.csv',P/'ga8_trades.csv',Path(__file__),Path(meta['SPY']['path']),Path(meta['DEV79']['path']),Path('/opt/mts/ga6/data/ga6d_defensive_features.parquet')]:hashes[str(p)]=sha(p)
 (R/'metadata.json').write_text(json.dumps(dict(elapsed_seconds=time.monotonic()-start,pool=len(pool),selected_rows=len(chosen),selected_identities=chosen[['system','chromosome_id']].drop_duplicates().shape[0],trades=len(t),hashes=hashes,time_budget_minutes=20),indent=2));print(z[(z.feature=='b50')&~z.within_chromosome_year].to_string(index=False),flush=True)
if __name__=='__main__':main()
