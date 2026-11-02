"""Iteration3: frozen conditional EV fit; independent calibration; safety-only holdout monitor."""
import sys,json,math,statistics as st,time,subprocess,gzip,csv,hashlib,importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('iteration2_reference',OUT.parent/'discrimination_iteration2/experiment.py')
previous_model=importlib.util.module_from_spec(spec);sys.modules[spec.name]=previous_model;spec.loader.exec_module(previous_model)
b=previous_model.b
m,k,r,s=b.m,b.k,b.r,b.s
TIERS,EDGES,tier,infer,observed,sha=b.TIERS,b.EDGES,b.tier,b.infer,b.observed,b.sha
generate=previous_model.generate

def block_stats(pairs):
    groups={}
    for i,v in pairs:groups.setdefault(i//5,[]).append(v)
    values=[st.mean(v) for v in groups.values() if len(v)>=3]
    return (st.mean(values),st.stdev(values)/len(values)**.5,len(values)) if len(values)>1 else (0.,1.,len(values))

def date_values(days,features,lo,hi):
    result=[]
    for i in range(lo,hi):
        row=[]
        for c in range(5):
            vals=[]
            for j in range(24):
                if features[i][j]==c:
                    try:vals.append(observed(days,i,j))
                    except (KeyError,IndexError,TypeError):pass
            row.append(max(-.05,min(.05,st.mean(vals))) if vals else None)
        result.append((i,row))
    return result

def fit(days,features):
    train=date_values(days,features,0,78);cal=date_values(days,features,80,122)
    stats=[block_stats([(i,v[c]) for i,v in train if v[c] is not None]) for c in range(5)]
    raw=[v[0] for v in stats];means=[]
    for c in range(5):
        neighbors=[raw[h] for h in (c-1,c+1) if 0<=h<5]
        parent=st.mean(neighbors);n=stats[c][2]
        means.append((raw[c]*n+2*parent)/(n+2))
    cells=[]
    for c in range(5):
        residuals=[(i,v[c]-means[c]) for i,v in cal if v[c] is not None]
        bias,cse,ncal=block_stats(residuals);tse=stats[c][1]
        scale=math.hypot(tse,cse);penalty=abs(means[c]-raw[c])
        radius=abs(bias)+2.58*scale+penalty
        normal=st.NormalDist(means[c],max(scale+(abs(bias)+penalty)/2.58,1e-10))
        cdf=[0.]+[normal.cdf(x) for x in EDGES]+[1.]
        posterior=[cdf[i+1]-cdf[i] for i in range(5)]
        label=tier(means[c]) if tier(means[c]-radius)==tier(means[c]+radius) and max(posterior)>=.95 and stats[c][2]>=12 and ncal>=8 else 'UNKNOWN'
        cells.append(dict(mean=means[c],radius=radius,ntrain=sum(v[c] is not None for i,v in train),ncal=sum(v[c] is not None for i,v in cal),train_blocks=stats[c][2],calibration_blocks=ncal,train_se=tse,calibration_se=cse,calibration_bias=bias,shrinkage_penalty=penalty,posterior=posterior,label=label,reason='CONFIDENT' if label!='UNKNOWN' else 'BOUNDARY_UNCERTAINTY',latest_outcome_signal=121,reliability=0.))
    identifiable=max(means)-min(means)-2.58*math.hypot(stats[0][1],stats[4][1])>.003
    if not identifiable:
        for cell in cells:cell.update(label='UNKNOWN',reason='NO_IDENTIFIABLE_SIGNAL')
    contrast=[(i,v[4]-v[0]) for i,v in cal if v[0] is not None and v[4] is not None]
    baseline,se,n=block_stats(contrast)
    return cells,dict(baseline=baseline,block_sd=se*math.sqrt(n),baseline_se=se,blocks=n)

def predict(days,features):
    states=[];ledger=[];alarms=[];pending={};cells=None;monitor=None;contrasts=[];latched=False
    for now in range(252):
        for row in pending.get(now-3,[]):
            try:row.update(realized_net=observed(days,row['index'],row['j']),missingness='OBSERVED',available_index=now)
            except (KeyError,IndexError,TypeError):row['missingness']='MISSING'
        if now==126:cells,monitor=fit(days,features)
        # 26 prespecified nonoverlapping five-date looks. No fitted model update.
        if cells is not None and now>=133 and (now-133)%5==0 and not latched:
            start=now-7
            dv=date_values(days,features,start,start+5)
            vals=[v[4]-v[0] for i,v in dv if v[4] is not None and v[0] is not None]
            threshold=max(.004,st.NormalDist().inv_cdf(1-.01/(2*26))*math.hypot(monitor['block_sd'],monitor['baseline_se']))
            if len(vals)>=3 and abs(st.mean(vals)-monitor['baseline'])>threshold:
                alarms.append(dict(index=now,cells=[0,4],threshold=threshold,last_signal=now-3));latched=True
        current=[dict(c) for c in cells] if cells else [dict(mean=0.,radius=1.,ntrain=0,ncal=0,label='UNKNOWN',reason='PRE_FIT',latest_outcome_signal=-3,reliability=0.,posterior=[.2]*5) for _ in range(5)]
        if latched:
            for c in current:c.update(label='UNKNOWN',reason='DRIFT_LATCH')
        states.append(current)
        if now<250:
            rows=[]
            for j in range(24):
                c=current[features[now][j]]
                rows.append(dict(index=now,j=j,ticker=s.TICKERS[j],signal=features[now][j],decision_timestamp=s.DATES[now],execution_index=now+1,maturity_index=now+2,available_index=None,realized_net=None,missingness='PENDING',inferred_net=c['mean'],radius=c['radius'],inferred_tier=c['label'],reason=c['reason'],posterior=c['posterior'],split='train' if now<=77 else 'calibration' if 80<=now<=121 else 'holdout' if now>=126 else 'embargo',horizon='open(k+1) to open(k+2)',costs=dict(s.COSTS),friction=s.FRICTION))
            ledger.extend(rows);pending[now]=rows
    return states,ledger,alarms

def writecsv(name,rows):
    if rows:
        with (OUT/name).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def diagnose():
    prior=json.loads((OUT.parent/'discrimination_iteration2/report.json').read_text())
    return dict(prior_diagnosis=prior['diagnosis'],prior_ledger_audit=prior['ledger_audit'],conclusions=['Short recent cell windows confound estimation and calibration; date-common noise forbids stock count as independent N.','Frozen partial pooling uses neighboring cells only from training; independent block residuals calibrate uncertainty without fitting mean.','Five-date blocks address short date correlation but reduce effective sample. Missing cell dates reduce support further.','No holdout online fit or residual bias fit: safety latches independently, never narrows intervals.','No observable precursors to reversal in DGP; pre-maturation protection is information-limited.','Original manager accepts caller conditional_ev; it does not provide a class estimator. Prior causal ledger certifies timestamps, not calibration.'])
def main():
    start=time.monotonic();plan=json.loads((OUT/'preregister.json').read_text());ph=sha(OUT/'preregister.json')
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(OUT),'-p','test_*.py','-v'],capture_output=True,text=True)
    (OUT/'tests.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        (OUT/'report.json').write_text(json.dumps(dict(status='STOP_TEST_FAILURE',full_portfolio_replays=0)));raise SystemExit(result.returncode)
    sources=list(b.a.SOURCES)+[b.PRIOR/'corrected_manager.py',b.PRIOR/'corrected_kernel.py',Path(b.__file__),OUT/'experiment.py',OUT/'test_iteration3.py',OUT/'preregister.json']
    sources+=list((OUT.parent/'five_tier_discrimination').glob('*.py'))
    sources+=[OUT.parent/'five_tier_discrimination/report.json',OUT.parent/'opportunity_evaluator_fix/report.json',OUT.parent.parent/'mts_v5_manager_repair_20261031/v5_working_copy/engines/counterfactual_learning/causal_ledger.py']
    sources += [Path(previous_model.__file__), OUT/'finalize.py', OUT.parent/'discrimination_iteration2/report.json', OUT.parent/'discrimination_iteration2/preregister.json', OUT.parent/'discrimination_iteration2/README.md']
    before={str(p):sha(p) for p in sources};diagnosis=diagnose();scores=[];metrics=[];attempts=0;opps=[];riskmax=0.;buys=0
    with gzip.open(OUT/'opportunities.jsonl.gz','wt') as of,gzip.open(OUT/'replays.jsonl.gz','wt') as rf:
        for seed in plan['seeds']:
            for scenario in plan['scenarios']:
                assert time.monotonic()-start<plan['max_seconds']
                days,coarse,f,p,truth=generate(seed,scenario)
                new,ledger,alarms=predict(days,f);previous,oldledger,oldalarms=previous_model.predict(days,f)
                for variant,features,cells,als in [('iteration3',f,new,alarms),('iteration2_repaired',f,previous,oldalarms)]:
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
                for variant,features,cells,policy in [('iteration3',f,new,'tier10'),('iteration2_repaired',f,previous,'tier10'),('existing_ev10',coarse,previous,'existing_ev10')]:
                    assert attempts<plan['max_full_replays'] and time.monotonic()-start<plan['max_seconds']
                    attempts+=1;(OUT/'attempts.json').write_text(json.dumps(dict(attempts=attempts,seed=seed,scenario=scenario,variant=variant)))
                    kw=b.callbacks(features,p,cells,policy,days);evdays=days[126:252]
                    candidates=[m.Candidate(t,'GA7','synthetic',.02,s.GAPS[j]) for j,t in enumerate(s.TICKERS)]
                    result=m.run_slice(evdays,candidates,max_sessions=126,max_stocks=24,**s.COSTS,**kw)
                    metric,_=s.measure(result,evdays);metric['total_return']=metric['final_nav']/s.INITIAL-1
                    metric['cagr']=(metric['final_nav']/s.INITIAL)**2-1
                    metric['fees']=sum(z[5] for z in result['ledger'])
                    metric['spread_slippage_impact_cost']=sum(z[3]*abs(z[4]-dict(evdays)[z[0]][z[1]].open) for z in result['ledger'])
                    assert all(z[2]>=-1e-8 for z in result['nav'])
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
        if z['variant']!='iteration3':continue
        for comparator in ('iteration2_repaired','existing_ev10'):
            old=next(v for v in metrics if v['seed']==z['seed'] and v['scenario']==z['scenario'] and v['variant']==comparator)
            paired.append(dict(seed=z['seed'],scenario=z['scenario'],comparator=comparator,return_delta=z['total_return']-old['total_return'],mdd_delta=z['mdd']-old['mdd'],iteration3_return=z['total_return'],comparator_return=old['total_return']))
    assert all(sha(p)==h for p,h in before.items());assert sha(OUT/'preregister.json')==ph
    for score in scores:
        with (OUT/f'confusion_{score["seed"]}_{score["scenario"]}_{score["variant"]}.csv').open('w') as cf:
            w=csv.writer(cf);w.writerow(['true / predicted',*TIERS,'UNKNOWN'])
            for i,t in enumerate(TIERS):w.writerow([t,*score['confusion_ev'][i],score['unknown_by_ev_tier'][i]])
    writecsv('tier_metrics.csv',opps);writecsv('portfolio_runs.csv',metrics);writecsv('paired.csv',paired)
    report=dict(status='PASS' if all(z['status']=='PASS' for z in scores if z['variant']=='iteration3' and z['scenario']!='null') and all(z['coverage']==0 for z in scores if z['variant']=='iteration3' and z['scenario']=='null') else 'FAIL',execution_status='COMPLETE',full_portfolio_replays=attempts,elapsed_seconds=time.monotonic()-start,preregister_sha256=ph,source_sha256=before,production_sources_unchanged=True,diagnosis=diagnosis,discrimination=scores,portfolio_runs=metrics,paired=paired,tier_metrics=opps,independent_risk_audit=dict(actual_buys=buys,max_candidate_modeled_loss=riskmax,passed=True),limitations=plan['limitations'])
    (OUT/'report.json').write_text(json.dumps(report,indent=2));print(report['status'])
if __name__=='__main__':
    main()
    import finalize
    finalize.main()
