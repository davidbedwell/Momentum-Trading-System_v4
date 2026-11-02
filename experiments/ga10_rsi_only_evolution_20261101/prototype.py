"""Isolated causal experimental portfolio manager; see PLAN.md for frozen scope."""
from pathlib import Path
import hashlib,json,time
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
SOURCE=Path('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet')
FEE=.001

def load(path=SOURCE):
    raw=pd.read_parquet(path)
    # Truncate before feature construction: no post-2018 values enter any calculations.
    raw=raw.loc[pd.to_datetime(raw.date)<='2018-12-31'].copy()
    raw.date=pd.to_datetime(raw.date)
    if raw.duplicated(['date','ticker']).any(): raise ValueError('duplicate price keys')
    c=raw.pivot(index='date',columns='ticker',values='adj_close').sort_index().sort_index(axis=1)
    o=(raw.assign(ao=raw.open*raw.adj_close/raw.close).pivot(index='date',columns='ticker',values='ao').reindex_like(c))
    return prepare(c,o)

def prepare(c,o):
    r=c.pct_change(fill_method=None)
    up=c.diff().clip(lower=0).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    dn=(-c.diff().clip(upper=0)).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    rsi=100-100/(1+up/dn)
    rsi=rsi.mask((dn==0)&(up>0),100).mask((up==0)&(dn>0),0)
    ma=c/c.rolling(20).mean()-1
    accel=c/c.shift(21)-1-(c.shift(21)/c.shift(42)-1)
    features=np.stack([(rsi.to_numpy()-50)/50,ma.to_numpy()*10,accel.to_numpy()*5,
                       (c/c.shift(5)-1).to_numpy()*10,(c/c.shift(63)-1).to_numpy()*3,
                       r.rolling(21).std().to_numpy()*np.sqrt(252)],axis=2)
    # Full history indicators, all decisions explicitly index previous session.
    screens=np.zeros(c.shape,bool); rscreens=screens.copy()
    active=np.zeros(c.shape[1],bool); ra=active.copy()
    for t in range(1,len(c)):
        if c.index[t].month!=c.index[t-1].month or c.index[t].year!=c.index[t-1].year:
            a=rsi.iloc[t-1].to_numpy(); price=c.iloc[t-1].to_numpy()
            ix=np.flatnonzero(np.isfinite(a)&np.isfinite(price)&(price>0))
            chosen=ix[np.argsort(a[ix],kind='stable')[:max(1,len(ix)//5)]]
            ra=np.zeros(c.shape[1],bool);ra[chosen]=True
            active=ra & (ma.iloc[t-1].to_numpy()<0)&(accel.iloc[t-1].to_numpy()>0)
        screens[t]=active;rscreens[t]=ra
    return dict(dates=c.index,names=list(c.columns),c=c.to_numpy(),o=o.to_numpy(),x=features,screen=screens,rsi=rscreens)

# 5 heads × (bias + 8 predictors), followed by 6 bounded sizing/control genes.
SIZE=51

def controls(g):
    s=1/(1+np.exp(-g[45:]))
    return .1+.8*s[0], .05+.45*s[1], .1+.8*s[2], .05+.25*s[3], .2+.8*s[4], .08+.16*s[5]

def target(g,x,w,age,pnl,screen,dd):
    finite=np.isfinite(x).all(axis=1)
    z=np.column_stack([np.ones(len(w)),np.nan_to_num(x),np.clip(pnl,-1,1),np.minimum(age,252)/252])
    scores=z@g[:45].reshape(5,9).T
    entry,add,reduce,cap,exposure,stop=controls(g)
    held=w>1e-12; desired=w.astype(float).copy(); actions=np.full(len(w),'hold',dtype=object)
    exit_=held & ((scores[:,3]>0)|(dd>=stop))
    red=held & ~exit_ & (scores[:,2]>0)
    adds=held & ~exit_ & ~red & finite & (scores[:,1]>0)
    enter=~held & screen & finite & (scores[:,0]>0) & (dd<stop)
    allocation=cap/(1+np.exp(-np.clip(scores[:,4],-30,30)))
    desired[exit_]=0;actions[exit_]='exit'
    desired[red]*=1-reduce;actions[red]='reduce'
    desired[adds]=np.minimum(cap,desired[adds]+add*allocation[adds]);actions[adds]='add'
    desired[enter]=entry*allocation[enter];actions[enter]='entry'
    desired=np.minimum(desired,cap)
    if desired.sum()>exposure: desired*=exposure/desired.sum()
    return desired,actions

def rebalance(shares,cash,price,weights):
    held=shares>1e-12
    if np.any(held & (~np.isfinite(price)|(price<=0))): raise ValueError('missing held execution price')
    tradable=np.isfinite(price)&(price>0)
    weights=weights.copy();weights[~tradable]=0
    current=shares*np.where(tradable,price,0);nav=cash+current.sum()
    # Bisection of post-fee wealth: exact fees on actual dollar notional.
    lo,hi=0.,nav
    for _ in range(40):
        mid=(lo+hi)/2
        if mid+FEE*np.abs(weights*mid-current).sum()>nav: hi=mid
        else: lo=mid
    dollars=weights*((lo+hi)/2);delta=dollars-current;fee=FEE*np.abs(delta).sum()
    newshares=np.divide(dollars,price,out=np.zeros_like(dollars),where=tradable)
    newcash=nav-dollars.sum()-fee
    assert newcash>=-1e-9 and weights.sum()<=1+1e-9
    return newshares,max(0.,newcash),delta,fee,nav

def run(data,start,end,g=None,baseline=None,details=False):
    dates=data['dates']; ids=np.flatnonzero((dates>=start)&(dates<=end)); n=len(data['names'])
    shares=np.zeros(n);cash=1.;age=np.zeros(n);basis=np.zeros(n);peak=1.;previous_nav=1.
    rows=[];trades=[];counts={a:0 for a in ['entry','hold','add','reduce','exit']};totalfee=turnover=0.
    for t in ids:
        if t==0: raise ValueError('prior session required')
        c,o=data['c'][t],data['o'][t];prior=data['c'][t-1]
        held=shares>1e-12
        if np.any(held & (~np.isfinite(prior)|(prior<=0))): raise ValueError('missing prior mark')
        lastvalue=shares*np.nan_to_num(prior);lastnav=cash+lastvalue.sum();w=lastvalue/lastnav
        pnl=np.divide(prior,basis,out=np.ones(n),where=basis>0)-1
        dd=1-lastnav/peak
        if baseline:
            monthly=t==ids[0] or dates[t].to_period('M')!=dates[t-1].to_period('M')
            pool=data[baseline][t];desired=pool.astype(float)/max(1,pool.sum())
            acts=np.where((w==0)&(desired>0),'entry',np.where((w>0)&(desired==0),'exit','rebalance'))
        else:
            desired,acts=target(g,data['x'][t-1],w,age,pnl,data['screen'][t],dd)
            # Preserve shares for HOLD; apply prior-close dollar changes at the open.
            if np.any(held & (~np.isfinite(o)|(o<=0))): raise ValueError('missing held open')
            open_values=shares*np.nan_to_num(o); open_total=cash+open_values.sum()
            desired=np.maximum(0,open_values+(desired-w)*lastnav)/open_total
            desired[acts=='exit']=0
            if desired.sum()>1: desired/=desired.sum()
            monthly=True
        if monthly:
            old=shares.copy(); shares,cash,delta,fee,open_nav=rebalance(shares,cash,o,desired)
            for j in np.flatnonzero(np.abs(delta)>1e-11):
                action=str(acts[j]);counts[action]=counts.get(action,0)+1
                if details: trades.append([str(dates[t].date()),data['names'][j],action,float(delta[j]),float(FEE*abs(delta[j])),bool(data['screen'][t,j]),str(dates[t-1].date())])
            buys=shares>old+1e-12
            basis[buys]=(old[buys]*basis[buys]+(shares[buys]-old[buys])*o[buys])/shares[buys]
            age[(old<=1e-12)&(shares>1e-12)]=0
            basis[shares<=1e-12]=0
            totalfee+=fee;turnover+=np.abs(delta).sum()/open_nav
            open_after=open_nav-fee
        else:
            if np.any(held&(~np.isfinite(o)|(o<=0))):raise ValueError('missing held open')
            open_after=cash+np.sum(shares*np.nan_to_num(o));fee=0
        held=shares>1e-12
        if np.any(held&(~np.isfinite(c)|(c<=0))):raise ValueError('missing held close')
        nav=cash+np.sum(shares*np.nan_to_num(c));peak=max(peak,open_after,nav)
        counts['hold']+=int(np.sum(held & (acts=='hold'))) if monthly else int(held.sum())
        rows.append([dates[t],nav,open_after,fee,1-cash/nav,int(held.sum())]);age[held]+=1;previous_nav=nav
    frame=pd.DataFrame(rows,columns=['date','nav','open_nav','fee','exposure','holdings'])
    marks=np.r_[1.,frame[['open_nav','nav']].to_numpy().ravel()];mdd=float(np.max(1-marks/np.maximum.accumulate(marks)))
    ret=np.diff(np.r_[1.,frame.nav])/np.r_[1.,frame.nav.to_numpy()[:-1]]
    metric=dict(cagr=float(frame.nav.iloc[-1]**(252/len(frame))-1),mdd=mdd,final_nav=float(frame.nav.iloc[-1]),annual_vol=float(np.std(ret,ddof=1)*np.sqrt(252)),sharpe=float(np.mean(ret)/np.std(ret,ddof=1)*np.sqrt(252)) if np.std(ret)>0 else 0.,turnover=turnover,costs_initial_capital=totalfee,mean_exposure=float(frame.exposure.mean()),sessions=len(frame),actions=counts)
    assert np.isfinite([metric['cagr'],mdd,metric['final_nav']]).all()
    return metric,frame,pd.DataFrame(trades,columns=['date','ticker','action','notional','fee','in_screen','signal_date'])

def fitness(m): return (1,m['cagr']) if m['mdd']<.25 else (0,-m['mdd'],m['cagr'])

def search(data,start,end,population,generations,folder):
    rng=np.random.default_rng(10);pop=rng.normal(0,.6,(population,SIZE));history=[];best=None;bestkey=None
    for gen in range(generations):
        evaluated=[]
        for k,g in enumerate(pop):
            m,_,_=run(data,start,end,g);key=fitness(m);evaluated.append((key,g.copy()))
            history.append(dict(generation=gen,candidate=k,**{a:b for a,b in m.items() if a!='actions'},genome=json.dumps(g.tolist())))
            if bestkey is None or key>bestkey: bestkey=key;best=g.copy()
        evaluated.sort(key=lambda a:a[0],reverse=True);elite=[a[1] for a in evaluated[:max(2,population//3)]]
        pop=np.array([best]+[np.where(rng.random(SIZE)<.5,elite[rng.integers(len(elite))],elite[rng.integers(len(elite))])+rng.normal(0,.25,SIZE) for _ in range(population-1)])
    folder.mkdir(exist_ok=True);pd.DataFrame(history).to_csv(folder/'search.csv',index=False)
    (folder/'genome.json').write_text(json.dumps(best.tolist(),indent=2))
    return best

def evaluate(data,g,periods,folder):
    metrics=[]
    for split,(start,end) in periods.items():
        for name,b in [('ga10',None),('monthly_rsi_setup','screen'),('monthly_rsi','rsi')]:
            m,nav,trades=run(data,start,end,g,b,True)
            nav.to_csv(folder/f'{split}_{name}_daily.csv',index=False);trades.to_csv(folder/f'{split}_{name}_trades.csv',index=False)
            metrics.append(dict(split=split,strategy=name,**m))
    (folder/'metrics.json').write_text(json.dumps(metrics,indent=2))
    pd.DataFrame([{k:v for k,v in m.items() if k!='actions'} for m in metrics]).to_csv(folder/'metrics.csv',index=False)
    return metrics

def main():
    started=time.monotonic();data=load()
    smoke=ROOT/'smoke';g=search(data,'2009-01-01','2010-12-31',6,2,smoke)
    metrics=evaluate(data,g,{'train':('2009-01-01','2010-12-31'),'diagnostic':('2011-01-01','2011-12-31')},smoke)
    replay=run(data,'2009-01-01','2010-12-31',g)[0]
    proof=all(np.isfinite(m['cagr']) for m in metrics) and sum(v for k,v in replay['actions'].items() if k!='hold')>0 and replay==run(data,'2009-01-01','2010-12-31',g)[0]
    (ROOT/'smoke_gate.json').write_text(json.dumps({'functionality_pass':bool(proof),'performance_used_for_gate':False},indent=2))
    if not proof: raise RuntimeError('STOP: smoke functionality failed; no scaling')
    bounded=ROOT/'bounded';g=search(data,'2009-01-01','2013-12-31',12,3,bounded)
    metrics=evaluate(data,g,{'train':('2009-01-01','2013-12-31'),'examined_holdout':('2014-01-01','2018-12-31')},bounded)
    monthly=[]
    for t in range(1,len(data['dates'])):
        d=data['dates'][t]
        if d.year>=2009 and d.to_period('M')!=data['dates'][t-1].to_period('M'):
            for j,name in enumerate(data['names']):
                if data['rsi'][t,j]:monthly.append([d,data['dates'][t-1],name,bool(data['screen'][t,j])])
    pd.DataFrame(monthly,columns=['month_execution','signal_date','ticker','setup_pass']).to_csv(ROOT/'monthly_screen.csv',index=False)
    (ROOT/'provenance.json').write_text(json.dumps(dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),plan_sha256=hashlib.sha256((ROOT/'PLAN.md').read_bytes()).hexdigest(),seed=10,elapsed_seconds=time.monotonic()-started,stop='bounded prototype complete; no further optimization',pit_archive_certified=False,holdout_previously_examined=True),indent=2))
    lines=['# GA10 experimental prototype results','','Functionality smoke passed; completed one bounded training search. No production changes or GA6/GA7 replay. Stopped at the frozen budget.','','|Split|Strategy|Net CAGR|Daily MDD|Mean exposure|Turnover|','|---|---|---:|---:|---:|---:|']
    for m in metrics:lines.append(f"|{m['split']}|{m['strategy']}|{m['cagr']:.2%}|{m['mdd']:.2%}|{m['mean_exposure']:.2%}|{m['turnover']:.2f}|")
    for split in ['train','examined_holdout']:
        ms={m['strategy']:m for m in metrics if m['split']==split};a=ms['ga10']
        lines+=['',f"{split}: GA10 CAGR difference vs setup baseline {a['cagr']-ms['monthly_rsi_setup']['cagr']:+.2%}; vs RSI baseline {a['cagr']-ms['monthly_rsi']['cagr']:+.2%}. MDD preference met: {a['mdd']<.25}. Actions: `{json.dumps(a['actions'])}`."]
    lines+=['','The monthly screen only grants entry eligibility. GA10 can decline entry, enter later in the month, and continue managing positions offscreen. The baselines deliberately purchase their monthly baskets. All use the same 10 bp per-side notional cost and adjusted next-open accounting. Training selection is lexicographic feasible CAGR / infeasible MDD; evaluation never participates in selection. Drawdown stop cannot guarantee a 25% realized limit through gaps.','', '2014–2018 is previously examined holdout, not pristine validation. The frozen screen itself was selected by earlier research. Adjusted archive prices and retrospective DEV79 membership are not certified PIT; no unbiased deployability or alpha claim is supported. No data after 2018 enter features or evaluation. Missing held prices fail closed. Fractional shares, instant sale proceeds, no market impact, taxes, settlement delays or cash interest. Final positions marked to close without liquidation fees.','', 'Reproduce: `bash experiments/ga10_rsi_screen_manager_20261101/run.sh`. See PLAN.md, test_ga10.py, smoke_gate.json, bounded/search.csv, bounded/genome.json, per-strategy daily paths/trades, monthly_screen.csv and provenance.json. This completes the prototype; further GA scale is not authorized by these returns.']
    lines += ['', 'Prototype limitation: the selected genome made no reduce trades; that branch was exercised by the forced-state test. The drawdown stop uses a persistent high-water mark and may leave a fully liquidated account in cash for the remainder of a split. No restart rule was tuned.']
    (ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines[:13]))

if __name__=='__main__':main()
