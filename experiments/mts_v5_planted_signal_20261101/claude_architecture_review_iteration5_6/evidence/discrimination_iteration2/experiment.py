#!/usr/bin/env python3
"""Independent injected-signal diagnostic; no production writes or oracle decision inputs."""
import sys,json,math,random,statistics as st,time,subprocess,gzip,csv,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parent/'opportunity_evaluator_fix'))
import importlib.util
spec=importlib.util.spec_from_file_location('previous_evaluator',OUT.parent/'opportunity_evaluator_fix/experiment.py')
b=importlib.util.module_from_spec(spec);sys.modules[spec.name]=b;spec.loader.exec_module(b)
sys.path.remove(str(OUT.parent/'opportunity_evaluator_fix'))
m,k,r,s=b.m,b.k,b.r,b.s
TIERS,EDGES,tier,infer,observed=b.TIERS,b.EDGES,b.tier,b.infer,b.observed
sha=b.sha

def isotonic(values,weights):
    blocks=[]
    for i,(v,w) in enumerate(zip(values,weights)):
        blocks.append([i,i,v*w,w])
        while len(blocks)>1 and blocks[-2][2]/blocks[-2][3]>blocks[-1][2]/blocks[-1][3]:
            q=blocks.pop();p=blocks.pop();blocks.append([p[0],q[1],p[2]+q[2],p[3]+q[3]])
    result=[0.]*len(values)
    for lo,hi,v,w in blocks:result[lo:hi+1]=[v/w]*(hi-lo+1)
    return result

def generate(seed,scenario):
    """Truth separately returned for scoring. Sensors are injected noisy PIT measurements.

    Independent sensor RNG keeps tape outcomes identical across scenario variants.
    Sensor1 sd .30 and sensor2 sd .50 latent-class units; inverse-variance fusion.
    No observable change flag is provided at inversion.
    """
    rng=random.Random(seed);sensor=random.Random(seed+90000)
    coarse=[];features=[];pred=[];truth=[];rets=[];mu=(-.012,-.004,0.,.004,.012)
    for i in range(252):
        common=rng.gauss(0,.003);cc=[];ff=[];pp=[];tt=[];rr=[]
        for j in range(24):
            z=rng.randrange(5);c=z if rng.random()<.8 else rng.randrange(5)
            net=mu[z]+common+rng.gauss(0,.008)
            # Null: sensors and coarse feature independent of the outcome class.
            source=sensor.randrange(5) if scenario=='null' else z
            x=source+sensor.gauss(0,.30);y=source+sensor.gauss(0,.50)
            f=max(0,min(4,int(math.floor((x/.09+y/.25)/(1/.09+1/.25)+.5))))
            if scenario=='null':c=sensor.randrange(5)
            if scenario=='reversal' and i>=126:c=4-c;f=4-f
            prediction=.010-mu[c] if scenario in ('misleading','null','reversal') else mu[c]
            gross=(1+net)*(1+s.FRICTION)*(1+s.COSTS['fees'])/((1-s.FRICTION)*(1-s.COSTS['fees']))-1
            cc.append(c);ff.append(f);pp.append(prediction);tt.append(mu[z]);rr.append(gross)
        coarse.append(cc);features.append(ff);pred.append(pp);truth.append(tt);rets.append(rr)
    prices=[100.+j for j in range(24)];days=[]
    for i,d in enumerate(s.DATES):
        if i>=2:prices=[p*(1+v) for p,v in zip(prices,rets[i-2])]
        days.append((d,{t:k.Bar(prices[j],prices[j]) for j,t in enumerate(s.TICKERS)}))
    return days,coarse,features,pred,truth

def estimate(grouped):
    raw=[st.mean(v) if v else 0. for v in grouped];weights=[max(1,len(v)) for v in grouped]
    center=sum(v*w for v,w in zip(raw,weights))/sum(weights)
    slope=sum((i-2)*(v-center)*w for i,v,w in zip(range(5),raw,weights))/sum((i-2)**2*w for i,w in enumerate(weights))
    # Hierarchical shrinkage: six pseudo dates toward the learned linear parent.
    shrunk=[(v*w+6*(center+slope*(i-2)))/(w+6) for i,(v,w) in enumerate(zip(raw,weights))]
    sign=1 if slope>=0 else -1
    return [sign*v for v in isotonic([sign*v for v in shrunk],weights)]

def predict(days,features):
    ledger=[];states=[];alarms=[];quarantine=-1;floor=0
    bysignal={};residuals={}
    for now in range(252):
        for row in bysignal.get(now-3,[]):
            try:row['realized_net']=observed(days,row['index'],row['j']);row['missingness']='OBSERVED';row['available_index']=now
            except (KeyError,IndexError,TypeError):row['missingness']='MISSING'
        matured=[z for i in range(max(floor,now-93),now-2) for z in bysignal.get(i,[]) if z['missingness']=='OBSERVED']
        grouped=[];dated=[];cal=[];drift=[]
        for c in range(5):
            dates={}
            for z in matured:
                if z['signal']==c:dates.setdefault(z['index'],[]).append(z['realized_net'])
            dv=[(i,st.mean(v)) for i,v in sorted(dates.items())];dated.append(dv)
            grouped.append([v for _,v in dv]);cal.append([v for i,v in dv if i>=now-33])
            old=[v for i,v in dv if i<now-11];recent=[v for i,v in dv if i>=now-11]
            if len(old)>=24 and len(recent)>=7 and abs(st.mean(old)-st.mean(recent))>max(.004,3*math.hypot(b.se(old),b.se(recent))):drift.append(c)
        if drift and now>quarantine:
            alarms.append(dict(index=now,cells=drift));quarantine=now+20;floor=now-10
        means=estimate(grouped);identifiable=max(means)-min(means)>=.003
        cells=[]
        for c in range(5):
            values=grouped[c];cv=cal[c];mean=means[c]
            bias=abs(st.mean(cv)-mean) if cv else 1.
            radius=max(2.58*b.se(values),bias+1.64*b.se(cv)) if values and cv else 1.
            # Shrinkage displacement is additional model uncertainty, never hidden.
            if values:radius+=abs(mean-st.mean(values))
            ntrain=sum(i<now-33 for i,v in dated[c]);ncal=len(cv)
            label=infer(mean,radius,ntrain,ncal)
            # Causal rolling interval reliability of forecasts as issued, date clustered.
            rv=[]
            for i in range(max(0,now-63),now-2):
                rows=[z for z in bysignal.get(i,[]) if z['signal']==c and z['missingness']=='OBSERVED' and z['forecast_ready']]
                if rows:rv.append(st.mean(z['realized_net']-z['inferred_net'] for z in rows))
            reliability=st.mean(abs(v)<=.006 for v in rv) if rv else 0.
            reason='CONFIDENT'
            if now<=quarantine:reason='DRIFT_QUARANTINE'
            elif not identifiable:reason='NO_IDENTIFIABLE_SIGNAL'
            elif ntrain<20 or ncal<20:reason='INSUFFICIENT_MATURE_DATES'
            elif len(rv)>=20 and abs(st.mean(rv))>max(.003,2.58*b.se(rv)):reason='UNRELIABLE_RESIDUAL_BIAS'
            elif label=='UNKNOWN':reason='BOUNDARY_UNCERTAINTY'
            if reason!='CONFIDENT':label='UNKNOWN'
            cells.append(dict(mean=mean,radius=radius,ntrain=ntrain,ncal=ncal,label=label,reason=reason,reliability=reliability,reliability_dates=len(rv),latest_outcome_signal=max((i for i,v in dated[c]),default=-3)))
        states.append(cells)
        if now<250:
            rows=[]
            for j in range(24):
                c=cells[features[now][j]]
                rows.append(dict(index=now,j=j,signal=features[now][j],execution_index=now+1,maturity_index=now+2,available_index=None,realized_net=None,missingness='PENDING',inferred_net=c['mean'],radius=c['radius'],inferred_tier=c['label'],reason=c['reason'],forecast_ready=min(c['ntrain'],c['ncal'])>=20))
            ledger.extend(rows);bysignal[now]=rows
    return states,ledger,alarms

def writecsv(name,rows):
    if not rows:return
    with (OUT/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def diagnose():
    """Prior saved outcomes only; descriptive attribution, no portfolio/tuning."""
    reasons={};cells={};unknown=0;center_middle=0;narrow=0;gate_middle=0
    p=OUT.parent/'opportunity_evaluator_fix/opportunities.jsonl.gz'
    with gzip.open(p,'rt') as f:
        for line in f:
            z=json.loads(line)
            if not 126<=z['index']<250:continue
            reason=z['reason'];reasons[reason]=reasons.get(reason,0)+1
            key=(z['scenario'],z['signal']);v=cells.setdefault(key,[])
            if z['realized_net'] is not None:v.append(z['realized_net'])
            if z['inferred_tier']=='UNKNOWN':
                unknown+=1
                if tier(z['inferred_net']) in TIERS[1:4]:
                    center_middle+=1
                    if z['radius']<.002:narrow+=1
                    if b.tier(z['inferred_net']-z['radius'])==b.tier(z['inferred_net']+z['radius']):gate_middle+=1
    return dict(prior_reasons=reasons,unknown=unknown,middle_center_unknown=center_middle,middle_center_radius_below_half_band=narrow,middle_interval_fits_but_gated=gate_middle,realized_cell_means={str(k):st.mean(v) for k,v in cells.items()},conclusions=['No tier dispatch bug: absolute infer emits all five tiers in unit tests. Bands are disjoint, not overlapping.','80% faithful coarse sensor mixes neighboring latent states; conditional cell EV is not individual latent EV.','Middle bands have half-width .002. Diagnostic radius and window bias dominate when center lies near boundaries.','All samples are date clustered: 24 stocks are not 24 independent dates. Prior recent calibration has at most 21 dates.','Global quarantine and signal-identifiability gates additionally suppress coverage; counters isolate these from interval rejection.','Original manager delegates quality to caller conditional_ev; causal ledger handles outcome availability, not inference validity.'])

def main():
    start=time.monotonic();plan=json.loads((OUT/'preregister.json').read_text());ph=sha(OUT/'preregister.json')
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(OUT),'-p','test_*.py','-v'],capture_output=True,text=True)
    (OUT/'tests.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        (OUT/'report.json').write_text(json.dumps(dict(status='STOP_TEST_FAILURE',full_portfolio_replays=0)));raise SystemExit(result.returncode)
    sources=list(b.a.SOURCES)+[b.PRIOR/'corrected_manager.py',b.PRIOR/'corrected_kernel.py',Path(b.__file__),OUT/'experiment.py',OUT/'test_iteration2.py',OUT/'preregister.json']
    sources+=list((OUT.parent/'five_tier_discrimination').glob('*.py'))
    sources+=[OUT.parent/'five_tier_discrimination/report.json',OUT.parent/'opportunity_evaluator_fix/report.json',OUT.parent.parent/'mts_v5_manager_repair_20261031/v5_working_copy/engines/counterfactual_learning/causal_ledger.py']
    before={str(p):sha(p) for p in sources};diagnosis=diagnose();scores=[];metrics=[];attempts=0;opps=[];riskmax=0.;buys=0
    with gzip.open(OUT/'opportunities.jsonl.gz','wt') as of,gzip.open(OUT/'replays.jsonl.gz','wt') as rf:
        for seed in plan['seeds']:
            for scenario in plan['scenarios']:
                assert time.monotonic()-start<plan['max_seconds']
                days,coarse,f,p,truth=generate(seed,scenario)
                new,ledger,alarms=predict(days,f);previous,oldledger,oldalarms=b.causal_predictions(days,coarse,p)
                for variant,features,cells,als in [('iteration2',f,new,alarms),('previous_repaired',coarse,previous,oldalarms)]:
                    score,rows=b.discrimination(days,features,p,truth,cells)
                    score.pop('cells',None)
                    scores.append(dict(seed=seed,scenario=scenario,variant=variant,alarms=als,reversal_lag=next((z['index']-126 for z in als if z['index']>=126),None) if scenario=='reversal' else None,**score))
                    for z in rows:
                        z.update(seed=seed,scenario=scenario,variant=variant);of.write(json.dumps(z)+'\n')
                    for t in (*TIERS,'UNKNOWN'):
                        v=[z for z in rows if z['inferred_tier']==t]
                        opps.append(dict(seed=seed,scenario=scenario,variant=variant,tier=t,n=len(v),coverage=len(v)/len(rows),precision=st.mean(z['true_ev_tier']==t for z in v) if v and t!='UNKNOWN' else None,realized_net=st.mean(z['realized_net'] for z in v) if v else None,abstained_positive_net_sum=sum(max(0,z['realized_net']) for z in v) if t=='UNKNOWN' else 0,abstained_signed_net_sum=sum(z['realized_net'] for z in v) if t=='UNKNOWN' else 0,abstained_positive_ev_sum=sum(max(0,z['true_ev']) for z in v) if t=='UNKNOWN' else 0))
                with gzip.open(OUT/f'ledger_{seed}_{scenario}.jsonl.gz','wt') as lf:
                    for z in ledger:lf.write(json.dumps(z)+'\n')
                for variant,features,cells,policy in [('iteration2',f,new,'tier10'),('previous_repaired',coarse,previous,'tier10'),('existing_ev10',coarse,previous,'existing_ev10')]:
                    assert attempts<plan['max_full_replays'] and time.monotonic()-start<plan['max_seconds']
                    attempts+=1;(OUT/'attempts.json').write_text(json.dumps(dict(attempts=attempts,seed=seed,scenario=scenario,variant=variant)))
                    kw=b.callbacks(features,p,cells,policy,days);evdays=days[126:252]
                    candidates=[m.Candidate(t,'GA7','synthetic',.02,s.GAPS[j]) for j,t in enumerate(s.TICKERS)]
                    result=m.run_slice(evdays,candidates,max_sessions=126,max_stocks=24,**s.COSTS,**kw)
                    metric,_=s.measure(result,evdays);metric['total_return']=metric['final_nav']/s.INITIAL-1
                    metric['cagr']=(metric['final_nav']/s.INITIAL)**2-1
                    metrics.append(dict(seed=seed,scenario=scenario,variant=variant,**metric))
                    # Independent full post-BUY position risk, reconstructed from actual fills/NAV.
                    previous_shares={};bydate={d:[] for d,_ in evdays}
                    for fill in result['ledger']:bydate[fill[0]].append(fill)
                    for (d,bars),nav in zip(evdays,result['nav']):
                        fills=bydate[d];opening=nav[1]+sum(z[5]+z[3]*abs(z[4]-bars[z[1]].open) for z in fills)
                        for z in fills:
                            if z[2]=='BUY':
                                loss=(previous_shares.get(z[1],0)+z[3])*bars[z[1]].open/opening*(max(.02,s.GAPS[int(z[1][3:])])+s.ROUND_TRIP)
                                assert loss<=.02+1e-10;buys+=1;riskmax=max(riskmax,loss)
                        previous_shares=nav[3]
                    rf.write(json.dumps(dict(seed=seed,scenario=scenario,variant=variant,ledger=result['ledger'],nav=result['nav'],risk=result['risk_audit'],decisions=result['decisions']))+'\n')
                print(f'{seed} {scenario} {attempts}/{plan["max_full_replays"]} elapsed={time.monotonic()-start:.1f}s',flush=True)
    paired=[]
    for z in metrics:
        if z['variant']!='iteration2':continue
        for comparator in ('previous_repaired','existing_ev10'):
            old=next(v for v in metrics if v['seed']==z['seed'] and v['scenario']==z['scenario'] and v['variant']==comparator)
            paired.append(dict(seed=z['seed'],scenario=z['scenario'],comparator=comparator,return_delta=z['total_return']-old['total_return'],mdd_delta=z['mdd']-old['mdd'],iteration2_return=z['total_return'],comparator_return=old['total_return']))
    assert all(sha(p)==h for p,h in before.items());assert sha(OUT/'preregister.json')==ph
    for score in scores:
        with (OUT/f'confusion_{score["seed"]}_{score["scenario"]}_{score["variant"]}.csv').open('w') as cf:
            w=csv.writer(cf);w.writerow(['true / predicted',*TIERS,'UNKNOWN'])
            for i,t in enumerate(TIERS):w.writerow([t,*score['confusion_ev'][i],score['unknown_by_ev_tier'][i]])
    writecsv('tier_metrics.csv',opps);writecsv('portfolio_runs.csv',metrics);writecsv('paired.csv',paired)
    report=dict(status='PASS' if all(z['status']=='PASS' for z in scores if z['variant']=='iteration2' and z['scenario']!='null') and all(z['coverage']==0 for z in scores if z['variant']=='iteration2' and z['scenario']=='null') else 'FAIL',execution_status='COMPLETE',full_portfolio_replays=attempts,elapsed_seconds=time.monotonic()-start,preregister_sha256=ph,source_sha256=before,production_sources_unchanged=True,diagnosis=diagnosis,discrimination=scores,portfolio_runs=metrics,paired=paired,tier_metrics=opps,independent_risk_audit=dict(actual_buys=buys,max_candidate_modeled_loss=riskmax,passed=True),limitations=plan['limitations'])
    (OUT/'report.json').write_text(json.dumps(report,indent=2));print(report['status'])
if __name__=='__main__':main()
