"""Causal exploratory follow-up. Run with /opt/mts/.venv/bin/python."""
from pathlib import Path
import sys, json, hashlib, itertools, importlib.util
import numpy as np
import pandas as pd
from scipy.stats import norm
ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'spy_state_predictor_20261031/study.py'
spec=importlib.util.spec_from_file_location('prior',PRIOR); prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
H=[5,10,21,63]

def build(p,x,weak=.4):
    f=prior.features(p,{'DEV79':x});r=p.pct_change(fill_method=None)
    ema=p.ewm(span=20,adjust=False,min_periods=20).mean()
    f['price_persistence']=(p>ema).astype(float).where(ema.notna()).rolling(5).sum()
    f['ret5']=p/p.shift(5)-1;f['rv20']=r.rolling(20).std()
    f['rv20_change5']=f.rv20-f.rv20.shift(5)
    f['recent_damage']=(p/p.rolling(252).max()-1).rolling(63).min()
    xx=x.reindex(p.index);valid=xx.notna()&xx.shift(20).notna()&xx.rolling(21).count().eq(21)
    n=valid.sum(axis=1);f['bpos20']=((xx>xx.shift(20))&valid).sum(axis=1).div(n).where(n>=20)
    f['bpos_velocity']=f.bpos20.diff(5);f['bpos_persistence']=f.bpos20.rolling(5).mean()
    f['ema_gap']=p/ema-1;f['ema_slope']=ema/ema.shift(5)-1
    definitions={
      'weak':(['DEV79_b50'],f.DEV79_b50<weak),
      'improving':(['DEV79_db'],f.DEV79_db>.1),
      'persistence':(['price_persistence','ret5'],(f.price_persistence>=4)&(f.ret5>0)),
      'stabilization':(['rv20_change5'],f.rv20_change5<=0),
      'momentum':(['m63'],f.m63>0),
      'R1_proxy':(['recent_damage','ret5','bpos_velocity','bpos_persistence','ema_gap','ema_slope'],(f.recent_damage<=-.15)&(f.ret5>0)&(f.bpos_velocity>.1)&(f.bpos_persistence>.5)&(f.ema_gap>0)&(f.ema_slope>0))}
    s=pd.DataFrame({k:v.astype(float).where(f[c].notna().all(axis=1)) for k,(c,v) in definitions.items()})
    components={k:[k] for k in s}
    combos=list(itertools.combinations(list(s),2))+[('weak',*v) for v in itertools.combinations(['improving','persistence','stabilization','momentum'],2)]+[('R1_proxy','persistence','stabilization')]
    for c in combos:
        k='&'.join(c);s[k]=s[list(c)].eq(1).all(axis=1).astype(float).where(s[list(c)].notna().all(axis=1));components[k]=list(c)
    return f,s,components

def period(index,h,year=None):
    ep=pd.Series(index,index=index).shift(-h)
    mask=(index.year>=2012)&(index.year<=2025)&(ep.dt.year.to_numpy()==index.year)
    return mask if year is None else mask&(index.year==year)

def adjust(df):
    df['q']=prior.bh(df.p);df['bonferroni']=np.minimum(1,df.p*df.p.notna().sum());return df

def evaluate(s,ys,components,year=None,lag=None):
    rows=[]
    for h,y in ys.items():
      window=period(s.index,h,year)
      for rule,c in components.items():
        comps=list(dict.fromkeys(['unconditional','momentum']+(c if len(c)>1 else [])))
        for comp in comps:
          valid=window&s[rule].notna().to_numpy()
          if comp!='unconditional':valid &=s[comp].notna().to_numpy()
          a=valid&s[rule].eq(1).to_numpy();b=valid if comp=='unconditional' else valid&s[comp].eq(1).to_numpy()
          on,non=prior.counts(a,h)
          for metric in ['return','drawdown','downside']:
            val=y[metric].to_numpy();e=prior.estimate(val,a,b,lag=lag or max(63,2*h))
            rows.append(dict(year=year or 'pooled',rule=rule,comparator=comp,horizon=h,metric=metric,n=int(a.sum()),baseline_n=int(b.sum()),onsets=on,nonoverlap_n=non,fragile=on<20 or non<20,mean=np.mean(val[a]) if a.any() else np.nan,baseline_mean=np.mean(val[b]) if b.any() else np.nan,effect=e[0],ci_low=e[1],ci_high=e[2],se=e[3],p=e[4]))
    return pd.DataFrame(rows)

def interactions(s,ys):
    rows=[]
    for a,b in itertools.combinations(['weak','improving','persistence','stabilization','momentum','R1_proxy'],2):
      for h,y in ys.items():
        valid=period(s.index,h)&s[[a,b]].notna().all(axis=1).to_numpy()
        cells=[valid&s[a].eq(i).to_numpy()&s[b].eq(j).to_numpy() for i,j in [(1,1),(1,0),(0,1),(0,0)]]
        for metric in ['return','drawdown','downside']:
          val=y[metric].to_numpy();counts=[int(c.sum()) for c in cells];e=se=pv=np.nan
          if min(counts)>=5:
            influence=np.zeros(len(s));e=0
            for c,sign in zip(cells,[1,-1,-1,1]):
              mu=val[c].mean();e+=sign*mu;influence[c]+=sign*(val[c]-mu)*len(s)/c.sum()
            lag=max(63,2*h);lrv=influence@influence
            for k in range(1,lag+1):lrv+=2*(1-k/(lag+1))*(influence[k:]@influence[:-k])
            se=np.sqrt(max(lrv,0))/len(s);pv=2*norm.sf(abs(e/se)) if se>0 else np.nan
          rows.append(dict(pair=a+'&'+b,horizon=h,metric=metric,cell_counts=str(counts),effect=e,ci_low=e-1.96*se,ci_high=e+1.96*se,p=pv))
    return adjust(pd.DataFrame(rows))

def main():
    meta={'sources':{},'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),'prior_code_sha256':hashlib.sha256(PRIOR.read_bytes()).hexdigest()}
    panels={}
    for name,path in prior.SOURCES.items():
      try:
        d=pd.read_parquet(path);d['date']=pd.to_datetime(d.date).dt.tz_localize(None)
        meta['sources'][name]={'path':path,'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'rows':len(d),'end':str(d.date.max())}
        if name=='SPY':
          assert not d.date.duplicated().any();p=d.set_index('date').adj_close.sort_index().loc[:'2025-12-31']
        else:
          assert not d.duplicated(['date','ticker']).any();panels[name]=d.pivot(index='date',columns='ticker',values='adj_close').sort_index().loc[:'2025-12-31']
      except (PermissionError,FileNotFoundError) as e:meta['sources'][name]={'path':path,'unavailable':str(e)}
    x=panels['DEV79'];assert (p>0).all() and p.notna().all();assert (x.stack().dropna()>0).all()
    f,s,c=build(p,x);f.to_csv(ROOT/'features.csv');s.to_csv(ROOT/'signals.csv')
    ys={h:prior.outcomes(p,h) for h in H};pd.concat(ys,axis=1).to_csv(ROOT/'outcomes.csv')
    result=adjust(evaluate(s,ys,c));result.to_csv(ROOT/'results.csv',index=False)
    annual=adjust(pd.concat([evaluate(s,ys,c,year=yr) for yr in range(2012,2026)],ignore_index=True));annual.to_csv(ROOT/'annual_results.csv',index=False)
    interactions(s,ys).to_csv(ROOT/'interactions.csv',index=False)
    selections=[];chosen=pd.Series(np.nan,index=p.index)
    ep=pd.Series(p.index,index=p.index).shift(-21)
    for yr in range(2012,2026):
      train=(p.index.year>=2006)&(p.index.year<yr)&(ep<pd.Timestamp(f'{yr}-01-01')).to_numpy()
      candidates=[]
      for rule,parts in c.items():
        if len(parts)<2:continue
        valid=train&s[rule].notna().to_numpy();a=valid&s[rule].eq(1).to_numpy();on,non=prior.counts(a,21)
        if a.sum()>=100 and on>=15:
          e=prior.estimate(ys[21]['return'],a,valid)[0]
          if e>0:candidates.append((e,rule,int(a.sum()),on))
      pick=sorted(candidates,key=lambda z:(-z[0],z[1]))[0] if candidates else None
      test=p.index.year==yr;chosen.loc[test]=s.loc[test,pick[1]] if pick else 0
      selections.append(dict(year=yr,rule=pick[1] if pick else 'none',training_effect=pick[0] if pick else np.nan,training_n=pick[2] if pick else 0,training_onsets=pick[3] if pick else 0))
    pd.DataFrame(selections).to_csv(ROOT/'rolling_selections.csv',index=False)
    ss=s.copy();ss['rolling_selected']=chosen
    roll=adjust(evaluate(ss,ys,{'rolling_selected':['rolling_selected']}));roll.to_csv(ROOT/'rolling_results.csv',index=False)
    chosen.to_csv(ROOT/'rolling_signals.csv')
    sens=[]
    variants={'lag126':(s,126),'delay1':(s.shift(1),None),'weak35':(build(p,x,.35)[1],None),'weak45':(build(p,x,.45)[1],None),'exclude_crisis':(s.where(pd.Series(~s.index.year.isin([2008,2009,2020,2022]),index=s.index),axis=0),None)}
    for label,(signals,lag) in variants.items():
      z=evaluate(signals,ys,c,lag=lag);z['variant']=label;sens.append(z)
    for yr in range(2012,2026):
      z=evaluate(s.where(pd.Series(s.index.year!=yr,index=s.index),axis=0),ys,c);z['variant']=f'omit_{yr}';sens.append(z)
    adjust(pd.concat(sens,ignore_index=True)).to_csv(ROOT/'robustness.csv',index=False)
    if 'DEV87' in panels:
      _,s87,c87=build(p,panels['DEV87']);adjust(evaluate(s87,ys,c87)).to_csv(ROOT/'dev87_results.csv',index=False)
    pd.DataFrame([dict(source=k,dates=len(v),tickers=v.shape[1],missing_cells=int(v.isna().sum().sum()),max_abs_daily_move=float(v.pct_change(fill_method=None).abs().max().max())) for k,v in panels.items()]).to_csv(ROOT/'data_quality.csv',index=False)
    meta['rule_count']=len(c);meta['finite_pooled_tests']=int(result.p.notna().sum());meta['finite_annual_tests']=int(annual.p.notna().sum());meta['components']=c
    (ROOT/'run_metadata.json').write_text(json.dumps(meta,indent=2))
    print(result.query("horizon==21 and metric=='return' and comparator=='unconditional'").sort_values('effect',ascending=False).to_string(index=False))
    print('ROLLING');print(roll.to_string(index=False))
if __name__=='__main__':main()
