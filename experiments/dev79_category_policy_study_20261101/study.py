"""Frozen, real-OHLCV category attribution; no policy selection."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
import itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
from comparison import SOURCE,digest,INITIAL
from trade_accounting import TradeAccount
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'artifacts'
SPY=Path('/opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet')
MODES=['manager','claude_approx','gemini_approx','grok_dev79_approx']
CATS=['acceleration','uptrend','consolidation','deterioration','reversal','unknown']

def classify(d,spy):
    c=d['close'];v=d['volume'];r5=c/c.shift(5)-1;r20=c/c.shift(20)-1
    ma20=c.rolling(20).mean();ma50=c.rolling(50).mean();old5=c.shift(5)/c.shift(10)-1
    rs=r20.sub(spy.reindex(c.index).pct_change(20,fill_method=None),axis=0)
    vr=v/v.rolling(20).mean()
    valid=pd.DataFrame(True,index=c.index,columns=c.columns)
    for k in ['open','high','low','close']:valid &= np.isfinite(d[k]) & (d[k]>0)
    valid &= np.isfinite(v)&(v>=0)
    ready=valid.astype(int).rolling(51).sum().eq(51)&rs.notna()&vr.notna()
    rules=[(c>ma20)&(r5>0)&(c.shift(5)<=ma20.shift(5))&(c.shift(20)/c.shift(40)-1<0),
           (c<ma50)&((r20<0)|(rs<0)),
           (c>ma20)&(ma20>ma50)&(r5>old5)&(r20>0)&(rs>0)&(vr>=1),
           (c>ma50)&(r20>0)&(rs>=0)]
    state=pd.DataFrame(np.select([ready.to_numpy()&r.to_numpy() for r in rules]+[ready.to_numpy()],['reversal','deterioration','acceleration','uptrend','consolidation'],default='unknown'),index=c.index,columns=c.columns)
    # Stronger-than-required lag: even the decision day's bar cannot affect category.
    return state.shift(1).fillna('unknown'), {'r5':r5.shift(1),'r20':r20.shift(1),'rs20':rs.shift(1),'vr20':vr.shift(1),'ma20':ma20.shift(1),'ma50':ma50.shift(1)}

def segment(dates):
    return np.where(dates<=pd.Timestamp('2017-12-29'),'discovery','test')

def load_panel():
    raw=pd.read_parquet(SOURCE,use_threads=False);raw.date=pd.to_datetime(raw.date)
    return raw,{k:raw.pivot(index='date',columns='ticker',values=k).sort_index() for k in ['open','high','low','close','volume']}

def main():
    raw,d=load_panel();spy=pd.read_parquet(SPY,use_threads=False);spy.date=pd.to_datetime(spy.date)
    assert not spy.date.duplicated().any() and (spy.close>0).all()
    spy=spy.set_index('date').close.sort_index();states,ind=classify(d,spy)
    dates=d['close'].loc['2009-01-01':'2026-09-14'].index;ts=d['close'].columns
    idx=pd.MultiIndex.from_product([dates,ts],names=['date','ticker'])
    common=pd.DataFrame(index=idx)
    for k,v in {'category':states,**ind,'decision_close':d['close'],'execution_open':d['open'].shift(-1),'end_open':d['open'].shift(-2),'execution_close':d['close'].shift(-1)}.items():common[k]=v.reindex(dates).stack(future_stack=True).reindex(idx)
    common['state_asof']=np.repeat(d['close'].index.to_series().shift(1).reindex(dates).dt.strftime('%Y-%m-%d').values,len(ts))
    common['execution_date']=np.repeat(d['close'].index.to_series().shift(-1).reindex(dates).values,len(ts))
    common['horizon_end']=np.repeat(d['close'].index.to_series().shift(-2).reindex(dates).values,len(ts))
    common['segment']=np.repeat(segment(dates),len(ts))
    # Both horizon endpoints must be within replay AND the originating split.
    common['valid']=common[['execution_open','end_open','decision_close','execution_close']].gt(0).all(axis=1)&common.horizon_end.le(dates[-1])&((common.segment=='discovery')==common.horizon_end.le(pd.Timestamp('2017-12-29')))
    common['stock_hold_return']=common.end_open/common.execution_open-1
    common.to_csv(OUT/'state_opportunities.csv.gz',compression='gzip')
    frames={};fillattrs=[];summ=[];coverage=[]
    for mode in MODES:
        p=OUT/mode;dec=pd.read_csv(p/'decisions.csv',parse_dates=['date']).set_index(['date','ticker']).reindex(idx)
        pos=pd.read_csv(p/'positions.csv',parse_dates=['date']);qp=pos.pivot(index='date',columns='ticker',values='shares').reindex(index=dates,columns=ts).fillna(0)
        q0=qp.stack(future_stack=True).reindex(idx)
        daily=pd.read_csv(p/'daily.csv',parse_dates=['date']).set_index('date')
        gaps=(qp*(d['open'].shift(-1).reindex(dates)-d['close'].reindex(dates))).sum(axis=1)
        open_nav=(daily.nav+gaps).rename('open_nav')
        fills=pd.read_csv(p/'fills.csv',parse_dates=['date','signal_date'])
        fills['delta']=np.where(fills.side=='BUY',fills.shares,-fills.shares)
        fills['slippage_dollars']=fills.shares*(fills.price-fills.open).abs()
        # Reconstruct average-cost realized PnL per fill from unchanged accounting.
        shares={};accounts={};real=[];actual_actions=[]
        for r in fills.itertuples():
            q=shares.get(r.ticker,0.);a=accounts.setdefault(r.ticker,TradeAccount());before=a.realized
            if r.side=='BUY':a.buy(r.notional+r.fee,.1);act='enter' if q<1e-9 else 'add'
            else:a.sell(r.notional-r.fee,min(1.,r.shares/q));act='exit' if q-r.shares<1e-9 else 'reduce'
            shares[r.ticker]=q+r.delta;real.append(a.realized-before);actual_actions.append(act)
        fills['realized_pnl']=real;fills['filled_action']=actual_actions
        fa=fills.merge(common.reset_index()[['date','ticker','category','segment','state_asof']],left_on=['signal_date','ticker'],right_on=['date','ticker'],suffixes=('_fill','_decision'),validate='many_to_one');fa['policy']=mode
        fa.to_csv(OUT/f'{mode}_fill_attribution.csv.gz',index=False,compression='gzip');fillattrs.append(fa)
        agg=fills.groupby(['signal_date','ticker']).agg(delta=('delta','sum'),fee=('fee','sum'),slippage_dollars=('slippage_dollars','sum'),realized_pnl=('realized_pnl','sum'),filled_action=('filled_action','first'))
        agg.index.names=['date','ticker']
        x=common.join(dec[['action','current_dollars','target_dollars']]).join(agg).copy()
        for k in ['delta','fee','slippage_dollars','realized_pnl']:x[k]=x[k].fillna(0)
        x['filled_action']=x.filled_action.fillna('no_fill');x['q0']=q0;x['q1']=q0+x.delta
        x['open_nav']=x.index.get_level_values('date').map(open_nav)
        x['pre_exposure']=x.q0*x.execution_open/x.open_nav;x['post_exposure']=x.q1*x.execution_open/x.open_nav
        x['hold_pnl']=x.q0*(x.end_open-x.execution_open)
        x['local_net_pnl']=x.q1*(x.end_open-x.execution_open)-x.fee-x.slippage_dollars
        x['incremental_pnl']=x.local_net_pnl-x.hold_pnl
        x['incremental_nav']=x.incremental_pnl/x.open_nav
        x['local_net_nav']=x.local_net_pnl/x.open_nav
        x['hold_nav']=x.hold_pnl/x.open_nav
        x['policy']=mode;x.to_csv(OUT/f'{mode}_opportunity_ledger.csv.gz',compression='gzip');frames[mode]=x
        for (seg,cat),g in x.groupby(['segment','category']):
            good=g[g.valid];dates_n=g.index.get_level_values('date').nunique()
            actual=fa[(fa.segment==seg)&(fa.category==cat)]
            row=dict(policy=mode,segment=seg,category=cat,all_opportunities=len(g),matched_opportunities=len(good),coverage=len(good)/len(g),matched_days=good.index.get_level_values('date').nunique(),fees_all_fills=actual.fee.sum(),slippage_all_fills=actual.slippage_dollars.sum(),realized_pnl_all_fills=actual.realized_pnl.sum(),mean_pre_exposure=good.pre_exposure.sum()/dates_n,mean_post_exposure=good.post_exposure.sum()/dates_n,local_net_pnl=good.local_net_pnl.sum(),hold_pnl=good.hold_pnl.sum(),incremental_pnl=good.incremental_pnl.sum(),incremental_nav_sum=good.incremental_nav.sum(),stock_hold_mean=good.stock_hold_return.mean())
            for act in ['enter','add','reduce','exit']:row['filled_'+act]=int((actual.filled_action==act).sum());row['decision_'+act]=int((g.action==act).sum())
            summ.append(row)
        coverage.append(dict(policy=mode,all=len(x),matched=int(x.valid.sum()),excluded=int((~x.valid).sum()),missing_action=int(x.action.isna().sum()),max_realized_reconciliation=abs(sum(real)-daily.realized_pnl.iloc[-1])))
    pd.DataFrame(summ).to_csv(OUT/'category_summary.csv',index=False)
    # Shared support eliminates policy-level filtering of category opportunities.
    support=common.copy();support['all_flat']=np.logical_and.reduce([frames[m].q0.lt(1e-9) for m in MODES]);support['all_held']=np.logical_and.reduce([frames[m].q0.gt(1e-9) for m in MODES])
    support.reset_index().groupby(['segment','category']).agg(opportunities=('valid','size'),matched=('valid','sum'),all_flat=('all_flat','sum'),all_held=('all_held','sum')).to_csv(OUT/'support.csv')
    contrasts=[];dailyrows=[];rng=np.random.default_rng(79)
    for seg in ['discovery','test']:
        calendar=dates[segment(dates)==seg];months=calendar.to_period('M');unique=months.unique();codes=unique.get_indexer(months);counts=np.bincount(codes)
        draws=rng.integers(0,len(unique),size=(2000,len(unique)))
        for cat in CATS:
            mask=common.valid&common.segment.eq(seg)&common.category.eq(cat)
            for a,b in itertools.combinations(MODES,2):
                aa=frames[a];bb=frames[b]
                z=(aa.incremental_nav-bb.incremental_nav).where(mask,0).groupby(level='date').sum().reindex(calendar,fill_value=0)
                sums=np.bincount(codes,weights=z.to_numpy(),minlength=len(unique));boot=sums[draws].sum(axis=1)/counts[draws].sum(axis=1)
                # Discordance uses actual executed direction incl no-fill, rather than intended action.
                discord=mask & (np.sign(aa.delta)!=np.sign(bb.delta))
                nd=int(discord.sum());nm=common.index.get_level_values('date')[discord].to_period('M').nunique()
                low,high=np.quantile(boot,[.025,.975]);fl,fh=np.quantile(boot,[.05/60,1-.05/60])
                supported=nd>=100 and nm>=24
                contrasts.append(dict(segment=seg,category=cat,a=a,b=b,matched=int(mask.sum()),discordant_actions=nd,discordant_months=nm,all_flat_matched=int((mask&support.all_flat).sum()),all_held_matched=int((mask&support.all_held).sum()),mean_daily_bps=z.mean()*1e4,ci95_low_bps=low*1e4,ci95_high_bps=high*1e4,family_low_bps=fl*1e4,family_high_bps=fh*1e4,support_pass=bool(supported),status='descriptive_path_confounded' if supported else 'inconclusive_insufficient_comparable_actions'))
                dailyrows.extend(dict(date=str(t.date()),segment=seg,category=cat,a=a,b=b,paired_incremental_nav=float(v)) for t,v in z.items())
    pd.DataFrame(contrasts).to_csv(OUT/'matched_contrasts.csv',index=False);pd.DataFrame(dailyrows).to_csv(OUT/'paired_daily.csv.gz',index=False,compression='gzip')
    audit=dict(source=str(SOURCE),source_sha256=digest(SOURCE),spy=str(SPY),spy_sha256=digest(SPY),spy_rows=len(spy),spy_range=[str(spy.index.min()),str(spy.index.max())],spy_missing_on_dev_sessions=int(spy.reindex(d['close'].index).loc[dates].isna().sum()),relative_strength='SPY unadjusted-for-dividends close return, no verified sector history',coverage=coverage,selector='not fitted; Phase 1 only',bootstrap_replicates=2000,bootstrap_seed=79)
    (OUT/'study_audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
