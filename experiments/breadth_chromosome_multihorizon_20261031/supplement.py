"""After the main run: synchronize finalized GA8 ledger and add close-path MAE proxy."""
import json
import numpy as np
import pandas as pd
from study import R,P,sha,fit
from scipy.stats import t as student
def describe(g,feat,out):
 xx=g[feat]-g.groupby(['chromosome_id','year'])[feat].transform('mean');yy=g[out]-g.groupby(['chromosome_id','year'])[out].transform('mean');den=np.dot(xx,xx)
 if den<=1e-18:return None
 sd=np.sqrt(den/len(g));return dict(n=len(g),months=g.entry_date.dt.to_period('M').nunique(),chromosomes=g.chromosome_id.nunique(),years=g.year.nunique(),within_sd=sd,effect=np.dot(xx,yy)/den*sd)
def describe_cached(g,feat,out):
 xx=rx.loc[g.index,feat].to_numpy();yy=ry.loc[g.index].to_numpy();den=np.dot(xx,xx)
 if den<=1e-18:return None
 sd=np.sqrt(den/len(g));return dict(n=len(g),months=g.entry_date.dt.to_period('M').nunique(),chromosomes=g.chromosome_id.nunique(),years=g.year.nunique(),within_sd=sd,effect=np.dot(xx,yy)/den*sd)
m=json.loads((R/'run_metadata.json').read_text());t=pd.read_csv(R/'trades_with_features.csv.gz',parse_dates=['entry_date','exit_date']);feats=m['features']
p=P/'ga8_trades.csv';before=sha(p);g=pd.read_csv(p,parse_dates=['entry_date','exit_date']);assert sha(p)==before
keys=['ticker','entry_date','exit_date','chromosome_id'];gg=g[keys+['pnl','net_return']];idx=t.system.eq('GA8');a=t.loc[idx,keys].merge(gg,on=keys,validate='one_to_one',how='left');assert a.net_return.notna().all();t.loc[idx,'r']=a.net_return.to_numpy();t.loc[idx,'pnl']=a.pnl.to_numpy();t.loc[idx,'net_return']=a.net_return.to_numpy();t['win']=(t.pnl>0).astype(float)
source=[k for k in m['hashes'] if k.endswith('dev80_raw_no_smci.parquet')][0];raw=pd.read_parquet(source);raw['date']=pd.to_datetime(raw.date).dt.tz_localize(None);x=raw.pivot(index='date',columns='ticker',values='adj_close').sort_index();dates=x.index
cache={};values={c:x[c].to_numpy() for c in x}
for row in t[['ticker','entry_date','exit_date']].drop_duplicates().itertuples(index=False):
 key=(row.ticker,row.entry_date,row.exit_date);lo=dates.searchsorted(row.entry_date);hi=dates.searchsorted(row.exit_date)
 v=values.get(row.ticker);ans=np.nan
 if v is not None and hi<len(dates) and lo<=hi and dates[lo]==row.entry_date and dates[hi]==row.exit_date:
  path=v[lo:hi+1]
  if np.isfinite(path).all() and (path>0).all():ans=float(np.min(path/path[0]-1))
 cache[key]=ans
t['close_mae_proxy']=[cache[k] for k in t[['ticker','entry_date','exit_date']].itertuples(index=False,name=None)];t.to_csv(R/'trades_with_features.csv.gz',index=False)
z=pd.read_csv(R/'pooled_results.csv');h=pd.read_csv(R/'heterogeneity.csv');l=pd.read_csv(R/'leave_one_year_out.csv');z=z[z.system.ne('GA8')&z.outcome.ne('close_mae_proxy')];h=h[h.system.ne('GA8')&h.outcome.ne('close_mae_proxy')];l=l[l.system.ne('GA8')&l.outcome.ne('close_mae_proxy')];res=[];het=[];loo=[]
for aset in ['identity_sample','retrospective_top']:
 for system,u in t[t.eligible&t[aset]].groupby('system'):
  outcomes=['r','win','close_mae_proxy'] if system=='GA8' else ['close_mae_proxy']
  for out in outcomes:
   v=u[u[out].notna()];rx=v[feats]-v.groupby(['chromosome_id','year'])[feats].transform('mean');ry=v[out]-v.groupby(['chromosome_id','year'])[out].transform('mean')
   for feat in feats:
    tags=dict(analysis_set=aset,system=system,feature=feat,outcome=out);rr=fit(v,feat,out)
    if rr:res.append(dict(**tags,**rr))
    for year in sorted(v.year.unique()):
     rr=describe_cached(v[v.year.ne(year)],feat,out)
     if rr:loo.append(dict(**tags,excluded_year=int(year),**rr))
    for dims,label in [(['year'],'year'),(['family'],'family'),(['chromosome_id'],'chromosome')]:
     for key,vg in v.groupby(dims):
      if len(vg)<30:continue
      rr=describe(vg,feat,out) if system=='GA8' and label=='family' else describe_cached(vg,feat,out)
      if rr:het.append(dict(**tags,level=label,group=str(key[0]),**{k:w for k,w in rr.items() if k not in ['p','se','lo','hi']}))
z=pd.concat([z,pd.DataFrame(res)],ignore_index=True);z=z.drop(columns=[c for c in z if c in ['q_bh','p_bonferroni','p_month_cluster','se_hac63','se_hac126','p_hac63','p_hac126']]);z['p_month_cluster']=2*student.sf(abs(z.effect/z.se),z.months-1);calendar=pd.read_csv(R/'entry_features.csv',usecols=['entry_date'],parse_dates=['entry_date']).entry_date
for i,row in z.iterrows():
 u=t[t.eligible&t[row.analysis_set]&t.system.eq(row.system)&t[row.outcome].notna()]
 xx=u[row.feature]-u.groupby(['chromosome_id','year'])[row.feature].transform('mean');yy=u[row.outcome]-u.groupby(['chromosome_id','year'])[row.outcome].transform('mean');sd=np.sqrt(np.mean(xx*xx));xx=xx/sd;den=np.dot(xx,xx)
 if not np.isfinite(den) or den<=0:continue
 residual=yy-row.effect*xx;scores=pd.Series((xx*residual).to_numpy(),index=u.entry_date).groupby(level=0).sum().reindex(pd.DatetimeIndex(calendar),fill_value=0);scores=scores.loc[u.entry_date.min():u.entry_date.max()].to_numpy()
 for lag in [63,126]:
  var=np.dot(scores,scores)
  for k in range(1,min(lag,len(scores)-1)+1):var+=2*(1-k/(lag+1))*np.dot(scores[k:],scores[:-k])
  se=np.sqrt(max(0,var))/den;pvalue=2*student.sf(abs(row.effect/se),max(1,row.months-1)) if se>0 else np.nan
  z.loc[i,'se_hac'+str(lag)]=se;z.loc[i,'p_hac'+str(lag)]=pvalue
# Conservative discovery requires all three dependence approximations to agree.
z['p']=z[['p_month_cluster','p_hac63','p_hac126']].max(axis=1,skipna=False);valid=z.p.notna();pvals=z.loc[valid,'p'].to_numpy();order=np.argsort(pvals);q=np.minimum.accumulate((pvals[order]*len(pvals)/np.arange(1,len(pvals)+1))[::-1])[::-1];q0=np.empty(len(q));q0[order]=np.minimum(q,1);z.loc[valid,'q_bh']=q0;z['p_bonferroni']=(z.p*len(pvals)).clip(upper=1);z.to_csv(R/'pooled_results.csv',index=False)
pd.concat([h,pd.DataFrame(het)],ignore_index=True).to_csv(R/'heterogeneity.csv',index=False);pd.concat([l,pd.DataFrame(loo)],ignore_index=True).to_csv(R/'leave_one_year_out.csv',index=False)
m['hashes'][str(P/'ga8_trades.csv')]=before;m['hashes'][str(P/'REPORT.md')]=sha(P/'REPORT.md');m['hashes'][str(R/'supplement.py')]=sha(__file__);m['tests']=len(z);m['finite_tests']=int(valid.sum());m['close_mae_proxy_missing']=int(t.close_mae_proxy.isna().sum());m['ga8_synchronized_to_final_report']=True;(R/'run_metadata.json').write_text(json.dumps(m,indent=2));print('Synchronized GA8; total tests',len(z),'proxy missing',m['close_mae_proxy_missing'])
