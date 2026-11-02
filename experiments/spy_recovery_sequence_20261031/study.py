"""Bounded causal ordered recovery experiment. See PROTOCOL.md."""
from pathlib import Path
import importlib.util, json, hashlib, platform
import numpy as np
import pandas as pd
from scipy.stats import norm
ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'spy_state_predictor_20261031/study.py'
spec=importlib.util.spec_from_file_location('prior_sequence',PRIOR)
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
STAGES=['damage','breadth','confirmed']
METRICS=['return','downside','drawdown']

def features(p,x):
    f=prior.features(p,{'DEV79':x})
    ema=p.ewm(span=20,adjust=False,min_periods=20).mean()
    f['dd']=p/p.rolling(252).max()-1
    f['rv']=p.pct_change(fill_method=None).rolling(20).std()*np.sqrt(252)
    f['rv_change']=f.rv-f.rv.shift(5)
    f['b']=f.DEV79_b50;f['bmean']=f.b.rolling(5).mean()
    f['ret5']=p/p.shift(5)-1;f['ema_slope']=ema/ema.shift(5)-1
    f['above_count']=(p>ema).astype(float).where(p.notna()&ema.notna()).rolling(5).sum()
    return f[['dd','rv','rv_change','b','bmean','ret5','ema_slope','above_count','m63']]

def machine(f,wait_damage=63,wait_breadth=21,retention=21,damage_cut=-.10):
    """Single pass; no access to outcomes, suffixes, future minima or episode success."""
    state=0;armed=True;eid=0;start=bt=ct=None;anchor=np.nan
    records=[];ledger=[]
    for i,(date,r) in enumerate(f.iterrows()):
        pulse=0;reason='';old=state
        if not np.isfinite(r.to_numpy(dtype=float)).all():
            if state: ledger.append(dict(date=date,episode=eid,from_state=state,to_state=0,reason='missing_abort'))
            state=0;armed=False
            records.append(dict(state=np.nan,episode=np.nan,damage_date=pd.NaT,breadth_date=pd.NaT,confirmation_date=pd.NaT,anchor_breadth=np.nan,pulse=np.nan))
            continue
        gate=r.dd<=damage_cut and r.b<.4
        if state and (i-start>126 or (state==1 and i-start>wait_damage) or (state==2 and i-bt>wait_breadth) or (state==3 and i-ct>=retention)):
            state=0;reason='expiry';armed=False
        elif state==1 and i>start and r.b>=anchor+.10 and r.bmean>=.40:
            state=2;bt=i;pulse=2;reason='breadth_recovery'
        elif state==2 and i>bt and r.above_count>=4 and r.ret5>0 and r.ema_slope>0 and r.rv_change<=0:
            state=3;ct=i;pulse=3;reason='price_confirmation'
        elif state==0:
            if not gate:armed=True
            elif armed:
                eid+=1;state=1;start=i;bt=ct=None;anchor=r.b;armed=False;pulse=1;reason='damage_declaration'
        if state!=old:ledger.append(dict(date=date,episode=eid,from_state=old,to_state=state,reason=reason))
        records.append(dict(state=state,episode=eid if state else np.nan,damage_date=f.index[start] if state else pd.NaT,breadth_date=f.index[bt] if state and bt is not None else pd.NaT,confirmation_date=f.index[ct] if state and ct is not None else pd.NaT,anchor_breadth=anchor if state else np.nan,pulse=pulse))
    d=pd.DataFrame(records,index=f.index)
    for col in ['state','episode','anchor_breadth','pulse']:d[col]=d[col].astype(float)
    for col in ['damage_date','breadth_date','confirmation_date']:d[col]=pd.to_datetime(d[col]).astype('datetime64[ns]')
    s=pd.DataFrame(index=f.index)
    for k,name in enumerate(STAGES,1):
        s[name]=d.state.eq(k).astype(float).where(d.state.notna())
        s[name+'_pulse']=d.pulse.eq(k).astype(float).where(d.state.notna())
    s['weak']=(f.b<.4).astype(float).where(d.state.notna())
    s['momentum']=(f.m63>0).astype(float).where(d.state.notna())
    s['unordered']=((f.dd<=damage_cut)&(f.bmean>=.4)&(f.b.diff(21)>=.1)&(f.above_count>=4)&(f.ret5>0)&(f.ema_slope>0)&(f.rv_change<=0)).astype(float).where(d.state.notna()&f.b.shift(21).notna())
    return s,d,pd.DataFrame(ledger)

def adjust(d):
    d=d.copy();d['q']=prior.bh(d.p);d['bonferroni']=np.minimum(1,d.p*d.p.notna().sum());return d

def period(index,h,year=None,omit=()):
    ep=pd.Series(index,index=index).shift(-h)
    out=(index.year>=2006)&(index.year<=2025)&(ep.dt.year.to_numpy()==index.year)&~index.year.isin(omit)
    return out if year is None else out&(index.year==year)

def strata(f):
    dd=pd.cut(f.dd,[-np.inf,-.2,-.1,-.05,0,np.inf],labels=False)
    rv=pd.cut(f.rv,[-np.inf,.2,.35,np.inf],labels=False)
    return pd.Series(f.index.year.astype(str),index=f.index)+'|'+dd.astype(str)+'|'+rv.astype(str)

def match(a,b,key):
    """Exact strata with replacement, weights sum to target n in support."""
    a=a.copy();w=np.zeros(len(a));kk=np.asarray(key)
    for k in np.unique(kk[a]):
        aa=a&(kk==k);bb=b&(kk==k)
        if bb.sum():w[bb]=aa.sum()/bb.sum()
        else:a[aa]=False
    return a,w

def weighted_estimate(y,a,w,lag):
    y=np.asarray(y,float);a=np.asarray(a,bool)&np.isfinite(y);w=np.where(np.isfinite(y),w,0)
    if a.sum()<5 or (w>0).sum()<5:return (np.nan,)*5
    if np.array_equal(w/w.sum(),a.astype(float)/a.sum()):return 0.,0.,0.,0.,np.nan
    ma=y[a].mean();mb=np.nansum(w*y)/w.sum();n=len(y)
    z=np.zeros(n);z[a]+=(y[a]-ma)*n/a.sum()
    ids=w>0;z[ids]-=w[ids]*(y[ids]-mb)*n/w.sum()
    v=z@z
    for k in range(1,min(lag,n-1)+1):v+=2*(1-k/(lag+1))*(z[k:]@z[:-k])
    se=np.sqrt(max(v,0))/n;e=ma-mb
    return e,e-1.96*se,e+1.96*se,se,2*norm.sf(abs(e/se)) if se else np.nan

def evaluate(s,f,ys,year=None,omit=(),lag_override=None):
    rows=[];key=strata(f)
    for h,y in ys.items():
      window=period(s.index,h,year,omit)
      for mode in ['occupancy','pulse']:
       for j,stage in enumerate(STAGES):
        rule=stage if mode=='occupancy' else stage+'_pulse'
        prev='unconditional' if j==0 else STAGES[j-1]+('_pulse' if mode=='pulse' else '')
        for comp in dict.fromkeys([prev,'weak','momentum','unconditional','matched_damage','unordered']):
          valid=window&s[rule].notna().to_numpy()
          if comp not in ['unconditional','matched_damage']:valid &=s[comp].notna().to_numpy()
          a=valid&s[rule].eq(1).to_numpy();original_n=int(a.sum())
          if comp=='matched_damage':
              # Occupancy controls for both pulse and occupancy targets.
              a,w=match(a,valid&s.damage.eq(1).to_numpy(),key);b=w>0
          else:
              b=valid if comp=='unconditional' else valid&s[comp].eq(1).to_numpy();w=b.astype(float)
          on,non=prior.counts(a,h);bon,bnon=prior.counts(b,h)
          for metric in METRICS:
            val=y[metric].to_numpy();lag=lag_override or max(63,2*h)
            e=weighted_estimate(val,a,w,lag)
            rows.append(dict(year=year or 'pooled',mode=mode,stage=stage,comparator=comp,horizon=h,metric=metric,n=int(a.sum()),unmatched_n=original_n-int(a.sum()),baseline_n=int(b.sum()),baseline_effective_n=w.sum()**2/(w@w) if w.sum() else 0,onsets=on,nonoverlap_n=non,baseline_onsets=bon,baseline_nonoverlap_n=bnon,fragile=min(on,non,bon,bnon)<20,mean=float(np.mean(val[a])) if a.any() else np.nan,baseline_mean=float(np.nansum(w*val)/w.sum()) if w.sum() else np.nan,effect=e[0],ci_low=e[1],ci_high=e[2],se=e[3],p=e[4]))
    return pd.DataFrame(rows)

def bootstrap(s,ys,reps=1000):
    rng=np.random.default_rng(20261031);rows=[];n=len(s)
    # Paired circular calendar block resampling; gaps retained via eligibility masks.
    for h,y in ys.items():
      valid=period(s.index,h)&s[STAGES+['weak']].notna().all(axis=1).to_numpy()
      for block in [63,126]:
        ii=(rng.integers(0,n,size=(reps,int(np.ceil(n/block))))[:,:,None]+np.arange(block)[None,None,:])%n
        ii=ii.reshape(reps,-1)[:,:n]
        for stage,prev in [('breadth','damage'),('confirmed','breadth')]:
          a=valid&s[stage].eq(1).to_numpy()
          for comp in [prev,'weak','unconditional']:
            b=valid if comp=='unconditional' else valid&s[comp].eq(1).to_numpy()
            for metric in METRICS:
              v=y[metric].to_numpy();aa=a[ii];bb=b[ii];vals=v[ii]
              na=aa.sum(1);nb=bb.sum(1);ok=(na>=5)&(nb>=5)
              av=np.nansum(np.where(aa,vals,0),axis=1)/np.maximum(na,1)
              bv=np.nansum(np.where(bb,vals,0),axis=1)/np.maximum(nb,1)
              effects=(av-bv)[ok];lo,hi=np.quantile(effects,[.025,.975]) if len(effects) else [np.nan,np.nan]
              rows.append(dict(stage=stage,comparator=comp,horizon=h,metric=metric,block=block,replicates=reps,valid_replicates=int(ok.sum()),ci_low=lo,ci_high=hi))
    return pd.DataFrame(rows)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    meta={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':__import__('scipy').__version__,'sources':{}}
    data={}
    for name in ['SPY','DEV79']:
        path=prior.SOURCES[name];d=pd.read_parquet(path);d.date=pd.to_datetime(d.date).dt.tz_localize(None)
        assert not d.duplicated(['date'] if name=='SPY' else ['date','ticker']).any()
        meta['sources'][name]=dict(path=path,sha256=sha(path),rows=len(d),start=str(d.date.min()),end=str(d.date.max()))
        data[name]=d
    p=data['SPY'].set_index('date').adj_close.sort_index().loc[:'2025-12-31']
    x=data['DEV79'].pivot(index='date',columns='ticker',values='adj_close').sort_index().loc[:'2025-12-31']
    assert p.notna().all() and (p>0).all() and (x.stack().dropna()>0).all()
    f=features(p,x);s,d,ledger=machine(f)
    f.to_csv(ROOT/'features.csv');s.to_csv(ROOT/'signals.csv');d.to_csv(ROOT/'state_history.csv');ledger.to_csv(ROOT/'transitions.csv',index=False)
    ys={h:prior.outcomes(p,h) for h in [21,63]};pd.concat(ys,axis=1).to_csv(ROOT/'outcomes.csv')
    result=adjust(evaluate(s,f,ys));result.to_csv(ROOT/'results.csv',index=False)
    annual=adjust(pd.concat([evaluate(s,f,ys,year=y) for y in range(2006,2026)],ignore_index=True));annual.to_csv(ROOT/'annual_results.csv',index=False)
    variants={'wait42_10':machine(f,42,10)[0],'wait84_42':machine(f,84,42)[0],'retention10':machine(f,retention=10)[0],'retention42':machine(f,retention=42)[0],'damage15':machine(f,damage_cut=-.15)[0],'delay1':s.shift(1)}
    robust=[]
    for label,ss in variants.items():
        z=evaluate(ss,f.shift(1) if label=='delay1' else f,ys);z['variant']=label;robust.append(z)
    for label,omits in [('omit_crises',[2008,2009,2020,2022])]+[(f'omit_{y}',[y]) for y in range(2006,2026)]:
        z=evaluate(s,f,ys,omit=omits);z['variant']=label;robust.append(z)
    z=evaluate(s,f,ys,lag_override=126);z['variant']='lag126';robust.append(z)
    adjust(pd.concat(robust,ignore_index=True)).to_csv(ROOT/'robustness.csv',index=False)
    bootstrap(s,ys).to_csv(ROOT/'bootstrap.csv',index=False)
    support=[]
    for h in ys:
      valid=period(s.index,h)&s.damage.notna().to_numpy()
      for mode in ['occupancy','pulse']:
       for stage in STAGES:
        a=valid&s[stage+('_pulse' if mode=='pulse' else '')].eq(1).to_numpy()
        aa,w=match(a,valid&s.damage.eq(1).to_numpy(),strata(f))
        for i in np.flatnonzero(a|(w>0)):
          support.append(dict(date=s.index[i],horizon=h,mode=mode,stage=stage,stratum=strata(f).iloc[i],target=bool(a[i]),target_in_support=bool(aa[i]),control_weight=w[i]))
    pd.DataFrame(support).to_csv(ROOT/'match_support.csv',index=False)
    quality=[]
    for name,v in [('SPY',p.to_frame()),('DEV79',x)]:
        quality.append(dict(source=name,dates=len(v),columns=v.shape[1],missing_cells=int(v.isna().sum().sum()),min_price=float(v.min().min()),max_abs_daily_move=float(v.pct_change(fill_method=None).abs().max().max())))
    pd.DataFrame(quality).to_csv(ROOT/'data_quality.csv',index=False)
    paths=[ROOT/'PROTOCOL.md',ROOT/'SOURCES.md',ROOT/'study.py',ROOT/'test_study.py',ROOT/'report.py',PRIOR]+list((ROOT.parent/'spy_r1_combinations_20261031').glob('*.md'))
    frozen=Path('/opt/mts/ga7-deploy/Momentum-Trading-System_v4-research-ga7-dev79/Research/Protocols')
    paths += [frozen/n for n in ['MTS_R1_MULTI_RECOVERY_MORPHOLOGY_COMPARISON_FREEZE_20261004.json','MTS_TRUE_RECOVERY_EMERGENCE_DESCRIPTOR_DISCOVERY_FREEZE_20261004.json','MTS_REENTRY_CAUSAL_STATE_MACHINE_FREEZE_20261004.json']]
    meta['hashes']={str(q):sha(q) for q in paths};meta['finite_pooled_tests']=int(result.p.notna().sum());meta['finite_annual_tests']=int(annual.p.notna().sum());meta['sessions']=len(p);meta['breadth_min_required']=20
    (ROOT/'run_metadata.json').write_text(json.dumps(meta,indent=2))
    print(result.query("mode=='occupancy' and metric=='return'").to_string(index=False))
if __name__=='__main__':main()
