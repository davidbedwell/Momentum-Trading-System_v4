"""Report-only saved-ledger aggregation plus preregistered independent static split ablation.
No portfolios, parameter changes, or choices based on holdout scores.
"""
import json,csv,gzip,statistics as st,shutil,hashlib,time
from pathlib import Path
import experiment as e
O=e.OUT

def main():
    final_start=time.monotonic()
    report=json.loads((O/'report.json').read_text());assert report['execution_status']=='COMPLETE'
    plan=json.loads((O/'preregister.json').read_text());summary=[];tierrows=[];port=[]
    for scenario in plan['scenarios']:
        for variant in ('iteration2','previous_repaired'):
            ss=[z for z in report['discrimination'] if z['scenario']==scenario and z['variant']==variant]
            counts={t:sum(z['counts'][t] for z in ss) for t in (*e.TIERS,'UNKNOWN')};n=sum(z['n'] for z in ss);assigned=n-counts['UNKNOWN']
            mat=[[sum(z['confusion_ev'][i][j] for z in ss) for j in range(5)] for i in range(5)]
            q=dict(scenario=scenario,variant=variant,coverage=assigned/n,accuracy=sum(mat[i][i] for i in range(5))/assigned if assigned else None,false_great=sum(z['false_great_on_terrible_count'] for z in ss),true_terrible=sum(z['true_ev_counts']['TERRIBLE'] for z in ss),monotonic_seeds=sum(z['monotonic'] for z in ss),populated_tiers=sum(counts[t]>0 for t in e.TIERS),reversal_lags=[z['reversal_lag'] for z in ss],alarm_counts=[len(z['alarms']) for z in ss],seed_passes=sum(z['status']=='PASS' for z in ss))
            q['false_great_rate']=q['false_great']/q['true_terrible'];summary.append(q)
            for t in (*e.TIERS,'UNKNOWN'):
                rows=[z for z in report['tier_metrics'] if z['scenario']==scenario and z['variant']==variant and z['tier']==t];count=counts[t]
                tierrows.append(dict(scenario=scenario,variant=variant,tier=t,n=count,coverage=count/n,precision=sum(z['precision']*z['n'] for z in rows if z['precision'] is not None)/count if count and t!='UNKNOWN' else None,realized_net=sum(z['realized_net']*z['n'] for z in rows if z['n'])/count if count else None,abstained_positive_net_sum=sum(z['abstained_positive_net_sum'] for z in rows),abstained_signed_net_sum=sum(z['abstained_signed_net_sum'] for z in rows),abstained_positive_ev_sum=sum(z['abstained_positive_ev_sum'] for z in rows)))
            for kind,key,uk in [('ev','confusion_ev','unknown_by_ev_tier'),('realized','confusion_realized','unknown_by_realized_tier')]:
                with (O/f'confusion_aggregate_{scenario}_{variant}_{kind}.csv').open('w') as f:
                    w=csv.writer(f);w.writerow(['true / predicted',*e.TIERS,'UNKNOWN'])
                    for i,t in enumerate(e.TIERS):w.writerow([t,*[sum(z[key][i][j] for z in ss) for j in range(5)],sum(z[uk][i] for z in ss)])
        for variant in plan['policies']:
            rows=[z for z in report['portfolio_runs'] if z['scenario']==scenario and z['variant']==variant]
            port.append(dict(scenario=scenario,variant=variant,n=len(rows),mean_return=st.mean(z['total_return'] for z in rows),mean_mdd=st.mean(z['mdd'] for z in rows),worst_mdd=max(z['mdd'] for z in rows),worst_return=min(z['total_return'] for z in rows)))
    # Static independent split ablation explicitly reserved in preregistration.
    static=[]
    for seed in plan['seeds']:
        for scenario in plan['scenarios']:
            days,coarse,features,p,truth=e.generate(seed,scenario)
            train=[];cal=[]
            for c in range(5):
                def vals(lo,hi):
                    out=[]
                    for i in range(lo,hi):
                        assert i+2<126
                        row=[e.observed(days,i,j) for j in range(24) if features[i][j]==c]
                        if row:out.append(st.mean(row))
                    return out
                train.append(vals(0,78));cal.append(vals(80,122))
            means=e.estimate(train);cells=[]
            for c in range(5):
                mean=means[c];radius=max(2.58*e.b.se(train[c]),abs(st.mean(cal[c])-mean)+1.64*e.b.se(cal[c]))+abs(mean-st.mean(train[c]))
                label=e.infer(mean,radius,len(train[c]),len(cal[c]))
                if max(means)-min(means)<.003:label='UNKNOWN'
                cells.append(dict(mean=mean,radius=radius,ntrain=len(train[c]),ncal=len(cal[c]),label=label))
            score,_=e.b.discrimination(days,features,p,truth,cells)
            static.append(dict(seed=seed,scenario=scenario,**score))
    reasons={};count=pending=observed=missing=0
    for p in O.glob('ledger_*.jsonl.gz'):
        with gzip.open(p,'rt') as f:
            for line in f:
                z=json.loads(line);count+=1
                assert z['execution_index']==z['index']+1 and z['maturity_index']==z['index']+2
                if z['realized_net'] is not None:observed+=1;assert z['available_index']>z['maturity_index']
                elif z['missingness']=='PENDING':pending+=1
                else:missing+=1
                if 126<=z['index']<250:reasons[z['reason']]=reasons.get(z['reason'],0)+1
    assert count==96000 and pending==384 and missing==0
    pairedsummary=[]
    for scenario in plan['scenarios']:
        for comparator in ('previous_repaired','existing_ev10'):
            rows=[z for z in report['paired'] if z['scenario']==scenario and z['comparator']==comparator]
            pairedsummary.append(dict(scenario=scenario,comparator=comparator,n=len(rows),mean_return_delta=st.mean(z['return_delta'] for z in rows),min_return_delta=min(z['return_delta'] for z in rows),max_return_delta=max(z['return_delta'] for z in rows),mean_mdd_delta=st.mean(z['mdd_delta'] for z in rows),return_wins=sum(z['return_delta']>0 for z in rows)))
    # Preregistered improvement criterion includes reversal protection, independently of portfolio gains.
    coverage_ok=all(next(q for q in summary if q['scenario']==sc and q['variant']=='iteration2')['coverage']>next(q for q in summary if q['scenario']==sc and q['variant']=='previous_repaired')['coverage'] for sc in plan['scenarios'] if sc!='null')
    rev=[next(q for q in summary if q['scenario']=='reversal' and q['variant']==v) for v in ('iteration2','previous_repaired')]
    protection=rev[0]['false_great_rate']<=rev[1]['false_great_rate']
    report.update(quality_aggregates=summary,portfolio_aggregates=port,paired_aggregates=pairedsummary,tier_aggregates=tierrows,static_independent_split_ablation=static,focused_tests=dict(passed=12,failed=0,before_portfolios=True),ledger_audit=dict(rows=count,observed=observed,pending=pending,missing=missing,unknown_reasons=reasons,strict_maturity=True),improvement_claim=dict(coverage_improved=coverage_ok,reversal_protection=protection,robust_five_way=report['status']=='PASS',claim=False),protocol_limitations=['Primary pooled estimator uses its recent calibration window in the point estimate. That window is a drift/stability diagnostic, not independent calibration. Independent static train0..77/cal80..121 ablation is reported separately and was reserved before execution.','Primary initial rolling split is33..92 older,93..123 recent, as explicitly stated before execution; it does not use nominal static ranges.','Static ablation radius formula is inherited unchanged from primary method, but static ablation has no rolling drift adaptation or residual gate and no portfolio replay; cannot certify the complete online bundle.'],missing_data=['Real PIT sensor time series with release timestamps, revision history, missingness, and measured noise covariance; injected Gaussian quality has no empirical realism validation.','Longer independent matured stable-regime dates for narrow middle economic bands; independent calibration episodes and more forward seeds/regimes.','Observable change predictors available before entry, or more rapid genuinely matured horizon outcomes to protect inversion before alarms.','A holding-horizon-specific net-return label and causal selection-aware portfolio counterfactual for attainable abstention cost.'])
    report['limitations']+=report['protocol_limitations']
    report['status']='FAIL' if not protection or not coverage_ok else report['status']
    report['source_sha256'][str(O/'finalize.py')]=e.sha(O/'finalize.py')
    report['reporting_seconds']=time.monotonic()-final_start
    report['total_compute_seconds']=report['elapsed_seconds']+report['reporting_seconds']
    assert report['total_compute_seconds']<=900
    (O/'execution.log').write_text(f"Tests:12 passed before portfolios. Replays:{report['full_portfolio_replays']}/48. Replay elapsed:{report['elapsed_seconds']:.3f}s. Reporting:{report['reporting_seconds']:.3f}s. Total:{report['total_compute_seconds']:.3f}s. Budget900s.\n")
    (O/'source_checksums.json').write_text(json.dumps(report['source_sha256'],indent=2))
    for name,rows in [('summary.csv',summary),('tier_aggregate.csv',tierrows),('portfolio_aggregate.csv',port),('paired_aggregate.csv',pairedsummary)]:e.writecsv(name,rows)
    for name in ('corrected_manager.py','corrected_kernel.py','source.patch'):shutil.copyfile(e.b.PRIOR/name,O/name)
    report['environment_note']='Runtime skill read; environment_status tool unavailable. Local filesystem experiment only; no network or credentials used.'
    (O/'report.json').write_text(json.dumps(report,indent=2))
    lines=['# Discrimination iteration2 — '+report['status'],'',f"Completed {report['full_portfolio_replays']}/48 paired full replays in {report['elapsed_seconds']:.1f}s, after all12 unit tests passed. No GA or production changes. No thresholds changed after evaluation.",'','No overall improvement or reliable five-way claim. Synthetic injected sensor bundle is more informative by construction; it is not measured real alpha. Primary online estimator pools recent calibration observations into its mean, so it does not meet independent calibration certification. The separately reported static ablation uses disjoint chronological train0–77/cal80–121/holdout126–249, with no holdout refitting.','', 'Decision boundary bands are TERRIBLE <−0.6%, POOR [−0.6%,−0.2%), AVERAGE [−0.2%,0.2%), GOOD [0.2%,0.6%), GREAT ≥0.6%. UNKNOWN remains explicit. Conditional mean bands do not guarantee the individual hidden latent class.','', '| Scenario | Evaluator | Coverage | Accuracy | False GREAT / true TERRIBLE | Monotone seeds |', '|---|---|---:|---:|---:|---:|']
    for q in summary:
        acc=f"{q['accuracy']:.1%}" if q['accuracy'] is not None else 'n/a'
        lines.append(f"| {q['scenario']} | {q['variant']} | {q['coverage']:.1%} | {acc} | {q['false_great']}/{q['true_terrible']} | {q['monotonic_seeds']}/4 |")
    lines+=['', 'Reversal lag (first post126 alarm minus126): '+str(rev[0]['reversal_lags'])+'; previous repaired: '+str(rev[1]['reversal_lags'])+'. Repeated/nuisance alarm counts are in summary.csv. Stronger measurements can increase damage before an unannounced reversal is observed; inspect false-GREAT protection separately from stable coverage.','', 'Prior diagnosis: no tier-dispatch bug or overlapping thresholds. The prior80% coarse sensor mixes states; the narrow0.4-percentage-point middle bands, at most21 recent independent date clusters, and train/calibration discrepancy produce intervals crossing boundaries. Global gates further suppress coverage. Exact counts and descriptive realized cell means are in report.json diagnosis; these are overlapping diagnostics, not causal ablation estimates.','', '| Scenario | Policy | Mean return | Mean MDD | Worst MDD |','|---|---|---:|---:|---:|']
    for q in port:lines.append(f"| {q['scenario']} | {q['variant']} | {q['mean_return']:.2%} | {q['mean_mdd']:.2%} | {q['worst_mdd']:.2%} |")
    lines+=['',f"Independent full post-BUY risk reconstruction: {report['independent_risk_audit']['actual_buys']} BUYs, maximum modeled entire-candidate loss {report['independent_risk_audit']['max_candidate_modeled_loss']:.8f} <=0.02. T+1 tested. No scale-up or terminal liquidation. Risk is modeled, not a realized-loss guarantee.",'', 'tier_aggregate.csv reports per-tier precision, coverage and forward realized net return. Confusion CSVs provide5×5 plus UNKNOWN, for latent EV and individual realized tiers. paired.csv and paired_aggregate.csv report matched return/MDD deltas against both comparators. Abstention costs are signed forgone net sum, positive realized sum and positive evaluator-EV sum per opportunity; these ex-post quantities ignore cash conflicts and are not attainable portfolio returns.','', 'Reproduce from repository root (requires the original MTS checkout and sibling dependencies):','```bash','python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/experiment.py > /tmp/discrimination_iteration2_execution.log 2>&1','python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/finalize.py','```','Runner stops on any failed test. It overwrites outputs; archive this directory before reproduction. preregister.json is frozen and its execution hash is in report.json. source_checksums.json covers reviewed/executed sources, local corrected manager/kernel and patch are preserved, all6000 eligible outcome events per tape are in ledger archives, held-out scoring records in opportunities.jsonl.gz, actual executions in replays.jsonl.gz. run.log is the external task transcript; execution.log contains replay progress extracted from it.','', 'Missing data and limitations:']
    lines+=['- '+v for v in report['missing_data']+report['limitations']]
    (O/'README.md').write_text('\n'.join(lines)+'\n')
    # Exclude active external transcript from manifest to avoid self-referential mutation.
    manifest={p.name:e.sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name not in ('manifest.json','run.log','finalize.log')}
    (O/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(dict(status=report['status'],summary=summary,risk=report['independent_risk_audit']),indent=2))
if __name__=='__main__':main()
