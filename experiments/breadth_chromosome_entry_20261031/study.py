"""Bounded archival study. Run with /opt/mts/.venv/bin/python study.py."""
from pathlib import Path
import sys,json,gzip,hashlib,sqlite3,os
import numpy as np
import pandas as pd
from scipy.stats import norm
ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'spy_state_predictor_20261031'
sys.path.insert(0,str(PRIOR))
import importlib.util
spec=importlib.util.spec_from_file_location('prior_study',PRIOR/'study.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
causal_features=prior.features;bh=prior.bh
BASE=Path('/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518')
COMMON=BASE/'ga6_ga7_common_v1_full_cohort_2009_2018'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regime(b):return np.where(pd.isna(b),'missing',np.where(b<.4,'weak',np.where(b>.6,'strong','medium')))
def inventory():
 rows=[];dbs=[]
 for family,base in [('GA6','/opt/mts/ga6'),('GA7','/opt/mts/ga7-deploy'),('GA8','/opt/mts/ga8')]:
  for parent,dirs,files in os.walk(base):
   dirs[:]=[d for d in dirs if d not in ['.git','.venv','__pycache__','node_modules']]
   for name in sorted(files):
    p=Path(parent)/name
    if p.suffix not in ['.csv','.json','.jsonl','.parquet','.sqlite','.gz']:continue
    row=dict(family=family,path=str(p),bytes=p.stat().st_size,kind=p.suffix)
    try:
     if p.suffix=='.sqlite':
      con=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
      for (t,) in con.execute("select name from sqlite_master where type='table'"):
       cols=[x[1] for x in con.execute('pragma table_info("'+t.replace('"','""')+'")')]
       n=con.execute('select count(*) from "'+t.replace('"','""')+'"').fetchone()[0]
       dbs.append(dict(family=family,path=str(p),table=t,rows=n,columns=json.dumps(cols)))
      con.close()
     elif p.suffix=='.csv':
      with p.open() as f:row['fields']=f.readline().strip()[:2500]
     elif p.suffix=='.parquet':
      import pyarrow.parquet as pq
      m=pq.read_metadata(p);row['rows']=m.num_rows;row['fields']=','.join(m.schema.names)
     elif p.suffix=='.jsonl':
      with p.open() as f: d=json.loads(f.readline())
      row['fields']=','.join(d) if isinstance(d,dict) else 'list'
     elif p.suffix=='.json' and p.stat().st_size<3000000:
      d=json.loads(p.read_text());row['fields']=','.join(d) if isinstance(d,dict) else 'list'
    except Exception as e:row['error']=str(e)[:150]
    rows.append(row)
 pd.DataFrame(rows).to_csv(ROOT/'file_inventory.csv',index=False)
 pd.DataFrame(dbs).to_csv(ROOT/'sqlite_inventory.csv',index=False)
 print('inventory',len(rows),len(dbs),flush=True)
def load_features():
 meta=json.loads((PRIOR/'run_metadata.json').read_text())['sources'];sp=meta['SPY']['path'];dp=meta['DEV79']['path']
 p=pd.read_parquet(sp);p['date']=pd.to_datetime(p.date).dt.tz_localize(None);p=p.set_index('date').adj_close.sort_index()
 d=pd.read_parquet(dp);d['date']=pd.to_datetime(d.date).dt.tz_localize(None);x=d.pivot(index='date',columns='ticker',values='adj_close')
 f=causal_features(p,{'DEV79':x});f['slope5']=f.DEV79_b50.diff(5);f['rv20']=p.pct_change().rolling(20).std()*np.sqrt(252)
 cross=(f.DEV79_b50>=.4)&(f.DEV79_b50.shift()<.4)
 f['since_cross40']=np.arange(len(f))-pd.Series(np.where(cross,np.arange(len(f)),np.nan),index=f.index).ffill()
 f['timing']=np.where(f.DEV79_b50<.4,np.where(f.slope5>0,'weak_improving','weak_not_improving'),np.where(f.since_cross40<=5,'crossed_0_5',np.where(f.since_cross40<=21,'crossed_6_21','other')))
 f['regime']=regime(f.DEV79_b50)
 for h in [5,21,63]:f['spy_forward'+str(h)]=p.shift(-h)/p-1
 # Entire entry feature vector is known at prior session close; future SPY returns start at entry close below.
 f['feature_date']=f.index; lag=f.shift(1);lag.index.name='entry_date'
 for h in [5,21,63]:lag['spy_forward'+str(h)]=f['spy_forward'+str(h)]
 lag.to_csv(ROOT/'entry_calendar.csv')
 sector=pd.read_parquet('/opt/mts/ga6/runs/independent_review/market_indicator_panel.parquet',columns=['ticker','sector_name']).dropna().drop_duplicates('ticker').set_index('ticker').sector_name
 (ROOT/'source_hashes.json').write_text(json.dumps({sp:sha(sp),dp:sha(dp),'prior_code':sha(PRIOR/'study.py')},indent=2))
 return lag,sector

def contrast(g,mask,other):
 a=g[mask].copy();b=g[other].copy()
 if len(a)<10 or len(b)<10:return None
 for v in [a,b]:
  if 'weight' not in v:v['weight']=1.
 ma=np.average(a.r,weights=a.weight);mb=np.average(b.r,weights=b.weight)
 a['inf']=a.weight*(a.r-ma)/a.weight.sum();b['inf']=-b.weight*(b.r-mb)/b.weight.sum()
 z=pd.concat([a,b]);calendar=pd.bdate_range(g.entry_date.min(),g.exit_date.max())
 scores=z.groupby('entry_date').inf.sum().reindex(calendar,fill_value=0).to_numpy()
 def se(lag):
  v=np.dot(scores,scores)
  for k in range(1,min(lag,len(scores)-1)+1):v+=2*(1-k/(lag+1))*np.dot(scores[k:],scores[:-k])
  return np.sqrt(max(v,0))
 delta=ma-mb;err=se(63);err126=se(126)
 return dict(n_a=len(a),n_b=len(b),months=z.entry_date.dt.to_period('M').nunique(),delta_r=delta,se=err,lo=delta-1.96*err,hi=delta+1.96*err,se126=err126,lo126=delta-1.96*err126,hi126=delta+1.96*err126,p=2*norm.sf(abs(delta/err)) if err else np.nan)

def main():
 inventory();f,sectors=load_features();summary=pd.read_csv(COMMON/'summary.csv');summary.to_csv(ROOT/'available_common_cohort.csv',index=False)
 # Fixed identity sample, independent of returns; all GA6 plus 20 GA7 identities per family.
 sample=summary[summary.system=='GA6'].copy()
 g7=summary[summary.system=='GA7'].sort_values('chromosome_id').groupby('group',group_keys=False).head(20)
 sample=pd.concat([sample,g7]);sample['analysis_set']='identity_sample'
 top7=pd.read_csv(COMMON/'GA7_top10_per_14_groups_common_v1.csv')
 top6=summary[summary.system=='GA6'].sort_values('cagr',ascending=False).head(10)
 tops=set(zip(pd.concat([top7,top6]).system,pd.concat([top7,top6]).chromosome_id))
 selected=pd.concat([sample,summary[[ (r.system,r.chromosome_id) in tops for r in summary.itertuples()]]]).drop_duplicates(['system','chromosome_id'])
 selected['identity_sample']=[(r.system,r.chromosome_id) in set(zip(sample.system,sample.chromosome_id)) for r in selected.itertuples()]
 selected['retrospective_top']=[(r.system,r.chromosome_id) in tops for r in selected.itertuples()];selected.to_csv(ROOT/'selection.csv',index=False)
 records=[];ledger_meta=[]
 for k,row in enumerate(selected.itertuples()):
  path=COMMON/'ledgers'/f'{row.system}_{row.chromosome_id}.json.gz'
  if not path.exists():continue
  d=json.load(gzip.open(path,'rt'));tr=d['trades'];nav=np.asarray(d['nav'],float)
  ledger_meta.append(dict(system=row.system,chromosome_id=row.chromosome_id,trades=len(tr),path=str(path),sha256=sha(path),nav_mdd=float(np.min(nav/np.maximum.accumulate(nav)-1))))
  for t in tr:records.append(dict(**t,system=row.system,chromosome_id=row.chromosome_id,family=row.group,identity_sample=row.identity_sample,retrospective_top=row.retrospective_top))
  if k%100==0:print('ledger',k,flush=True)
 pd.DataFrame(ledger_meta).to_csv(ROOT/'ledger_inventory.csv',index=False)
 t=pd.DataFrame(records);t['entry_date']=pd.to_datetime(t.entry_date);t['exit_date']=pd.to_datetime(t.exit_date)
 t=t.join(f,on='entry_date');t['year']=t.entry_date.dt.year;t['sector']=t.ticker.map(sectors).fillna('UNKNOWN');t['win']=(t.pnl>0).astype(float)
 t['hold_bin']=pd.cut(t.holding_sessions,[-1,5,20,40,10000],labels=False);t['momentum_bin']=(t.m63>0).astype(int);t['vol_bin']=pd.cut(t.rv20,[0,.15,.25,np.inf],labels=False)
 t.to_csv(ROOT/'trades.csv.gz',index=False)
 analyze(t)
 print('analysis complete',flush=True)
 (ROOT/'run_metadata.json').write_text(json.dumps(dict(python=sys.version, pandas=pd.__version__,numpy=np.__version__,study_sha256=sha(__file__),trades=len(t),selected=len(selected),sample=len(sample),entry_start=str(t.entry_date.min()),entry_end=str(t.entry_date.max())),indent=2))
def analyze(t):
 results=[]
 for aset in ['identity_sample','retrospective_top']:
  u=t[t[aset]&t.regime.ne('missing')]
  for dims,label in [(['system','regime'],'system'),(['system','year','regime'],'year'),(['system','family','regime'],'family'),(['system','chromosome_id','regime'],'chromosome'),(['system','timing'],'timing')]:
   z=u.groupby(dims,observed=True).agg(n=('r','size'),entry_dates=('entry_date','nunique'),mean_r=('r','mean'),median_r=('r','median'),win_rate=('win','mean'),pnl=('pnl','sum'),avg_hold=('holding_sessions','mean'),spy21=('spy_forward21','mean')).reset_index();z['analysis_set']=aset;z['level']=label;results.append(z)
 pd.concat(results).to_csv(ROOT/'regime_results.csv',index=False)
 tests=[];support=[]
 for aset in ['identity_sample','retrospective_top']:
  for system,u in t[t[aset]].groupby('system'):
   for kind in ['weak_vs_strong','weak_improving_vs_other_weak','cross_0_5_vs_weak']:
    if kind=='weak_vs_strong':a=u.regime.eq('weak');b=u.regime.eq('strong')
    elif kind=='weak_improving_vs_other_weak':a=u.timing.eq('weak_improving');b=u.timing.eq('weak_not_improving')
    else:a=u.timing.eq('crossed_0_5');b=u.regime.eq('weak')
    for matched in [False,True]:
     v=u[a|b].copy();v['arm']=a[a|b].astype(int)
     if matched:
      # Exact ticker controls sector more finely; realized horizon matching is descriptive, not executable.
      keys=['chromosome_id','ticker','year','hold_bin','momentum_bin','vol_bin']
      groups=v.groupby(keys,observed=True).arm.transform('nunique');v=v[groups==2].copy()
      # Equal-weight arms within cell, then trade-count-weighted cells.
      if len(v):
       v['weight']=1/v.groupby(keys+['arm'],observed=True).r.transform('size')
     support.append(dict(analysis_set=aset,system=system,test=kind,matched=matched,n=len(v),chromosomes=v.chromosome_id.nunique(),years=v.year.nunique()))
     result=contrast(v,v.arm.eq(1),v.arm.eq(0)) if len(v) else None
     if result:tests.append(dict(analysis_set=aset,system=system,test=kind,matched=matched,**result))
 out=pd.DataFrame(tests);out['q_bh']=bh(out.p);out.to_csv(ROOT/'contrasts.csv',index=False);pd.DataFrame(support).to_csv(ROOT/'match_support.csv',index=False)
if __name__=='__main__':main()
