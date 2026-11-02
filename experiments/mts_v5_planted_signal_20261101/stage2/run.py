#!/usr/bin/env python3
"""Bounded Stage 2; imports actual kernel and experiment-local manager patch."""
from dataclasses import replace
import sys, importlib.util, hashlib, json, time, statistics as st, csv
from pathlib import Path
ROOT=Path('/opt/Momentum-Trading-System_v5-alpha')
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import discovery.competitive_ga.functional_niche_manager as original
spec=importlib.util.spec_from_file_location('discovery.competitive_ga.stage2_manager',OUT/'functional_niche_manager.py')
patched=importlib.util.module_from_spec(spec);sys.modules[spec.name]=patched;spec.loader.exec_module(patched)
spec=importlib.util.spec_from_file_location('stage1',OUT.parent/'run.py')
s1=importlib.util.module_from_spec(spec);spec.loader.exec_module(s1)
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.progressive_scaling import ScaleEvidence

VARIANTS=('ev','risk','cluster','hysteresis','scale15','scale20')
QUALITIES=('strong','weak','misnull')

def callbacks(tape,q,v,seed,days):
    # Misnull deliberately (and incorrectly) treats independent null predictor as strong.
    quality='strong' if q=='misnull' else q
    classify,eligible,base,ev,counts=s1.callback_factory(tape,quality,'baseline',seed)
    idx={d:i for i,d in enumerate(s1.DATES)}
    net=[[s1.expected(p,quality)-s1.ROUND_TRIP for p in row] for row in tape]
    stats={'add_requests':0,'evidence_calls':0,'evidence_15_pass':0,'evidence_20_pass':0}
    streak=[0]*s1.K;last=[-1]*s1.K
    def native(c,t,d,held):
        i=idx[d];j=int(t[3:]);p=base(c,t,d,held)
        if last[j]!=i:
            streak[j]=streak[j]+1 if net[i][j]>0 else 0;last[j]=i
        if v=='hysteresis' and p and p.action=='ENTER' and streak[j]<3:return None
        if v.startswith('scale') and held and p and p.action=='HOLD' and net[i][j]>0:
            target=.15 if v=='scale15' else .20
            if held['weight']<target-1e-6:
                stats['add_requests']+=1
                return replace(p,action='ADD',target_weight=target)
        return p
    def priority(c,t,d,control,matches,value):
        j=int(t[3:]);row=net[idx[d]]
        if v=='risk':return value/(max(.02,s1.GAPS[j])+s1.ROUND_TRIP)
        if v=='cluster':return value/(1+sum(x>0 for x in row[j//6*6:j//6*6+6]))
        return value
    def evidence(c,t,d,held,realized,nav):
        stats['evidence_calls']+=1
        # Only funded completed trades through this close, grouped in fixed 63-session folds.
        folds={}
        for r in realized:folds.setdefault(idx[r['date']]//63,[]).append(r['return'])
        # Current partial fold is excluded from forward fold evidence.
        positive_folds=sum(k<idx[d]//63 and st.mean(values)>0 for k,values in folds.items())
        peak=s1.INITIAL;mdd=0
        for r in nav:peak=max(peak,r[1]);mdd=max(mdd,1-r[1]/peak)
        positive=bool(realized) and st.mean(r['return'] for r in realized)>0
        e=ScaleEvidence(len(realized),positive_folds,positive,mdd,True,days[idx[d]][1][t].close>held['entry']*(1+s1.COSTS['fees']),False)
        stats['evidence_15_pass']+=int(e.matured_trades>=30 and positive and e.position_profitable)
        stats['evidence_20_pass']+=int(e.matured_trades>=50 and positive_folds>=2 and positive and mdd<=.20 and e.position_profitable)
        return e
    return dict(classify=classify,eligible=eligible,native=native,conditional_ev=ev,allocation_priority=priority,scaling_evidence=evidence if v.startswith('scale') else None),stats

def execute(days,kwargs,manager=patched):
    if manager is patched:
        kwargs=dict(kwargs)
        classify=kwargs['classify']
        kwargs['classify']=lambda t,d:patched.NicheObservation(**vars(classify(t,d)))
    candidates=[patched.Candidate(t,'GA7','synthetic',.02,s1.GAPS[j]) for j,t in enumerate(s1.TICKERS)]
    return manager.run_slice(days,candidates,max_sessions=252,max_stocks=24,**s1.COSTS,**kwargs)

def write(name,rows):
    if rows:
        with (OUT/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    start=time.monotonic();rows=[];compat=[];cal=[];tapes_sha=[]
    sources=[Path(original.__file__),Path(sys.modules[s1.Replay.__module__].__file__),ROOT/'discovery/competitive_ga/progressive_scaling.py']
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    for seed in s1.SEEDS:
        if time.monotonic()-start>840:raise RuntimeError('bounded runtime stop')
        days,tapes,returns=s1.generate(seed)
        # One original/default pair per seed; original run counts toward hard budget.
        cl,el,na,ev,_=s1.callback_factory(tapes['strong'],'strong','baseline',seed)
        kw=dict(classify=cl,eligible=el,native=na,conditional_ev=ev)
        old=execute(days,kw,original);new=execute(days,kw)
        for audit in new['decisions']:
            for key in ('marginal_net_ev','allocation_priority','scaling_evidence'):audit.pop(key,None)
        assert old==new,'default behavior changed'
        compat.append(seed)
        for q in QUALITIES:
            tape=tapes['null' if q=='misnull' else q]
            tapes_sha.append(dict(seed=seed,quality=q,sha256=hashlib.sha256(json.dumps(tape).encode()).hexdigest()))
            quality='strong' if q=='misnull' else q
            c,_=s1.calibration(seed,quality,tape,returns);c['quality']=q;cal.append(c)
            for v in VARIANTS:
                kw,stats=callbacks(tape,q,v,seed,days)
                r=execute(days,kw);m,daily=s1.measure(r,days)
                # Funded weights checked at close; drift can exceed target, so report separately.
                maxw=max((q*dict(days)[d][t].close/nav for d,nav,cash,shares,defense in r['nav'] for t,q in shares.items()),default=0)
                scaled=sum(a['allowed']>.10001 and a['allowed']>0 for a in r['risk_audit'])
                rows.append(dict(seed=seed,quality=q,variant=v,**m,**stats,scaled_risk_admissions=scaled,max_close_position_weight=maxw))
                if seed==1101:
                    write(f'{q}_{v}_daily.csv',daily)
                    write(f'{q}_{v}_fills.csv',[dict(date=f[0],ticker=f[1],side=f[2],quantity=f[3],price=f[4],fee=f[5]) for f in r['ledger']])
        print(f'seed {seed}; portfolio executions {len(rows)+2*len(compat)}; elapsed {time.monotonic()-start:.1f}s',flush=True)
    paired=[];agg=[]
    metrics=('cagr','mdd','turnover','exposure','fills','scaled_risk_admissions','max_close_position_weight')
    for q in QUALITIES:
        for v in VARIANTS:
            rr=[r for r in rows if r['quality']==q and r['variant']==v]
            agg.append(dict(quality=q,variant=v,n=len(rr),**{k:st.mean(r[k] for r in rr) for k in metrics},evidence_15_pass=sum(r['evidence_15_pass'] for r in rr),evidence_20_pass=sum(r['evidence_20_pass'] for r in rr)))
            if v=='ev':continue
            deltas={k:[] for k in metrics}
            for r in rr:
                b=next(x for x in rows if x['seed']==r['seed'] and x['quality']==q and x['variant']=='ev')
                for k in metrics:deltas[k].append(r[k]-b[k])
            paired.append(dict(quality=q,variant=v,n=len(rr),cagr_wins=sum(x>1e-12 for x in deltas['cagr']),**{k+'_delta':st.mean(values) for k,values in deltas.items()},cagr_delta_sd=st.stdev(deltas['cagr'])))
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==before[str(p)] for p in sources)
    write('runs.csv',rows);write('aggregate.csv',agg);write('paired.csv',paired);write('calibration.csv',cal)
    report=dict(stage=2,portfolio_executions=len(rows)+24,comparison_portfolios=len(rows),compatibility_seeds=compat,sessions=252,seeds=list(s1.SEEDS),elapsed_seconds=time.monotonic()-start,source_sha256=before,tapes=tapes_sha,aggregates=agg,paired=paired,calibration=cal,policy_probes=s1.policy_probes(),failures=[],limits=['Synthetic planted signals, no historic alpha or native-model forecast validation.','Scaling evidence pools causal funded exits across invented assets; forward folds are fixed chronological blocks, not independent validation.','Scaling does not guarantee a target is funded; cash, evidence, other-position risk and per-position loss gates can block adds.','Close weights drift; target cap is not a continuous concentration rebalance.','2% ordinary gate is per-position modeled risk, not guaranteed portfolio loss.','Cluster penalty counts opportunities, not covariance or funded marginal risk.','No terminal liquidation; one-session calibration differs from native holding P&L.'])
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
