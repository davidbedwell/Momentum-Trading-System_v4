"""Offline reconstruction: original user script was not available. See README."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import hashlib, json, time, platform
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet')
NAMES=['mom_126d','mom_12m_skip1m','price_over_sma200','sma50_over_sma200','ema20_over_ema100','near_52w_high','donchian_100d','low_vol_60d','reversal_1m','rsi14_oversold']

def indicators(c):
    sma200=c.rolling(200).mean(); delta=c.diff()
    gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    rsi=100-100/(1+gain/loss)
    return dict(zip(NAMES,[c/c.shift(126)-1,c.shift(21)/c.shift(252)-1,c/sma200-1,c.rolling(50).mean()/sma200-1,c.ewm(span=20,adjust=False,min_periods=20).mean()/c.ewm(span=100,adjust=False,min_periods=100).mean()-1,c/c.rolling(252).max()-1,c/c.rolling(100).max()-1,-c.pct_change(fill_method=None).rolling(60).std(),-(c/c.shift(21)-1),-rsi]))

def select(signal, valid, rng=None, trials=1):
    ids=np.flatnonzero(valid & np.isfinite(signal)); k=max(1,len(ids)//5) if len(ids) else 0
    w=np.zeros((trials,len(signal)))
    if k:
        if rng is None:
            chosen=ids[np.argsort(-signal[ids],kind='stable')[:k]];w[:,chosen]=1/k
        else:
            ranks=rng.random((trials,len(ids))).argsort(axis=1)[:,:k]
            np.put_along_axis(w,ids[ranks],1/k,axis=1)
    return w,len(ids),k

def rebalance(previous,target,cost=.001):
    # Solve exact self-financing proportional commission at open; cash is not traded.
    fee=np.zeros(len(target))
    for _ in range(12): fee=cost*np.abs(target*(1-fee[:,None])-previous).sum(axis=1)
    turnover=np.abs(target*(1-fee[:,None])-previous).sum(axis=1)
    return fee,turnover

def summarize(r, benchmark, daily, turnover, cost, sessions):
    r=np.asarray(r);b=np.asarray(benchmark);x=r-b
    t,p=stats.ttest_1samp(x,0) if len(x)>1 and x.std()>0 else (0.,1.)
    wealth=np.cumprod(1+r); dd=np.asarray(daily); dd=np.r_[1,dd]
    return dict(months=len(r),total_return=wealth[-1]-1,cagr=wealth[-1]**(252/sessions)-1,annualized_arithmetic_excess=x.mean()*12,t=float(t),p=float(p),monthly_sharpe=r.mean()/r.std(ddof=1)*np.sqrt(12),max_drawdown=float(1-np.min(dd/np.maximum.accumulate(dd))),monthly_max_drawdown=float(1-np.min(np.r_[1,wealth]/np.maximum.accumulate(np.r_[1,wealth]))),turnover_sum=float(np.sum(turnover)),turnover_monthly_mean=float(np.mean(turnover)),cost_fraction_sum=float(np.sum(cost)))

def replay(c,o,sig,start,end,seed=1):
    # The mask is made solely from the previous session. No future listing/return eligibility.
    idx=c.index; a=np.flatnonzero((idx>=start)&(idx<=end)); first=a[0];last=a[-1]
    starts=[i for i in a if i==first or idx[i].month!=idx[i-1].month]
    rng=np.random.default_rng(seed); n=c.shape[1]; prev=np.zeros((502,n)); nav=np.ones(502)
    returns=[]; turns=[]; fees=[]; records=[]; dailies=[]; daily_records=[]; weights=[]
    cv=c.to_numpy();ov=o.to_numpy();sv=sig.to_numpy()
    for m,i in enumerate(starts):
        j=starts[m+1] if m+1<len(starts) else last
        terminal=m+1==len(starts)
        valid=np.isfinite(cv[i-1])&(cv[i-1]>0)
        w,eligible,k=select(sv[i-1],valid)
        rw,_,_=select(sv[i-1],valid,rng,500)
        b=np.zeros((1,n)); ids=valid & np.isfinite(sv[i-1]); b[:,ids]=1/eligible if eligible else 0
        target=np.vstack([w,b,rw]); requested=target.copy()
        # Missing opening quotes cancel target purchases; this is execution, not screening.
        available=np.isfinite(ov[i])&(ov[i]>0)
        if np.any((prev>0)&~available): raise RuntimeError('Missing open for held name: requires explicit liquidation policy')
        target[:,~available]=0
        mark=cv[j] if terminal else ov[j]
        if np.any((target>0)&~np.isfinite(mark)): raise RuntimeError('Missing terminal held mark')
        rel=np.divide(mark,ov[i],out=np.ones(n),where=available & np.isfinite(mark))-1
        fee,turn=rebalance(prev,target)
        gross=1+target@rel; r=(1-fee)*gross-1
        # Intramonth close marks plus next-open endpoint; only selected strategy and benchmark.
        stop=j+1 if terminal else j
        marks=cv[i:stop]/ov[i]
        for q in range(len(marks)):
            used=target[:2]>0
            if np.any(used & ~np.isfinite(marks[q])): raise RuntimeError('Missing held daily close')
        daily=nav[:2,None]*(1-fee[:2,None])*(1+target[:2]@np.nan_to_num(marks-1).T)
        dailies.extend(daily.T.tolist()); dailies.append((nav[:2]*(1+r[:2])).tolist())
        for q,values in enumerate(daily.T):
            daily_records.append(dict(date=str(idx[i+q].date()),mark='close',strategy_nav=values[0],benchmark_nav=values[1]))
        values=nav[:2]*(1+r[:2])
        daily_records.append(dict(date=str(idx[j].date()),mark='close' if terminal else 'open',strategy_nav=values[0],benchmark_nav=values[1]))
        nav*=1+r; prev=target*(1+rel)/gross[:,None]
        returns.append(r);turns.append(turn);fees.append(fee)
        records.append(dict(signal_date=str(idx[i-1].date()),execution_date=str(idx[i].date()),end_date=str(idx[j].date()),terminal_close=terminal,eligible=eligible,prior_price_eligible=int(valid.sum()),nonfinite_signal_excluded=int((valid & ~np.isfinite(sv[i-1])).sum()),k=k,canceled_targets=int(np.sum((requested[0]>0)&~available))))
        for z in np.flatnonzero(target[0]): weights.append(dict(execution_date=str(idx[i].date()),ticker=c.columns[z],weight=target[0,z],signal=sv[i-1,z]))
    r=np.array(returns);tu=np.array(turns);fe=np.array(fees);dy=np.array(dailies)
    metrics=summarize(r[:,0],r[:,1],dy[:,0],tu[:,0],fe[:,0],len(a))
    bm=summarize(r[:,1],r[:,1],dy[:,1],tu[:,1],fe[:,1],len(a))
    random_cagr=np.prod(1+r[:,2:],axis=0)**(252/len(a))-1
    metrics.update(benchmark_cagr=bm['cagr'],benchmark_max_drawdown=bm['max_drawdown'],random_cagr_mean=float(random_cagr.mean()),random_cagr_p05=float(np.quantile(random_cagr,.05)),random_cagr_p95=float(np.quantile(random_cagr,.95)),random_empirical_p=float((1+np.sum(random_cagr>=metrics['cagr']))/501))
    table=pd.DataFrame(records); table['strategy_return']=r[:,0];table['benchmark_return']=r[:,1];table['turnover']=tu[:,0];table['cost_fraction']=fe[:,0];table.attrs['daily']=pd.DataFrame(daily_records)
    return metrics,table,pd.DataFrame(weights),pd.DataFrame({'trial':range(500),'cagr':random_cagr,'total_return':np.prod(1+r[:,2:],axis=0)-1,'turnover_sum':tu[:,2:].sum(axis=0)})

def discovery_gate(row):
    return row['t']>=2 and row['p']<=.05 and row['annualized_arithmetic_excess']>0

def main():
    begun=time.monotonic(); d=pd.read_parquet(SOURCE);d['date']=pd.to_datetime(d.date)
    assert not d.duplicated(['date','ticker']).any()
    close=d.pivot(index='date',columns='ticker',values='close').sort_index(); op=d.pivot(index='date',columns='ticker',values='open').reindex_like(close);adj=d.pivot(index='date',columns='ticker',values='adj_close').reindex_like(close)
    rows=[];gates=[]
    for basis,c,o in [('adjusted',adj,op*(adj/close)),('price_only',close,op)]:
        features=indicators(c); discovery=[]
        for name,s in features.items():
            metrics,table,w,random=replay(c,o,s,'2009-01-01','2018-12-31')
            row=dict(basis=basis,period='discovery',indicator=name,p_bonferroni_10=min(1,metrics['p']*10),**metrics); rows.append(row);discovery.append(row)
            dest=ROOT/basis/'discovery'/name;dest.mkdir(parents=True,exist_ok=True)
            table.to_csv(dest/'monthly.csv',index=False);table.attrs['daily'].to_csv(dest/'daily_marks.csv',index=False);w.to_csv(dest/'holdings.csv',index=False);random.to_csv(dest/'random_trials.csv',index=False)
        # Explicit reconstruction assumption: highest paired t is the single finalist.
        finalist=max(discovery,key=lambda x:x['t']);passed=discovery_gate(finalist)
        gates.append(dict(basis=basis,finalist=finalist['indicator'],passed=bool(passed),t=finalist['t'],p=finalist['p'],bonferroni_p=min(1,finalist['p']*10)))
        # Write discovery and gate before any conditional blind portfolio evaluation.
        pd.DataFrame(rows).to_csv(ROOT/'metrics.csv',index=False);(ROOT/'gates.json').write_text(json.dumps(gates,indent=2))
        if passed:
            name=finalist['indicator'];metrics,table,w,random=replay(c,o,features[name],'2019-01-01',str(c.index.max().date()))
            rows.append(dict(basis=basis,period='blind',indicator=name,**metrics));dest=ROOT/basis/'blind'/name;dest.mkdir(parents=True,exist_ok=True)
            table.to_csv(dest/'monthly.csv',index=False);table.attrs['daily'].to_csv(dest/'daily_marks.csv',index=False);w.to_csv(dest/'holdings.csv',index=False);random.to_csv(dest/'random_trials.csv',index=False)
    pd.DataFrame(rows).to_csv(ROOT/'metrics.csv',index=False)
    ordered=d.sort_values(['ticker','date']).copy()
    ordered['previous_close']=ordered.groupby('ticker')['close'].shift()
    splits=ordered.loc[ordered.stock_splits.ne(0)].copy()
    splits['open_ratio']=splits.open/splits.previous_close
    splits['error_already_split_adjusted']=abs(splits.open_ratio-1)
    splits['error_if_raw_unadjusted']=abs(splits.open_ratio*splits.stock_splits-1)
    splits.to_csv(ROOT/'split_continuity.csv',index=False)
    major=splits.loc[(splits.stock_splits>=1.5)|(splits.stock_splits<=1/1.5)]
    (ROOT/'split_audit.json').write_text(json.dumps(dict(events=len(splits),major_events=len(major),major_favoring_already_adjusted=int((major.error_already_split_adjusted<major.error_if_raw_unadjusted).sum()),note='Continuity heuristic only; vendor basis not independently certified.'),indent=2))
    coverage=d.groupby('ticker').agg(start=('date','min'),end=('date','max'),bars=('date','size'));coverage.to_csv(ROOT/'coverage.csv')
    provenance=dict(source=str(SOURCE),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),rows=len(d),tickers=len(coverage),start=str(d.date.min()),end=str(d.date.max()),spy_present='SPY' in coverage.index,seconds=time.monotonic()-begun,cpu_affinity=sorted(os.sched_getaffinity(0)),python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__)
    (ROOT/'provenance.json').write_text(json.dumps(provenance,indent=2));print(pd.DataFrame(rows).to_string(index=False));print(json.dumps(gates,indent=2));print(provenance)
if __name__=='__main__': main()
