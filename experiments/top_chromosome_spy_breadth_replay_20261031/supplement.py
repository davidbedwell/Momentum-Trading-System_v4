"""Additional fold, matched and filter uncertainty; inference remains exploratory."""
import study
import pandas as pd
import numpy as np
from scipy.stats import norm,spearmanr,pearsonr
R=study.R
def delta(g,weights):
 mu=np.sum(g.net_return*weights);s=pd.Series(weights*(g.net_return-mu),index=g.index).groupby(g.entry_date).sum().reindex(pd.bdate_range(g.entry_date.min(),g.exit_date.max()),fill_value=0).to_numpy()
 # weights sum zero: center separately by arm to obtain the difference-of-means influence
 return mu,s
def estimate(g,w):
 pos=w>0;neg=w<0;ma=np.sum(g.net_return[pos]*w[pos])/w[pos].sum();mb=np.sum(g.net_return[neg]*(-w[neg]))/(-w[neg]).sum();d=ma-mb
 inf=w*np.where(pos,g.net_return-ma,g.net_return-mb);s=pd.Series(inf,index=g.index).groupby(g.entry_date).sum().reindex(pd.bdate_range(g.entry_date.min(),g.exit_date.max()),fill_value=0).to_numpy()
 def se(lag):
  v=np.dot(s,s)
  for k in range(1,min(lag,len(s)-1)+1):v+=2*(1-k/(lag+1))*np.dot(s[k:],s[:-k])
  return np.sqrt(max(0,v))
 e=se(63);valid=len(g)>=30 and g.entry_date.nunique()>=20;return dict(delta=d,se=e if valid else np.nan,lo=d-1.96*e if valid else np.nan,hi=d+1.96*e if valid else np.nan,se126=se(126) if valid else np.nan,p=2*norm.sf(abs(d/e)) if e and valid else np.nan)
def main():
 t=pd.read_csv(R/'trades.csv.gz',parse_dates=['entry_date','exit_date','feature_date']);fold=[];matched=[]
 dec=[]
 for system,u in t.groupby('system'):
  for m in [10,20,50,100,200]:
   v=u.copy();v['quantile_decile']=pd.qcut(v[f'b{m}'],10,duplicates='drop');z=v.groupby('quantile_decile',observed=True).agg(n=('net_return','size'),dates=('entry_date','nunique'),breadth_min=(f'b{m}','min'),breadth_max=(f'b{m}','max'),mean_return=('net_return','mean'),win_rate=('win','mean')).reset_index();z['system']=system;z['ma']=m;dec.extend(z.to_dict('records'))
 pd.DataFrame(dec).to_csv(R/'quantile_deciles.csv',index=False)
 t.groupby(['system','fold','year']).agg(n=('net_return','size'),dates=('entry_date','nunique'),mean_return=('net_return','mean'),win_rate=('win','mean'),pnl=('pnl','sum'),mean_mae=('mae_return','mean')).to_csv(R/'fold_outcomes.csv')
 for (system,fo),g in t.groupby(['system','fold']):
  for method in ['pearson','spearman']:
   z=study.corr(g,'b50',method)
   if z:fold.append(dict(system=system,fold=fo,method=method,**z))
 for system,u in t.groupby('system'):
  v=u.dropna(subset=['b50','momentum_bin','vol_bin']).copy();v=v[(v.b50<.4)|(v.b50>.6)];v['arm']=(v.b50<.4).astype(int);keys=['chromosome_id','ticker','year','momentum_bin','vol_bin'];v=v[v.groupby(keys).arm.transform('nunique')==2].copy()
  if len(v):
   v['cell_n']=v.groupby(keys+['arm']).net_return.transform('size');nc=v.groupby(keys).ngroups;w=np.where(v.arm==1,1,-1)/v.cell_n/nc
   matched.append(dict(system=system,n=len(v),cells=nc,**estimate(v,w)))
 z=pd.DataFrame(matched);z['q_bh']=study.prior.bh(z.p);z.to_csv(R/'matched_conditions.csv',index=False)
 z=pd.DataFrame(fold);z['q_bh']=study.prior.bh(z.p);z.to_csv(R/'fold_correlations.csv',index=False)
 # Three-month moving block bootstrap; all trades sharing a date stay together.
 rng=np.random.default_rng(20261101);boot=[]
 for system,u in t.groupby('system'):
  periods=pd.period_range(u.entry_date.min().to_period('M'),u.entry_date.max().to_period('M'),freq='M');groups=[u[u.entry_date.dt.to_period('M')==m] for m in periods];vals=[]
  for b in range(400):
   starts=rng.integers(0,len(groups),size=int(np.ceil(len(groups)/3)));ix=[(a+j)%len(groups) for a in starts for j in range(3)][:len(groups)];g=pd.concat([groups[i] for i in ix]);g=g.dropna(subset=['b50','net_return'])
   if len(g)>10 and g.b50.nunique()>1:vals.append((pearsonr(g.b50,g.net_return).statistic,spearmanr(g.b50,g.net_return).statistic))
  for j,method in enumerate(['pearson','spearman']):
   a=np.array(vals)[:,j];boot.append(dict(system=system,feature='b50',method=method,replicates=len(a),lo=np.quantile(a,.025),hi=np.quantile(a,.975)))
 pd.DataFrame(boot).to_csv(R/'block_bootstrap.csv',index=False)
 d=pd.read_csv(R/'decision_value.csv');parts=[]
 for row in d.itertuples():
  g=t[(t.system==row.system)&(t.chromosome_id==row.chromosome_id)&(t.fold==row.fold)].copy();g['keep']=row.direction*(g[f'b{row.ma}']-row.threshold)>=0;parts.append(g)
 u=pd.concat(parts);out=[]
 for system,g in u.groupby('system'):
  # Kept versus skipped, a disjoint comparison; does not simulate altered cash/capacity.
  w=np.where(g.keep,1/g.keep.sum(),-1/(~g.keep).sum());out.append(dict(system=system,n=len(g),kept=int(g.keep.sum()),skipped=int((~g.keep).sum()),base_mean=g.net_return.mean(),kept_mean=g.loc[g.keep,'net_return'].mean(),base_pnl=g.pnl.sum(),kept_pnl=g.loc[g.keep,'pnl'].sum(),**estimate(g,w)))
 z=pd.DataFrame(out);z['q_bh']=study.prior.bh(z.p);z.to_csv(R/'decision_summary.csv',index=False)
if __name__=='__main__':main()
