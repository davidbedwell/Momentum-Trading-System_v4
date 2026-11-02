from model import *
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
    sources=list(b.a.SOURCES)+[b.PRIOR/'corrected_manager.py',b.PRIOR/'corrected_kernel.py',Path(b.__file__),OUT/'experiment.py',OUT/'test_iteration4.py',OUT/'preregister.json']
    sources+=list((OUT.parent/'five_tier_discrimination').glob('*.py'))
    sources+=[OUT.parent/'five_tier_discrimination/report.json',OUT.parent/'opportunity_evaluator_fix/report.json',OUT.parent.parent/'mts_v5_manager_repair_20261031/v5_working_copy/engines/counterfactual_learning/causal_ledger.py']
    sources += [Path(previous_model.__file__), OUT/'model.py', OUT.parent/'discrimination_iteration2/report.json', OUT.parent/'discrimination_iteration2/preregister.json', OUT.parent/'discrimination_iteration2/README.md']
    before={str(p):sha(p) for p in sources};diagnosis=diagnose();scores=[];metrics=[];attempts=0;opps=[];riskmax=0.;buys=0
    with gzip.open(OUT/'opportunities.jsonl.gz','wt') as of,gzip.open(OUT/'replays.jsonl.gz','wt') as rf:
        for seed in plan['seeds']:
            for scenario in plan['scenarios']:
                assert time.monotonic()-start<plan['max_seconds']
                days,coarse,f,p,truth=generate(seed,scenario)
                bundle,ledger,alarms=predict(days,f);new=bundle["iteration4"];previous,oldledger,oldalarms=previous_model.predict(days,f);ids=[list(range(24)) for _ in range(252)]
                for variant,features,cells,als in [('iteration4',ids,new,alarms),('iteration2_repaired',f,previous,oldalarms)]+[(v,ids,bundle[v],[]) for v in ('ungated','sensor_only','price_only')]:
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
                for variant,features,cells,policy in [('iteration4',ids,new,'tier10'),('iteration2_repaired',f,previous,'tier10'),('ungated',ids,bundle['ungated'],'tier10'),('scaled',ids,new,'tier15')]:
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
        if z['variant']!='iteration4':continue
        for comparator in ('iteration2_repaired','ungated','scaled'):
            old=next(v for v in metrics if v['seed']==z['seed'] and v['scenario']==z['scenario'] and v['variant']==comparator)
            paired.append(dict(seed=z['seed'],scenario=z['scenario'],comparator=comparator,return_delta=z['total_return']-old['total_return'],mdd_delta=z['mdd']-old['mdd'],iteration3_return=z['total_return'],comparator_return=old['total_return']))
    assert all(sha(p)==h for p,h in before.items());assert sha(OUT/'preregister.json')==ph
    for score in scores:
        with (OUT/f'confusion_{score["seed"]}_{score["scenario"]}_{score["variant"]}.csv').open('w') as cf:
            w=csv.writer(cf);w.writerow(['true / predicted',*TIERS,'UNKNOWN'])
            for i,t in enumerate(TIERS):w.writerow([t,*score['confusion_ev'][i],score['unknown_by_ev_tier'][i]])
    writecsv('tier_metrics.csv',opps);writecsv('portfolio_runs.csv',metrics);writecsv('paired.csv',paired)
    report=dict(status='PASS' if all(z['status']=='PASS' for z in scores if z['variant']=='iteration4' and z['scenario']!='null') and all(z['coverage']==0 for z in scores if z['variant']=='iteration4' and z['scenario']=='null') else 'FAIL',execution_status='COMPLETE',full_portfolio_replays=attempts,elapsed_seconds=time.monotonic()-start,preregister_sha256=ph,source_sha256=before,production_sources_unchanged=True,diagnosis=diagnosis,discrimination=scores,portfolio_runs=metrics,paired=paired,tier_metrics=opps,independent_risk_audit=dict(actual_buys=buys,max_candidate_modeled_loss=riskmax,passed=True),limitations=plan['limitations'])
    (OUT/'report.json').write_text(json.dumps(report,indent=2));print(report['status'])

if __name__=="__main__":main()
