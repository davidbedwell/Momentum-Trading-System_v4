"""Development-only experiments. Never authorizes validation, promotion or production."""
import argparse
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import random
import time
import numpy as np
import pandas as pd
from .execution import Panel, Gene, Manager, FAMILIES, replay
from .manager_pilot import fixture, mutate
from .nasdaq_archive import normalize
from .alpaca_repair import blocked_symbols
from .supervisor import atomic, target
from .exploratory_exclusions import exclusions

LABEL = 'EXPLORATORY_UNCERTIFIED_DEVELOPMENT_ONLY'
ARCHIVE = Path('/tmp/ga9_nasdaq_archive')


def build(frames):
    d = pd.concat(frames, ignore_index=True)
    dates = pd.DatetimeIndex(sorted(d.date.unique()))
    symbols = sorted(d.ticker.unique())
    def wide(k):
        return d.pivot(index='date', columns='ticker', values=k).reindex(index=dates, columns=symbols)
    c,o,v = wide('close'),wide('open'),wide('volume')
    # Missing execution marks are never filled. Small cohort selection bias is recorded.
    excluded = []
    if c.shape[1] < 2 or len(c)<500: raise ValueError('Insufficient development marks')
    r=c.pct_change(fill_method=None); mom=c/c.shift(20)-1; trend=c/c.rolling(50).mean()-1
    f=dict(momentum=mom/.08,trend=trend/.05,volume=v/v.rolling(20).mean()-1,
           volatility=(.025-r.rolling(20).std())/.015,recursive=(c/c.ewm(span=20,min_periods=50).mean()-1)/.04,
           relative_strength=(c/c.shift(60)-1).rank(axis=1,pct=True)*2-1,
           breadth=pd.DataFrame(np.repeat(((trend>0).mean(axis=1)*2-1).to_numpy()[:,None],c.shape[1],axis=1),index=c.index,columns=c.columns))
    valid=np.isfinite(c.to_numpy()) & np.isfinite(o.to_numpy()) & (c.to_numpy()>0) & (o.to_numpy()>0)
    from .screening import daily_screen, ScreenPolicy
    screen_score, screen_mask = daily_screen(c,c,pd.DataFrame(valid,index=c.index,columns=c.columns),ScreenPolicy())
    p=Panel(dates,c.columns.tolist(),o.to_numpy(),c.to_numpy(),np.zeros(c.shape),r.fillna(0).to_numpy(),
            {k:x.to_numpy() for k,x in f.items()},np.zeros(c.shape,int),np.zeros(len(c)),
            eligible=valid,screen_mask=screen_mask,screen_score=screen_score)
    return p,excluded


def inputs(kind):
    if kind=='synthetic':
        p,_=fixture()
        # Existing synthetic forward starts at 756. Do not reuse it, even as development.
        n=756
        p=replace(p, dates=p.dates[:n],open=p.open[:n],close=p.close[:n],dividends=p.dividends[:n],returns=p.returns[:n],
                  features={k:v[:n] for k,v in p.features.items()},niche=p.niche[:n],breadth=p.breadth[:n],
                  eligible=p.eligible[:n],screen_mask=p.screen_mask[:n],screen_score=p.screen_score[:n])
        return p,dict(kind='synthetic',excluded_forward='indices >=756',sources=[]),{}
    blocked=blocked_symbols(ARCHIVE)
    paths=sorted((ARCHIVE/'price_raw').glob('*.parquet'))
    lineage_exclusions=exclusions(paths)
    quarantined={s for r in lineage_exclusions for s in r['matched_symbols']}
    files=[p for p in paths if p.stem not in blocked and p.stem not in quarantined and p.stem not in ('SPY','QQQ')]
    frames=[];sources=[]
    for path in files:
        d=normalize(path)
        # Explicit previously exposed development window. No 2025/2026 or sealed forward.
        d=d[d.date.between('2022-01-01','2024-12-31')]
        if len(d): frames.append(d)
        sources.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    p,excluded=build(frames)
    refs={}
    for symbol in ('SPY','QQQ'):
        path=ARCHIVE/'price_raw'/f'{symbol}.parquet'
        if symbol == 'SPY' and not path.exists():
            from .benchmarks import DEFAULT_SPY
            path=DEFAULT_SPY
        if path.exists():
            d=normalize(path);refs[symbol]=d.set_index('date').reindex(p.dates)
            sources.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    if 'QQQ' not in refs:
        from .alpaca_repair import reuse_benchmark
        cache=Path(__file__).parent/'artifacts/alpaca_repair_live_batch_20261029'
        if cache.exists():
            raw=reuse_benchmark(cache);bars=[]
            for source in raw['sources']:
                bars.extend(json.loads(Path(source['source_file']).read_text()).get('bars',{}).get('QQQ',[]))
                sources.append(source)
            if bars:
                d=pd.DataFrame(bars).rename(columns={'o':'open','c':'close'})
                d['date']=pd.to_datetime(d.t,utc=True).dt.tz_convert('America/New_York').dt.tz_localize(None).dt.normalize()
                if d.groupby('date')[['open','close']].nunique().gt(1).any().any():
                    raise ValueError('Conflicting cached QQQ marks')
                refs['QQQ']=d.drop_duplicates('date').set_index('date').reindex(p.dates)
    return p,dict(kind='available_real_historical',sources=sources,excluded_incomplete=excluded,
                  lineage_exclusions=lineage_exclusions,
                  excluded_lineage_count=len(lineage_exclusions),
                  excluded_lineage_symbol_count=len(quarantined),
                  cohort='all available archive symbols outside protected identities; causal observed-bar eligibility; membership unverified',
                  limitations=['survivorship and cohort selection bias','PIT eligibility and delisting outcomes unverified',
                               'zero distributions assumed; raw vendor split normalization unverified','peer sessions not independent calendar']),refs


def precursor(p, cutoff, horizon=40):
    """Train snapshots before runup, including failed lookalikes in same causal bins."""
    y=np.full(p.close.shape,np.nan); event=np.zeros(p.close.shape,bool);failed=event.copy()
    for t in range(60,cutoff-horizon-1):
        entry=p.open[t+1]*1.00060005
        y[t]=p.open[t+horizon+1]*.99940005/entry-1
        peak=np.max(p.close[t+1:t+horizon+1],axis=0)/entry-1
        early=(p.close[t]/p.close[t-20]-1<.08)&(p.close[t]/p.close[t-20]-1>-.10)
        event[t]=early&(peak>=.20)&(y[t]>0)
        failed[t]=early&(y[t]<=0)
    return y,event,failed


def model_signal(p,family,cutoff,horizon):
    y,event,failed=precursor(p,cutoff,horizon)
    z=p.features[family]; bins=np.digitize(np.nan_to_num(z,nan=-1e10),[-1,0,.5,1,2])
    expectation=np.zeros(6);rows=[]
    for b in range(6):
        m=(bins==b)&np.isfinite(z)&np.isfinite(y)
        e=m&event; f=m&failed
        # All nonwinners remain controls in exactly the same causal score bin.
        raw_mean=float(y[m].mean()) if m.sum()>=25 else 0.
        probability=float(e.sum()/max(1,m.sum()));failure=float(f.sum()/max(1,m.sum()))
        expectation[b]=raw_mean*(.5+.5*probability)-.001*failure if m.sum()>=25 else 0.
        rows.append(dict(bin=b,samples=int(m.sum()),precursors=int(e.sum()),failed_lookalikes=int(f.sum()),
                         nonwinners=int((m&~event).sum()),precursor_probability=probability,failed_probability=failure,raw_expected_net_return=raw_mean,precursor_adjusted_edge=expectation[b]))
    signal=np.where(np.isfinite(z)&(expectation[bins]>0),expectation[bins]/horizon,-np.inf)[None]
    return signal,dict(family=family,horizon=horizon,cutoff=str(p.dates[cutoff].date()),
                       latest_label_endpoint=str(p.dates[cutoff-1].date()),bins=rows)


def comparison(refs,p,a,b,metrics):
    result={}
    for name in ('SPY','QQQ'):
        d=refs.get(name)
        if d is None:
            result[name]=dict(status='MISSING',net_cagr=None); continue
        # Same account start/first executable open/final mark and entry cost; residual held.
        rows=d.iloc[a:b]
        if len(rows)<2 or not np.isfinite(rows[['open','close']]).all().all() or (rows[['open','close']]<=0).any().any():
            result[name]=dict(status='MISSING_MATCHED_MARKS',net_cagr=None);continue
        nav=np.r_[100000.,100000*rows.close.to_numpy()[1:]/(rows.open.iloc[1]*1.00060005)]
        cagr=float((nav[-1]/nav[0])**(252/len(nav))-1)
        result[name]=dict(status='AVAILABLE_UNCERTIFIED_PRICE_RETURN',net_cagr=cagr,excess_cagr=metrics['cagr']-cagr)
    available=all(result[n]['net_cagr'] is not None for n in ('SPY','QQQ'))
    return dict(benchmarks=result,target_met=bool(available and target(metrics['cagr'],result['SPY']['net_cagr'],result['QQQ']['net_cagr'],metrics['max_drawdown'])),
                status='COMPARED_UNCERTIFIED' if available else 'MISSING_BENCHMARKS_NO_SUCCESS')


def edge_manager(manager):
    """Adapt rank genomes to absolute return/session units; retain capital gates."""
    return replace(manager, niche_bias=(0., 0., 0.), specialist_bias=(),
                   entry_floor=0., replacement=.0001, score_size=0.,
                   exit_floor=0., reduce_floor=-1e30)


def experiment(out,kind,seconds=120,evaluations=48,attempts=3, repair=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    # Durable reservation is owned by supervisor. Never resume partially executed experiments.
    p,provenance,refs=inputs(kind)
    atomic(out/'inputs.json',dict(label=LABEL,certified=False,promotion_allowed=False,**provenance,
                                 dates=[str(p.dates[0].date()),str(p.dates[-1].date())],symbols=p.symbols))
    folds=[(int(len(p.dates)*.5),int(len(p.dates)*.75)),(int(len(p.dates)*.75),len(p.dates))]
    rng=random.Random(91029);begin=time.monotonic();used=0;best=None;history=[];cache={};generation=0;best_result=None
    total_fills=0;positive_forecasts=0;best_active=None
    stop_reason='resource_budget';base=Manager(slots=6,reserve=.3,risk_cap=.02,replacement=.0001)
    for attempt in range(attempts):
        stale=0;parent=best['manager'] if best else base
        while time.monotonic()-begin<seconds and used<evaluations:
            generation+=1;improved=False
            for child in range(4):
                if time.monotonic()-begin>=seconds or used>=evaluations:break
                manager=parent if child==0 else mutate(parent,rng)
                if repair == 'edge_units_v2': manager=edge_manager(manager)
                family=FAMILIES[(generation+child+attempt)%len(FAMILIES)];horizon=(20,40,60)[attempt%3]
                rows=[];score=[];models=[];replays=[]
                for a,b in folds:
                    key=(family,a,horizon)
                    if key not in cache:cache[key]=model_signal(p,family,a,horizon)
                    signal,model=cache[key];models.append(model)
                    z=replay(p,[Gene(family,threshold=0,hold_sessions=horizon,weight=.06)],manager,p.dates[a],p.dates[b-1]+pd.Timedelta(days=1),
                             detail=True,signal=signal,hold_signal=signal,edge_mode=True,absolute_edges=True)
                    m=z['metrics'];total_fills+=m['fills']
                    positive_forecasts+=int(np.count_nonzero(np.isfinite(signal[:,a:b]) & (signal[:,a:b]>0)))
                    comp=comparison(refs,p,a,b,m)
                    bench=[v['net_cagr'] for v in comp['benchmarks'].values() if v['net_cagr'] is not None]
                    score.append(m['cagr']-(max(bench) if bench else 0)-2*m['max_drawdown']-(0 if m['feasible'] else 10))
                    rows.append(dict(start=str(p.dates[a].date()),end_exclusive=str((p.dates[b-1]+pd.Timedelta(days=1)).date()),metrics=m,**comp));replays.append(z)
                used+=1;fitness=float(min(score));meaningful=best is None or fitness>best['fitness']+1e-5
                row=dict(label=LABEL,certified=False,attempt=attempt+1,generation=generation,evaluation=used,family=family,horizon=horizon,
                         manager=asdict(manager),fitness=fitness,folds=rows,meaningful_progress=meaningful)
                with (out/'evaluations.jsonl').open('a') as f:
                    f.write(json.dumps(row,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
                if all(r['metrics']['fills']>0 for r in rows) and (best_active is None or fitness>best_active['fitness']):
                    best_active=row
                    atomic(out/'best_active.json',dict(**row,models=models,replays=replays))
                if meaningful:
                    best=dict(fitness=fitness,manager=manager);best_result=row;parent=manager;improved=True
                    atomic(out/'best.json',dict(**row,models=models,replays=replays))
                atomic(out/'progress.json',dict(label=LABEL,evaluations=used,generation=generation,attempt=attempt+1,best_fitness=best['fitness'],elapsed_seconds=time.monotonic()-begin))
            stale=0 if improved else stale+1
            if stale>=2:
                history.append(dict(attempt=attempt+1,reason='NO_MEANINGFUL_PROGRESS',diagnosis='No worst-fold net risk-adjusted improvement for two generations',
                                    bounded_repair='Change label horizon, reseed candidate families and mutate best manager; no code rewriting or sealed data'))
                break
        else:
            stop_reason='resource_budget';break
        if attempt==attempts-1:stop_reason='bounded_repairs_exhausted'
    report=dict(label=LABEL,certified=False,promotion_allowed=False,production_allowed=False,final_validation_allowed=False,
                dataset=kind,status='HALTED',stop_reason=stop_reason,evaluations=used,generations=generation,attempts=attempt+1,
                elapsed_seconds=time.monotonic()-begin,repairs=history,best=best_result,
                repair_profile=repair,total_fills=total_fills,positive_forecasts=positive_forecasts,best_active=best_active,
                benchmark_status='MISSING_BENCHMARKS_NO_SUCCESS' if not all(n in refs for n in ('SPY','QQQ')) else 'UNCERTIFIED',
                target_met=False if best_result is None else all(r['target_met'] for r in best_result['folds']),
                llm_spend_usd=0,limitations=['Development folds reused for evolutionary selection; not out-of-sample certification',
                 'Precursor definition fixed: 20-session prior move -10% to +8%, future peak +20%; failed matched-bin controls terminal net <=0',
                 'Uninvested cash zero yield; fixed 5bp slippage +1bp fee each side; conservative T+2; terminal positions marked, not liquidated',
                 'No promotion, final evaluation, production, data acquisition or Codex invocation path'])
    atomic(out/'report.json',report)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',required=True);p.add_argument('--kind',choices=['synthetic','real'],required=True)
    p.add_argument('--seconds',type=float,default=120);p.add_argument('--evaluations',type=int,default=48)
    p.add_argument('--repair',choices=['edge_units_v2'])
    a=p.parse_args()
    if not 0<a.seconds<=300 or not 1<=a.evaluations<=96:p.error('Resource budget out of bounds')
    print(json.dumps(experiment(a.output,a.kind,a.seconds,a.evaluations,repair=a.repair),allow_nan=False))
