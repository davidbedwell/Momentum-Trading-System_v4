from pathlib import Path
import json,gzip,hashlib,sys
import numpy as np
import pandas as pd
from scipy.stats import t as student
R=Path(__file__).resolve().parent
P=R.parent/'breadth_chromosome_entry_20261031'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(x,calendar):
 x=x.reindex(calendar); f=pd.DataFrame(index=calendar)
 for m in [10,20,50,100,200]:
  ma=x.rolling(m,min_periods=m).mean();ok=x.notna()&ma.notna();n=ok.sum(axis=1)
  b=(x.gt(ma)&ok).sum(axis=1).div(n.replace(0,np.nan)).where(n>=20);f[f'b{m}']=b;f[f'n{m}']=n
  for h in [5,10,21]:
   f[f'd{m}_{h}']=b.diff(h);f[f'v{m}_{h}']=b.diff(h)/h;f[f'a{m}_{h}']=(b-2*b.shift(h)+b.shift(2*h))/h**2
 f['feature_date']=f.index
 return f.shift(1)
def fit(g,feat,out,infer=True):
 x=g[feat]-g.groupby(['chromosome_id','year'])[feat].transform('mean');y=g[out]-g.groupby(['chromosome_id','year'])[out].transform('mean')
 sd=np.sqrt(np.mean(x*x));xx=np.dot(x,x)
 if xx<=1e-18:return None
 z=x.to_numpy()/sd; yy=y.to_numpy();b=np.dot(z,yy)/np.dot(z,z);e=yy-b*z
 scores=pd.Series(z*e,index=g.index).groupby(g.entry_date.dt.to_period('M')).sum();k=len(scores)
 se=np.sqrt(np.sum(scores**2)*k/max(k-1,1))/np.dot(z,z)
 p=2*student.sf(abs(b/se),k-1) if se>0 and k>=12 and len(g)>=30 else np.nan
 return dict(n=len(g),months=k,chromosomes=g.chromosome_id.nunique(),years=g.year.nunique(),within_sd=sd,effect=b,se=se,p=p,lo=b-student.ppf(.975,max(1,k-1))*se,hi=b+student.ppf(.975,max(1,k-1))*se)
def main():
 paths=[P/'selection.csv',P/'ledger_inventory.csv',R/'PROTOCOL.md']; hashes={str(p):sha(p) for p in paths}
 s=pd.read_csv(paths[0]);inv=pd.read_csv(paths[1]);s.to_csv(R/'selection_snapshot.csv',index=False)
 records=[];audit=[]
 lookup=inv.set_index(['system','chromosome_id'])
 for row in s.itertuples():
  key=(row.system,row.chromosome_id);found=key in lookup.index
  a=dict(system=row.system,chromosome_id=row.chromosome_id,family=row.group,identity_sample=row.identity_sample,retrospective_top=row.retrospective_top,ledger_present=found)
  if found:
   p=Path(lookup.loc[key,'path']);before=sha(p);d=json.load(gzip.open(p,'rt'));assert sha(p)==before
   a.update(path=str(p),sha256=before,trades=len(d['trades']))
   for tr in d['trades']:records.append(dict(**tr,system=row.system,chromosome_id=row.chromosome_id,family=row.group,identity_sample=row.identity_sample,retrospective_top=row.retrospective_top))
  audit.append(a)
 pd.DataFrame(audit).to_csv(R/'ledger_audit.csv',index=False)
 meta=json.loads((R.parent/'spy_state_predictor_20261031/run_metadata.json').read_text())['sources']
 for name in ['SPY','DEV79']:hashes[meta[name]['path']]=sha(meta[name]['path'])
 spy=pd.read_parquet(meta['SPY']['path']);cal=pd.DatetimeIndex(pd.to_datetime(spy.date).dt.tz_localize(None)).sort_values()
 d=pd.read_parquet(meta['DEV79']['path']);d['date']=pd.to_datetime(d.date).dt.tz_localize(None);x=d.pivot(index='date',columns='ticker',values='adj_close').sort_index()
 f=build(x,cal);f.index.name='entry_date';f.to_csv(R/'entry_features.csv')
 feats=[c for c in f if c.startswith(('b','d','a'))];t=pd.DataFrame(records);t['entry_date']=pd.to_datetime(t.entry_date);t['year']=t.entry_date.dt.year;t['win']=(t.pnl>0).astype(float)
 ga8path=P/'ga8_trades.csv'
 if ga8path.exists():
  hashes[str(ga8path)]=sha(ga8path);g=pd.read_csv(ga8path,usecols=['ticker','entry_date','exit_date','pnl','net_return','year','chromosome_id','family']);assert sha(ga8path)==hashes[str(ga8path)]
  g['entry_date']=pd.to_datetime(g.entry_date);g['system']='GA8';g['identity_sample']=False;g['retrospective_top']=True;g['r']=g.net_return;g['win']=(g.pnl>0).astype(float);t=pd.concat([t,g],ignore_index=True)
 t=t.join(f,on='entry_date');t['eligible']=t[feats].notna().all(axis=1);t.to_csv(R/'trades_with_features.csv.gz',index=False)
 t.groupby(['system','year','identity_sample','retrospective_top']).agg(n=('r','size'),eligible=('eligible','sum')).to_csv(R/'coverage.csv')
 results=[];hetero=[];loo=[]
 for aset in ['identity_sample','retrospective_top']:
  for system,u in t[t.eligible & t[aset]].groupby('system'):
   for feat in feats:
    for out in ['r','win']:
     tags=dict(analysis_set=aset,system=system,feature=feat,outcome=out);r=fit(u,feat,out)
     if r:results.append(dict(**tags,**r))
     for year in sorted(u.year.unique()):
      rr=fit(u[u.year.ne(year)],feat,out)
      if rr:loo.append(dict(**tags,excluded_year=int(year),**rr))
     for dims,label in [(['year'],'year'),(['family'],'family'),(['chromosome_id'],'chromosome')]:
      for key,g in u.groupby(dims):
       if len(g)<30:continue
       rr=fit(g,feat,out)
       if rr:hetero.append(dict(**tags,level=label,group=str(key[0]),**{k:v for k,v in rr.items() if k not in ['p','lo','hi','se']}))
 z=pd.DataFrame(results);valid=z.p.notna();p=z.loc[valid,'p'];order=np.argsort(p.to_numpy());ranked=p.to_numpy()[order];q=np.minimum.accumulate((ranked*len(p)/np.arange(1,len(p)+1))[::-1])[::-1];q0=np.empty(len(p));q0[order]=np.minimum(q,1);z.loc[valid,'q_bh']=q0;z['p_bonferroni']=(z.p*len(p)).clip(upper=1)
 z.to_csv(R/'pooled_results.csv',index=False);pd.DataFrame(hetero).to_csv(R/'heterogeneity.csv',index=False);pd.DataFrame(loo).to_csv(R/'leave_one_year_out.csv',index=False)
 hashes[str(R/'study.py')]=sha(__file__)
 (R/'run_metadata.json').write_text(json.dumps(dict(hashes=hashes,python=sys.version,pandas=pd.__version__,numpy=np.__version__,trades=len(t),eligible=int(t.eligible.sum()),features=feats,tests=len(z),finite_tests=int(valid.sum()),mae_available=any('mae' in c.lower() for c in t.columns)),indent=2))
 print(z.sort_values('q_bh').head(12).to_string(index=False),flush=True)
if __name__=='__main__':main()
