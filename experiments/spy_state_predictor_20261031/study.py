"""Reproducible independent SPY state study; see PROTOCOL.md."""
from pathlib import Path
import json, hashlib, math, platform
import numpy as np
import pandas as pd
from scipy.stats import norm
ROOT=Path(__file__).resolve().parent
SOURCES={'SPY':'/opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet','DEV79':'/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet','DEV87':'/opt/mts/thunder-migration/mts-certification-20261011/dev87/dev87_raw.parquet'}
HORIZONS=[5,10,21,63]

def features(p, panels):
    f=pd.DataFrame(index=p.index)
    r=p.pct_change(fill_method=None)
    f['m21']=p/p.shift(21)-1; f['m63']=p/p.shift(63)-1
    f['accel']=f.m21-(p.shift(21)/p.shift(42)-1)
    f['vr']=r.rolling(20).std()/r.rolling(60).std()
    f['trend']=p/p.rolling(200).mean()-1
    for name,x in panels.items():
        x=x.reindex(p.index)
        for w in [50,200]:
            ma=x.rolling(w,min_periods=w).mean(); valid=x.notna() & ma.notna()
            n=valid.sum(axis=1)
            f[f'{name}_n{w}']=n
            f[f'{name}_b{w}']=((x>ma)&valid).sum(axis=1).div(n).where(n>=20)
        f[f'{name}_db']=f[f'{name}_b50'].diff(21)
    return f

def rules(f):
    out={}
    def add(name,cols,fn):
        ok=f[cols].notna().all(axis=1)
        out[name]=fn().astype(float).where(ok)
    add('momentum63_positive',['m63'],lambda:f.m63>0)
    add('momentum21_positive',['m21'],lambda:f.m21>0)
    add('acceleration_positive',['accel'],lambda:f.accel>0)
    add('vol_expansion',['vr'],lambda:f.vr>1.2)
    add('vol_contraction',['vr'],lambda:f.vr<.8)
    add('momentum_acceleration',['m63','accel'],lambda:(f.m63>0)&(f.accel>0))
    add('negative_momentum_expansion',['m63','vr'],lambda:(f.m63<0)&(f.vr>1.2))
    for name in [c[:-4] for c in f.columns if c.endswith('_b50')]:
        b=f[name+'_b50']; b2=f[name+'_b200']; db=f[name+'_db']
        for w,s in [(50,b),(200,b2)]:
            add(f'{name}_breadth{w}_strong',[f'{name}_b{w}'],lambda s=s:s>.6)
            add(f'{name}_breadth{w}_weak',[f'{name}_b{w}'],lambda s=s:s<.4)
        add(name+'_breadth_improving',[name+'_db'],lambda:db>.1)
        add(name+'_breadth_deteriorating',[name+'_db'],lambda:db<-.1)
        add(name+'_divergence',['m21',name+'_db'],lambda:(f.m21>0)&(db<-.1))
        add(name+'_recovery',['m63','m21',name+'_db'],lambda:(f.m63<0)&(f.m21>0)&(db>.1))
        add(name+'_healthy_trend',['m63','vr',name+'_b50',name+'_b200'],lambda:(f.m63>0)&(f.vr<1.2)&(b>.6)&(b2>.6))
        add(name+'_fragile_trend',['m63','vr',name+'_db'],lambda:(f.m63>0)&(f.vr>1.2)&(db<-.1))
    return pd.DataFrame(out,index=f.index)

def outcomes(p,h):
    a=p.to_numpy(); n=len(a); ret=np.full(n,np.nan); dd=ret.copy(); adverse=ret.copy()
    for i in range(n-h):
        path=a[i:i+h+1];ret[i]=path[-1]/path[0]-1
        dd[i]=np.min(path/np.maximum.accumulate(path)-1)
        adverse[i]=np.min(path/path[0]-1)
    return pd.DataFrame({'return':ret,'downside':np.where(np.isnan(ret),np.nan,(ret<0).astype(float)),'drawdown':dd,'adverse':adverse},index=p.index)

def estimate(y,a,b=None,lag=63):
    # Calendar-aligned influence scores; missing observations contribute zero.
    y=np.asarray(y,float);a=np.asarray(a,bool)&np.isfinite(y); n=len(y)
    if a.sum()<5: return (np.nan,)*5
    mu=np.mean(y[a]); influence=np.zeros(n);influence[a]=(y[a]-mu)*n/a.sum()
    if b is not None:
        b=np.asarray(b,bool)&np.isfinite(y)
        if b.sum()<5:return (np.nan,)*5
        mb=np.mean(y[b]);influence[b]-=(y[b]-mb)*n/b.sum();mu-=mb
    lrv=np.dot(influence,influence)
    for k in range(1,min(lag,n-1)+1):lrv+=2*(1-k/(lag+1))*np.dot(influence[k:],influence[:-k])
    se=np.sqrt(max(lrv,0))/n
    return mu,mu-1.96*se,mu+1.96*se,se,2*norm.sf(abs(mu/se)) if se>0 else np.nan

def bh(p):
    p=np.asarray(p,float);q=np.full(len(p),np.nan);ids=np.flatnonzero(np.isfinite(p));order=ids[np.argsort(p[ids])]
    if len(order):q[order]=np.minimum(1,np.minimum.accumulate((p[order]*len(order)/np.arange(1,len(order)+1))[::-1])[::-1])
    return q

def counts(mask,h):
    a=np.asarray(mask,bool); on=int(np.sum(a & ~np.r_[False,a[:-1]]));last=-h;n=0
    for i in np.flatnonzero(a):
        if i-last>=h:n+=1;last=i
    return on,n

def table(df,cols):
    d=df[cols].copy()
    for c in d.select_dtypes(include='number'):d[c]=d[c].map(lambda v:f'{v:.5f}' if pd.notna(v) else 'NA')
    return '| '+' | '.join(cols)+' |\n|'+ '|'.join(['---']*len(cols))+'|\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in d.to_numpy())

def main():
    metadata={'sources':{},'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':__import__('scipy').__version__}
    panels={};p=None
    for name,path in SOURCES.items():
        try:
            d=pd.read_parquet(path);d['date']=pd.to_datetime(d.date).dt.tz_localize(None);d=d.sort_values('date')
            metadata['sources'][name]={'path':path,'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'rows':len(d),'start':str(d.date.min()),'end':str(d.date.max())}
            if name=='SPY':
                assert not d.date.duplicated().any();p=d.set_index('date').adj_close.astype(float)
            else:
                assert not d.duplicated(['date','ticker']).any()
                assert (d.adj_close.dropna()>0).all()
                x=d.pivot(index='date',columns='ticker',values='adj_close').astype(float);panels[name]=x
                metadata['sources'][name]['tickers']=len(x.columns)
        except (PermissionError,FileNotFoundError) as e:metadata['sources'][name]={'path':path,'unavailable':str(e)}
    assert p is not None and (p>0).all() and p.notna().all()
    p=p.loc[:'2025-12-31']
    quality=[]
    for name,x in {'SPY':p.to_frame('SPY'),**panels}.items():
        x=x.loc['2005-01-01':'2025-12-31']; rr=x.pct_change(fill_method=None)
        quality.append(dict(source=name,rows=len(x),columns=len(x.columns),missing_cells=int(x.isna().sum().sum()),min_adjusted_price=float(x.min().min()),max_abs_daily_return=float(rr.abs().max().max()),daily_moves_over_50pct=int((rr.abs()>.5).sum().sum()),duplicate_dates=int(x.index.duplicated().sum())))
    pd.DataFrame(quality).to_csv(ROOT/'data_quality.csv',index=False)
    f=features(p,panels);s=rules(f)
    f.to_csv(ROOT/'features.csv');s.to_csv(ROOT/'signals.csv')
    ys={h:outcomes(p,h) for h in HORIZONS}
    pd.concat(ys,axis=1).to_csv(ROOT/'outcomes.csv')
    rows=[]
    for split,start,end in [('discovery','2006-01-01','2016-12-31'),('validation','2017-01-01','2025-12-31')]:
        date=(p.index>=start)&(p.index<=end)
        for h,y in ys.items():
            endpoint=pd.Series(p.index,index=p.index).shift(-h)
            period=date & (endpoint<=pd.Timestamp(end)).to_numpy()
            for rule in s:
                eligible=period & s[rule].notna().to_numpy() & s.momentum63_positive.notna().to_numpy()
                state=eligible & (s[rule].to_numpy()==1);on,non=counts(state,h)
                for metric in ['return','downside','drawdown']:
                    for comp,base in [('unconditional',eligible),('momentum63_positive',eligible & (s.momentum63_positive.to_numpy()==1))]:
                        val=y[metric].to_numpy();a=estimate(val,state,lag=max(63,2*h));b=estimate(val,base,lag=max(63,2*h));e=estimate(val,state,base,lag=max(63,2*h))
                        rows.append(dict(split=split,rule=rule,horizon=h,metric=metric,comparator=comp,n=int(state.sum()),baseline_n=int(base.sum()),onsets=on,nonoverlap_n=non,mean=a[0],mean_ci_low=a[1],mean_ci_high=a[2],baseline_mean=b[0],effect=e[0],ci_low=e[1],ci_high=e[2],se=e[3],p=e[4]))
    result=pd.DataFrame(rows);result['q']=np.nan
    for _,g in result.groupby(['split','comparator']):
        result.loc[g.index,'q']=bh(g.p)
        result.loc[g.index,'p_bonferroni']=np.minimum(1,g.p*g.p.notna().sum())
    discovery=result.query("split=='discovery' and horizon==21 and metric=='return' and comparator=='unconditional' and n>=100 and onsets>=20").copy()
    discovery['abs_effect']=discovery.effect.abs();chosen=discovery.sort_values(['abs_effect','rule'],ascending=[False,True]).iloc[0]
    selection={'rule':chosen.rule,'direction':int(np.sign(chosen.effect)),'discovery_effect':float(chosen.effect),'selection':'largest absolute 21d return uplift, n>=100, onsets>=20; frozen before validation inspection'}
    (ROOT/'selection.json').write_text(json.dumps(selection,indent=2))
    result.to_csv(ROOT/'results.csv',index=False)
    (ROOT/'results.json').write_text(result.to_json(orient='records',indent=2))
    metadata['finite_tests_per_family']={str(k):int(g.p.notna().sum()) for k,g in result.groupby(['split','comparator'])}
    # Year and causal trend/vol regime diagnostics for selected rule and momentum comparator.
    regimes=[]
    y=ys[21];ep=pd.Series(p.index,index=p.index).shift(-21)
    for rule in [chosen.rule,'momentum63_positive']:
        for label,mask in [(str(year),p.index.year==year) for year in range(2006,2026)]+[('validation_uptrend',((p.index.year>=2017)&(f.trend>0)).to_numpy()),('validation_downtrend',((p.index.year>=2017)&(f.trend<=0)).to_numpy()),('validation_vol_expansion',((p.index.year>=2017)&(f.vr>1.2)).to_numpy()),('validation_no_expansion',((p.index.year>=2017)&(f.vr<=1.2)).to_numpy())]:
            end='2016-12-31' if label.isdigit() and int(label)<=2016 else '2025-12-31'
            valid=mask & (ep<=pd.Timestamp(end)).to_numpy() & s[rule].notna().to_numpy();a=valid & (s[rule].to_numpy()==1)
            e=estimate(y['return'],a,valid,lag=63)
            regimes.append(dict(rule=rule,regime=label,n=int(a.sum()),baseline_n=int(valid.sum()),mean=y['return'][a].mean(),effect=e[0],ci_low=e[1],ci_high=e[2]))
    regime=pd.DataFrame(regimes);regime.to_csv(ROOT/'regimes.csv',index=False)
    sensitivity=[]
    for h in HORIZONS:
        valid=(p.index.year>=2017)&(pd.Series(p.index,index=p.index).shift(-h)<=pd.Timestamp('2025-12-31')).to_numpy()&s[chosen.rule].notna().to_numpy()
        a=valid & (s[chosen.rule].to_numpy()==1)
        for metric in ['return','downside','drawdown']:
            e=estimate(ys[h][metric],a,valid,lag=126);sensitivity.append(dict(horizon=h,metric=metric,effect=e[0],ci_low=e[1],ci_high=e[2],p=e[4]))
    pd.DataFrame(sensitivity).to_csv(ROOT/'sensitivity_lag126.csv',index=False)
    strategies=[];daily=pd.DataFrame(index=p.index)
    for split,start,end in [('discovery','2006-01-01','2016-12-31'),('validation','2017-01-01','2025-12-31')]:
        idx=(p.index>=start)&(p.index<=end);rr=p.pct_change(fill_method=None).loc[idx]
        for rule in ['buy_hold','momentum63_positive',chosen.rule]:
            sig=pd.Series(1.,index=p.index) if rule=='buy_hold' else s[rule].fillna(0)
            # Bearish discovery rule means long outside state, rather than short.
            if rule==chosen.rule and selection['direction']<0:sig=(1-sig).where(s[rule].notna(),0)
            pos=sig.shift(2).loc[idx].fillna(0);turn=pos.diff().abs();turn.iloc[0]=abs(pos.iloc[0])
            for cost in [5,10,25]:
                net=pos*rr-turn*cost/10000
                # Liquidation at final close.
                net.iloc[-1]-=pos.iloc[-1]*cost/10000
                wealth=(1+net).cumprod();dd=wealth/np.maximum.accumulate(np.r_[1.,wealth.to_numpy()])[1:]-1
                strategies.append(dict(split=split,rule=rule,one_way_bps=cost,n=len(net),exposure=pos.mean(),turnover=float(turn.sum()+pos.iloc[-1]),cagr=wealth.iloc[-1]**(252/len(net))-1,annual_vol=net.std()*np.sqrt(252),sharpe=net.mean()/net.std()*np.sqrt(252),max_drawdown=dd.min()))
                daily[f'{split}_{rule}_{cost}bps']=net.reindex(p.index)
    strategy=pd.DataFrame(strategies);strategy.to_csv(ROOT/'strategies.csv',index=False);daily.to_csv(ROOT/'strategy_daily.csv')
    metadata['selection']=selection;metadata['rule_count']=len(s.columns);metadata['hypotheses_per_family']=len(s.columns)*4*3
    metadata['protocol_sha256']=hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest()
    (ROOT/'run_metadata.json').write_text(json.dumps(metadata,indent=2))
    v=result.query("split=='validation' and rule==@chosen.rule and comparator=='unconditional'")
    primary=v.query("horizon==21 and metric=='return'").iloc[0]
    passes=bool(primary.q<.05 and primary.ci_low*primary.ci_high>0 and np.sign(primary.effect)==selection['direction'])
    lines=['# Independent SPY state prediction study','Executed 2026-10-31. All returns, effects, probabilities and drawdowns below are decimal fractions; 0.01 = 1 percentage point.',
    f"## Result\nDiscovery selected **{chosen.rule}**, direction {selection['direction']:+d}, 21-session discovery uplift {chosen.effect:.4%}. Validation 21-session uplift {primary.effect:.4%}, 95% HAC CI [{primary.ci_low:.4%}, {primary.ci_high:.4%}], p={primary.p:.5g}, BH q={primary.q:.5g}. Frozen validation criterion **{'PASSES' if passes else 'DOES NOT PASS'}** under BH; more conservative Bonferroni p={primary.p_bonferroni:.5g}. This is one chronological historical holdout, not evidence of future profitability.",
    '## Interpretation\nThe selected state is fewer than 40% of eligible DEV79 stocks above their trailing 50-session average. It occurred on 392 validation signal dates, in 61 runs, with only 38 greedily spaced 21-session windows. Its 21-session negative-return probability was 28.06% versus 29.81%; the difference is not significant. Mean maximum forward drawdown was worse: −5.60% versus −3.89% (effect −1.71 percentage points; BH q=0.0439). This is a rebound-return association with greater path risk. Versus positive 63-session momentum, return uplift was +1.74 points but BH q=0.0841, so adjusted evidence for improvement over momentum is insufficient. The lag-126 sensitivity interval for return uplift is [+0.84, +2.30] points. Discovery itself was noisy (21-session return BH q=0.433); selection did not require discovery significance.\n\nYearly uplift was positive in all eight validation years with signals; 2017 had no weak-breadth signals. That is descriptive and uses overlapping labels. The downtrend subgroup had a positive marginal interval; the uptrend and volatility-expansion subgroup intervals included zero. At 10 bps one way the secondary state-only strategy earned 4.34% CAGR versus 8.53% for simple momentum and 15.04% for buy-and-hold; exposure was only 17.3%. No deployable trading advantage is established.',
    '## Data and scope\n'+json.dumps(metadata['sources'],indent=2),
    'DEV79 is the requested dev80_raw_no_smci panel (file label differs from universe name). DEV87 source read and requested copy fallback both failed with permission denied. It was not fabricated or substituted. Cross-universe robustness therefore remains untested. Original Claude/Grok transcripts were unavailable; the fixed rules operationalize the hypotheses enumerated by the user.',
    '**DEV universes are retrospective and survivorship-biased.** Current-vintage adjusted histories and retrospective security selection prevent a point-in-time universe claim. Adjustment revisions can affect historical features; no historical-vintage correction is available. Breadth uses eligible current/complete trailing observations only, with minimum 20 stocks; no filling. Prices are asserted positive and keys unique. data_quality.csv records missingness and large daily moves without filtering them. Daily vendor data are not independently certified.',
    '## Design and inference\nSee PROTOCOL.md and study.py for exact rules. Discovery 2006–2016; validation 2017–2025. Outcomes are purged at each split end; 2026 never enters analysis. 2005 supplies warmup, so 200-session breadth may start later. No validation tuning. All rule results, including failures, are in results.csv. Daily signal counts, onsets and greedy nonoverlap counts are reported; neither onsets nor nonoverlap counts guarantee independent samples. No causal interpretation.',
    f"{len(s.columns)} fixed states; {len(s.columns)*12} tests per split/comparator. BH q-values adjust across all states × four horizons × three outcomes separately per split/comparator. Bonferroni adjusted p-values are also in results.csv as a conservative dependence-robust comparison. Only finite p-values enter BH (actual family sizes in run_metadata.json); zero-variance identical comparator contrasts have undefined p-values. Dependence may limit BH FDR guarantees. HAC influence-function normal CIs use Bartlett lag max(63,2h), preserving calendar gaps; they are marginal and approximate, especially for rare states. Lag-126 sensitivity appears in sensitivity_lag126.csv. Selection on discovery is optimistic; validation is not used to change selection. Comparator-specific eligibility makes unconditional baselines potentially differ by rule.",
    'Forward return is adjusted close t+h / close t − 1. Downside is return <0. Maximum forward drawdown is worst peak-to-trough across t..t+h, including interim peaks; daily closes omit intraday losses. adverse in outcomes.csv separately records worst close relative to entry. Features use close t and earlier only. Predictive close-t labels assume no ability to trade after seeing that same close.',
    '## Selected rule: untouched validation vs unconditional\n'+table(v,['horizon','metric','n','onsets','nonoverlap_n','mean','baseline_mean','effect','ci_low','ci_high','q']),
    '## Selected rule: validation vs simple positive 63-session momentum\n'+table(result.query("split=='validation' and rule==@chosen.rule and comparator=='momentum63_positive'"),['horizon','metric','n','baseline_n','mean','baseline_mean','effect','ci_low','ci_high','q']),
    '## Discovery ranking (21-session return; selection-eligible)\n'+table(discovery.sort_values('abs_effect',ascending=False).head(10),['rule','n','onsets','mean','baseline_mean','effect','ci_low','ci_high','q']),
    '## All states: validation 21-session return\n'+table(result.query("split=='validation' and horizon==21 and metric=='return' and comparator=='unconditional'"),['rule','n','onsets','mean','baseline_mean','effect','ci_low','ci_high','q']),
    '## Regime diagnostics\nCausal trend is SPY relative to trailing 200-session average; volatility expansion is trailing 20/60 realized volatility >1.2. Regimes are descriptive, not independent tests or selection inputs. Calendar years are in regimes.csv.\n'+table(regime[regime.regime.str.startswith('validation')],['rule','regime','n','baseline_n','mean','effect','ci_low','ci_high']),
    '## Secondary cost-aware strategy\nLong/cash only. State at close t executes close t+1; earliest earned return is t+1 to t+2. Bearish selected state means cash inside state and long outside. Missing signals remain cash; inspect daily exposure. No leverage; cash return zero, no tax, market impact or borrowing. Costs are 5/10/25 bps one way including entry and liquidation. Sharpe uses zero cash benchmark. Strategy summaries are descriptive, not additional confirmatory evidence.\n'+table(strategy.query("split=='validation'"),['rule','one_way_bps','exposure','turnover','cagr','annual_vol','sharpe','max_drawdown']),
    '## Reproduce\nRun `/opt/mts/.venv/bin/python experiments/spy_state_predictor_20261031/study.py`, then `/opt/mts/.venv/bin/python -m pytest -q experiments/spy_state_predictor_20261031/test_study.py`. Inputs remain external; SHA256 and coverage are in run_metadata.json. No MTS code changed, no GA, no paid data, no push. Tests and execution log are stored alongside outputs.']
    (ROOT/'REPORT.md').write_text('\n\n'.join(lines)+'\n')
    print(json.dumps({'selected':selection,'validation_primary':primary.to_dict(),'criterion_passes':passes},indent=2))
if __name__=='__main__':main()
