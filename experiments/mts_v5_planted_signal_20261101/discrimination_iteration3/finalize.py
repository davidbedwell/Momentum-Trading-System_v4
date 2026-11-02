"""Saved results aggregation only. Never fit or select parameters here."""
import json,gzip,csv,statistics as st
from pathlib import Path
import experiment as e
O=e.OUT

def main():
    r=json.loads((O/'report.json').read_text());assert r['execution_status']=='COMPLETE'
    plan=json.loads((O/'preregister.json').read_text());summary=[];tiers=[];ports=[];paired=[]
    for scenario in plan['scenarios']:
        for variant in ('iteration3','iteration2_repaired'):
            ss=[z for z in r['discrimination'] if z['scenario']==scenario and z['variant']==variant]
            mat=[[sum(z['confusion_ev'][i][j] for z in ss) for j in range(5)] for i in range(5)]
            n=sum(z['n'] for z in ss);assigned=sum(sum(v) for v in mat)
            q=dict(scenario=scenario,variant=variant,coverage=assigned/n,accuracy=sum(mat[i][i] for i in range(5))/assigned if assigned else None,false_great=sum(z['false_great_on_terrible_count'] for z in ss),true_terrible=sum(z['true_ev_counts']['TERRIBLE'] for z in ss),monotonic_seeds=sum(z['monotonic'] for z in ss),reversal_lags=[z['reversal_lag'] for z in ss],alarm_counts=[len(z['alarms']) for z in ss]);summary.append(q)
            for h,t in enumerate(e.TIERS):
                support=sum(v[h] for v in mat);true=sum(z['true_ev_counts'][t] for z in ss)
                rows=[z for z in r['tier_metrics'] if z['scenario']==scenario and z['variant']==variant and z['tier']==t]
                tiers.append(dict(scenario=scenario,variant=variant,tier=t,support=support,true_support=true,precision=mat[h][h]/support if support else None,recall=mat[h][h]/true,realized_net=sum(z['realized_net']*z['n'] for z in rows if z['n'])/support if support else None))
            for kind,key,uk in [('ev','confusion_ev','unknown_by_ev_tier'),('realized','confusion_realized','unknown_by_realized_tier')]:
                with (O/f'confusion_aggregate_{scenario}_{variant}_{kind}.csv').open('w') as f:
                    w=csv.writer(f);w.writerow(['true / predicted',*e.TIERS,'UNKNOWN'])
                    for i,t in enumerate(e.TIERS):w.writerow([t,*[sum(z[key][i][j] for z in ss) for j in range(5)],sum(z[uk][i] for z in ss)])
        for variant in plan['policies']:
            rr=[z for z in r['portfolio_runs'] if z['scenario']==scenario and z['variant']==variant]
            ports.append(dict(scenario=scenario,variant=variant,**{k:st.mean(z[k] for z in rr) for k in ('total_return','cagr','mdd','fees','spread_slippage_impact_cost')},exposure_fields={k:st.mean(z[k] for z in rr) for k in rr[0] if 'exposure' in k and isinstance(rr[0][k],(int,float))}))
        for comparator in ('iteration2_repaired','existing_ev10'):
            rr=[z for z in r['paired'] if z['scenario']==scenario and z['comparator']==comparator]
            paired.append(dict(scenario=scenario,comparator=comparator,mean_return_delta=st.mean(z['return_delta'] for z in rr),mean_mdd_delta=st.mean(z['mdd_delta'] for z in rr),return_delta_range=[min(z['return_delta'] for z in rr),max(z['return_delta'] for z in rr)]))
    reasons={};rows=pending=0
    for path in O.glob('ledger_*.jsonl.gz'):
        with gzip.open(path,'rt') as f:
            for line in f:
                z=json.loads(line);rows+=1
                assert z['execution_index']==z['index']+1 and z['maturity_index']==z['index']+2
                if z['available_index'] is not None:assert z['available_index']>z['maturity_index']
                else:pending+=1
                if z['index']>=126:reasons[z['reason']]=reasons.get(z['reason'],0)+1
    assert rows==96000 and pending==384
    rev=[q for q in summary if q['scenario']=='reversal']
    protection=rev[0]['false_great']<=rev[1]['false_great']
    if not protection:r['status']='FAIL'
    r.update(quality_aggregates=summary,tier_aggregates=tiers,portfolio_aggregates=ports,paired_aggregates=paired,ledger_audit=dict(rows=rows,pending=pending,reasons=reasons),improvement_claim=dict(claim=False,reversal_protection=protection),holdout_policy='No holdout outcome changes fit, calibration or posterior. Strictly matured holdout contrasts may only latch UNKNOWN. Tapes were viewed in iteration2; not fresh confirmatory holdout.',focused_tests=dict(before_portfolios=True,log='tests.log'),environment_note='Runtime skill read; environment_status unavailable; local only, no network.')
    for name,rr in [('summary.csv',summary),('tier_aggregate.csv',tiers),('portfolio_aggregate.csv',ports),('paired_aggregate.csv',paired)]:e.writecsv(name,rr)
    # Retrospective diagnostics only: no changes to preregistered estimator or gates.
    diagnostic=[]
    for seed in plan['seeds']:
        days,_,features,_,_=e.generate(seed,'learnable');cells,monitor=e.fit(days,features)
        diagnostic.append(dict(seed=seed,cells=cells,monitor=monitor))
    r['frozen_fit_diagnostics']=diagnostic
    r['fundamental_diagnosis']='Stable synthetic sensor contains predictive information by construction; failure to certify middle bands with 78/42 dates and block uncertainty is finite-information limitation, not proof of no signal. Null lacks PIT association by construction. Reversal has no observable advance warning: before matured outcomes no causal detector can distinguish it. Real PIT predictive information remains untested; no real-market edge inferred.'
    (O/'report.json').write_text(json.dumps(r,indent=2))
    (O/'source_checksums.json').write_text(json.dumps(r['source_sha256'],indent=2))
    text=['# Discrimination iteration3 — '+r['status'],'',f"Completed {r['full_portfolio_replays']}/48 paired portfolio replays in {r['elapsed_seconds']:.1f}s. Tests passed before replays; see tests.log. No GA or production modifications.",'','Frozen train signals 0–77; independent calibration 80–121; embargo; holdout 126–249. Calibration never changes point estimates. Holdout never changes estimates, uncertainty, or posterior. Matured holdout contrast blocks feed only a permanent safety veto. These exact synthetic tapes were already viewed in iteration2: this is a regression experiment, not new confirmatory evidence.','', 'Fit uses clipped cell date means, neighboring-cell partial pooling and five-date block standard errors. Calibration adds independent residual bias and sampling uncertainty. Economic boundaries remain −0.6%, −0.2%, +0.2%, +0.6%; the entire interval must fit a band and Gaussian conditional-mean posterior must exceed .95. UNKNOWN remains explicit. Gaussian block approximations assume independent/stable blocks; coverage is not distribution-free or certified with eight calibration blocks.','', '| Scenario | Evaluator | Coverage | Accuracy | False GREAT / TERRIBLE | Monotone seeds |','|---|---|---:|---:|---:|---:|']
    for q in summary:
        acc=f"{q['accuracy']:.1%}" if q['accuracy'] is not None else 'n/a'
        text.append(f"| {q['scenario']} | {q['variant']} | {q['coverage']:.1%} | {acc} | {q['false_great']}/{q['true_terrible']} | {q['monotonic_seeds']}/4 |")
    text+=['','GOOD/AVERAGE/POOR support, every class precision/recall and realized net means are in tier_aggregate.csv and report.json. Full 5×5 matrices plus UNKNOWN are in confusion_aggregate_*_{ev,realized}.csv. Portfolio CAGR/MDD/exposure/costs and paired differences are in portfolio_runs.csv, portfolio_aggregate.csv and paired*.csv. Exact per-seed results remain in report.json.','', 'Reversal lags: '+str(rev[0]['reversal_lags'])+'; iteration2: '+str(rev[1]['reversal_lags'])+'. Alarm counts are in summary.csv. A latch cannot anticipate inversion; it never relearns from holdout.','',r['fundamental_diagnosis'],'','Iteration2 diagnosis: short rolling windows and sparse per-cell independent dates inflate error; calibration pooled into mean invalidates independence; rolling residual vetoes and unadjusted repeated cell scans suppress coverage and produce nuisance alarms. Iteration3 separates those mechanisms but cannot manufacture missing information. Full shrinkage displacement and independent calibration uncertainty are retained instead of shrinking intervals merely to populate bins.','', 'Robust all-seed pass gates are frozen in preregister.json. Portfolio returns cannot override discriminator failure. No real-market edge claim. Modeled candidate risk <=2%, T+1 and cash/cost contracts tested; realized losses are not guaranteed capped. No terminal liquidation; one-session outcome label does not certify multi-session portfolio EV.','', 'Reproduce from repository root (requires original MTS checkout and sibling dependencies):','```bash','python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration3/experiment.py > /tmp/iteration3_execution.log 2>&1','```','Runner stops at test failure. It overwrites artifacts; archive first. finalize.py only aggregates saved results. Original native manager delegates quality to conditional_ev; the causal ledger enforces availability rather than estimating quality. Dependencies and source hashes are retained. Ledger archives contain all eligible opportunities, including unselected entries; scoring truth is added only by evaluator after forecasts.','', 'Limitations:']
    text+=['- '+x for x in plan['limitations']]
    (O/'README.md').write_text('\n'.join(text)+'\n')
    manifest={p.name:e.sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name not in ('manifest.json','execution.log','run.log')}
    (O/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(dict(status=r['status'],summary=summary,tiers=tiers),indent=2))
if __name__=='__main__':main()
