"""Selected archival fills: risk proxies only; no counterfactual performance."""
from pathlib import Path
import json,gzip,hashlib,collections
import numpy as np
import pandas as pd
from scipy.stats import norm
R=Path(__file__).resolve().parent
P=R.parent/'top_chromosome_spy_breadth_replay_20261031'
BAR=Path('/opt/mts/ga6/data/ga6d_defensive_features.parquet')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cycle_risk(events,bars):
    """Fill marks, legacy post-fill low, all-exposed-state low scenario envelope.
    Envelope may mark a stopped holding below its modeled stop: conservative
    daily-low scenario, not realizable intraday MAE or a certified bound.
    """
    q=cost=net=div=0.; fill=post=envelope=0.; adds=reductions=stops=0
    by=collections.defaultdict(list)
    for e in events:by[e['session']].append(e)
    for i in range(events[0]['session'],events[-1]['session']+1):
        op,lo,cl,d=bars[i];div+=q*d
        def mark(price):return net+div+q*price*.999-cost
        if q:envelope=min(envelope,mark(lo))
        for e in by[i]:
            if e['action']=='BUY':
                adds+=int(q>0);q+=e['qty'];cost+=e['cost']
            else:
                q-=e['qty'];net+=e['net'];reductions+=int(q>1e-6);stops+=int('STOP' in e.get('reason',''))
            assert q>=-1e-6
            if abs(q)<1e-6:q=0
            fill=min(fill,mark(e['price']));envelope=min(envelope,fill)
            if q:envelope=min(envelope,mark(lo))
        if q:post=min(post,mark(lo))
        post=min(post,fill)
    assert q==0
    return dict(fill_marks=fill/cost,post_fill_low=post/cost,exposed_state_low=envelope/cost,pnl=net+div-cost,acquisition_cost=cost,adds=adds,reductions=reductions,stop_fills=stops)
def fit(g,feature,outcome,controls):
    cols=[feature,outcome]+(['log_duration','vol20','mom63'] if controls else [])
    u=g.dropna(subset=cols).copy();keys=[u.chromosome_id,u.year]
    a=u[cols]-u[cols].groupby(keys).transform('mean');x=a[feature].to_numpy();sd=np.sqrt(np.mean(x*x))
    if len(u)<30 or sd<1e-10:return None
    X=np.column_stack([x/sd]+[a[c].to_numpy() for c in cols[2:]]);y=a[outcome].to_numpy()
    inv=np.linalg.pinv(X.T@X);b=inv@X.T@y;influence=(X*(y-X@b)[:,None])@inv[:,0]
    daily=pd.Series(influence,index=u.entry_date).groupby(level=0).sum().reindex(pd.bdate_range(u.entry_date.min(),u.exit_date.max()),fill_value=0)
    month=daily.groupby(daily.index.to_period('M')).sum();ses=[np.sqrt((month**2).sum()*len(month)/(len(month)-1))]
    s=daily.to_numpy()
    for lag in [63,126]:
        v=s@s
        for k in range(1,min(lag,len(s)-1)+1):v+=2*(1-k/(lag+1))*(s[k:]@s[:-k])
        ses.append(np.sqrt(max(0,v)))
    se=max(ses);return dict(n=len(u),dates=u.entry_date.nunique(),cells=u.groupby(['chromosome_id','year']).ngroups,effect=b[0],sd=sd,se_month=ses[0],se63=ses[1],se126=ses[2],lo=b[0]-1.96*se,hi=b[0]+1.96*se,p=2*norm.sf(abs(b[0]/se)))
def main():
    sel=pd.read_csv(P/'selection.csv');paths=sel.path.unique();hashes={str(BAR):sha(BAR)}
    raw=pd.read_parquet(BAR,columns=['date','ticker','open','low','close','dividends']);raw=raw[(raw.date>='2009-01-01')&(raw.date<'2019-01-01')];dates=sorted(raw.date.unique());idx={d:i for i,d in enumerate(dates)}
    bars=collections.defaultdict(dict)
    for d,t,o,l,c,v in raw.itertuples(index=False,name=None):bars[t][idx[d]]=(o,l,c,0 if pd.isna(v) else v)
    features=R.parent/'breadth_chromosome_multihorizon_20261031/entry_features.csv';f=pd.read_csv(features,parse_dates=['entry_date','feature_date']).set_index('entry_date');hashes[str(features)]=sha(features)
    source=json.loads((R.parent/'spy_state_predictor_20261031/run_metadata.json').read_text())['sources']['SPY']['path'];sp=pd.read_parquet(source);sp.date=pd.to_datetime(sp.date).dt.tz_localize(None);s=sp.set_index('date').adj_close.sort_index();f['vol20']=(s.pct_change().rolling(20).std()*np.sqrt(252)).shift(1);f['mom63']=(s/s.shift(63)-1).shift(1);hashes[source]=sha(source)
    rows=[];audit=[]
    for path in paths:
        d=json.load(gzip.open(path,'rt'));hashes[path]=sha(path);ev=collections.defaultdict(list)
        for e in d['fills']:ev[e['ticker']].append(e)
        reconstructed={};opens=0
        for t,ee in ev.items():
            q=0;cycle=[]
            for e in ee:
                cycle.append(e);q+=(1 if e['action']=='BUY' else -1)*e['qty']
                if abs(q)<1e-6:
                    z=cycle_risk(cycle,bars[t]);reconstructed[(t,cycle[0]['session'],cycle[-1]['session'])]=z;cycle=[];q=0
            opens+=bool(cycle)
        for t in d['trades']:
            z=reconstructed[(t['ticker'],t['entry_session'],t['exit_session'])];assert abs(z['pnl']-t['pnl'])<.005
            prices=[bars[t['ticker']][i][2] for i in range(t['entry_session'],t['exit_session']+1)]
            rows.append(dict(system=d['system'],chromosome_id=d['chromosome_id'],ticker=t['ticker'],entry_date=pd.Timestamp(dates[t['entry_session']]),exit_date=pd.Timestamp(dates[t['exit_session']]),duration=t['exit_session']-t['entry_session'],close_path=min(0,min(prices)/prices[0]-1),**z))
        assert len(reconstructed)==len(d['trades']);audit.append(dict(system=d['system'],chromosome_id=d['chromosome_id'],trades=len(reconstructed),open_cycles_excluded=opens,matched_pnl=True))
    u=pd.DataFrame(rows).join(f,on='entry_date');u['year']=u.entry_date.dt.year;u['log_duration']=np.log1p(u.duration);assert (u.feature_date<u.entry_date).all();u.to_csv(R/'risk_episodes.csv.gz',index=False);pd.DataFrame(audit).to_csv(R/'ledger_audit.csv',index=False)
    results=[];annual=[]
    for system,g in u.groupby('system'):
        for feature in (['b50','b100','d200_21'] if system=='GA7' else ['d50_21','a200_21','d200_21']):
            for outcome in ['close_path','fill_marks','post_fill_low','exposed_state_low']:
                for controls in [False,True]:
                    z=fit(g,feature,outcome,controls)
                    if z:results.append(dict(system=system,feature=feature,outcome=outcome,controls=controls,**z))
                for year,v in g.groupby('year'):
                    z=fit(v,feature,outcome,True)
                    if z:annual.append(dict(system=system,year=year,feature=feature,outcome=outcome,**z))
    z=pd.DataFrame(results);p=z.p.to_numpy();order=np.argsort(p);q=np.empty(len(p));q[order]=np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1];z['q_bh']=q.clip(0,1);z['p_bonferroni']=(z.p*len(z)).clip(upper=1);z.to_csv(R/'associations.csv',index=False);pd.DataFrame(annual).to_csv(R/'annual.csv',index=False)
    for p in [Path(__file__),P/'selection.csv',R/'engine_probe.log']:hashes[str(p)]=sha(p)
    (R/'metadata.json').write_text(json.dumps(dict(hashes=hashes,episodes=len(u),ledgers=len(paths),method='OHLC proxies; not actual intraday MAE',portfolio_status='BLOCKED',ga_run=False),indent=2))
    print(u.groupby('system')[['adds','reductions','stop_fills']].sum());print(z[(z.controls)&z.feature.isin(['b50','d50_21'])].to_string(index=False))
if __name__=='__main__':main()
