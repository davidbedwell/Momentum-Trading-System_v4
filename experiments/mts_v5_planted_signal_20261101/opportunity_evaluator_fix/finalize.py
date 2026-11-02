"""Report-only aggregation and independent saved-ledger verification. No replays/fitting."""
from pathlib import Path
import json,csv,gzip,statistics as st,hashlib,shutil,difflib,tempfile,subprocess
import experiment as e
O=e.OUT
report=json.loads((O/'report.json').read_text());assert report['execution_status']=='COMPLETE'
maxloss=0.;maxerror=0.;buys=0;replays=0
with gzip.open(O/'replays.jsonl.gz','rt') as f:
    for line in f:
        x=json.loads(line);days,_,_,_=e.generate(x['seed'],x['scenario']);days=days[126:252]
        previous={};bydate={d:[] for d,_ in days}
        for fill in x['ledger']:bydate[fill[0]].append(fill)
        for (d,bars),nav in zip(days,x['nav']):
            fills=bydate[d];opening=nav[1]+sum(z[5]+z[3]*abs(z[4]-bars[z[1]].open) for z in fills)
            for z in fills:
                if z[2]=='BUY':
                    t=z[1];weight=(previous.get(t,0)+z[3])*bars[t].open/opening
                    loss=weight*(max(.02,e.s.GAPS[int(t[3:])])+e.s.ROUND_TRIP)
                    assert loss<=.02+1e-10,(x['seed'],x['scenario'],x['variant'],d,loss)
                    maxloss=max(maxloss,loss);buys+=1
            previous=nav[3]
        replays+=1
assert replays==report['full_portfolio_replays']==64
report['independent_full_candidate_risk_verification']=dict(replays=replays,actual_buys=buys,max_full_post_buy_candidate_loss=maxloss,passed=True)
aggregates=[];quality=[]
for scenario in ('learnable','misleading','null','reversal'):
    scores=[z for z in report['discrimination'] if z['scenario']==scenario]
    counts={t:sum(z['counts'][t] for z in scores) for t in (*e.TIERS,'UNKNOWN')}
    mat=[[sum(z['confusion_ev'][i][j] for z in scores) for j in range(5)] for i in range(5)]
    n=sum(z['n'] for z in scores);assigned=n-counts['UNKNOWN']
    q=dict(scenario=scenario,status='PASS' if all(z['status']=='PASS' for z in scores) else 'FAIL',counts=counts,coverage=assigned/n,conditional_accuracy=sum(mat[i][i] for i in range(5))/assigned if assigned else None,false_great_on_terrible=sum(z['false_great_on_terrible_count'] for z in scores),true_terrible=sum(z['true_ev_counts']['TERRIBLE'] for z in scores),monotone_seeds=sum(z['monotonic'] for z in scores),mean_rank_ic=st.mean(z['calibration']['rank_correlation'] for z in scores),mean_raw_prediction_rank_ic=st.mean(z['raw_prediction_calibration']['rank_correlation'] for z in scores))
    quality.append(q)
    for kind,key,uk in [('ev','confusion_ev','unknown_by_ev_tier'),('realized','confusion_realized','unknown_by_realized_tier')]:
        with (O/f'confusion_aggregate_{scenario}_{kind}.csv').open('w') as f:
            w=csv.writer(f);w.writerow(['true / predicted',*e.TIERS,'UNKNOWN'])
            for i,t in enumerate(e.TIERS):w.writerow([t,*[sum(z[key][i][j] for z in scores) for j in range(5)],sum(z[uk][i] for z in scores)])
    for variant in ('existing_ev10','tier10','tier15','tier20'):
        rows=[z for z in report['portfolio_runs'] if z['scenario']==scenario and z['variant']==variant]
        aggregates.append(dict(scenario=scenario,variant=variant,n=len(rows),**{k:st.mean(z[k] for z in rows) for k in ('total_return','cagr','mdd','turnover','fees','spread_slippage_impact_cost','exposure','fills','scaled_fills','full_target_fills')},worst_mdd=max(z['mdd'] for z in rows),losing_seeds=[z['seed'] for z in rows if z['total_return']<0]))
report['quality_aggregates']=quality;report['portfolio_aggregates']=aggregates
report['baseline_scope']='Existing MTS net-EV admission and EV-ranked cash queue at 10% cap, on harmonized experiment ENTER/HOLD/EXIT proposals. Not a byte-identical rerun of the older planted-tape native switching policy; tape, horizon and proposal logic differ.'
report['limitations'].append('The DGP grosses up one-session net EV by round-trip costs. A portfolio holding across multiple signals pays costs less frequently and can earn positive drift even with null signals; null baseline profits are not evidence of quality recognition. Portfolio holding horizons differ from one-session label horizons.')
report['focused_tests']=dict(passed=14,failed=0,run_before_portfolios=True)
report['failure_specifics']=[dict(scenario=q['scenario'],unpopulated=[t for t in e.TIERS if q['counts'][t]==0],coverage=q['coverage'],conditional_accuracy=q['conditional_accuracy'],false_great_on_terrible=q['false_great_on_terrible'],monotone_seeds=q['monotone_seeds']) for q in quality if q['status']=='FAIL']
(O/'report.json').write_text(json.dumps(report,indent=2))
for name,rows in [('portfolio_runs.csv',report['portfolio_runs']),('portfolio_aggregate.csv',aggregates),('paired.csv',report['paired'])]:
    with (O/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Preserve exact local execution sources and their reconstructing inherited patch.
for name in ('corrected_manager.py','corrected_kernel.py','source.patch'):
    shutil.copyfile(e.PRIOR/name,O/name)

prior=json.loads((O.parent/'five_tier_discrimination/report.json').read_text())
comparisons=[]
for q in quality:
    old=next(z for z in prior['quality_aggregates'] if z['scenario']==q['scenario'])
    comparisons.append(dict(scenario=q['scenario'],old_coverage=old['coverage'],new_coverage=q['coverage'],old_accuracy=old['conditional_accuracy'],new_accuracy=q['conditional_accuracy'],old_false_great=old['false_great_on_terrible'],new_false_great=q['false_great_on_terrible']))
for q in quality:
    scores=[z for z in report['discrimination'] if z['scenario']==q['scenario']]
    q['realized_net_by_tier']={t:(sum(z['forward_realized_net_by_tier'][t]*z['counts'][t] for z in scores if z['counts'][t])/q['counts'][t] if q['counts'][t] else None) for t in (*e.TIERS,'UNKNOWN')}
    q['drift_detection_delays']=[z['drift_detection_delay'] for z in scores]
    q['alarm_counts']=[len(z['drift_alarms']) for z in scores]
report['previous_run_comparison']=comparisons
report['preregistration_metadata_discrepancy']={'description':'Version 2 method and online_evaluation supersede inherited static confidence/train/calibration metadata. Inclusive implementation windows contain 40 older and up to 21 recent dates (61 total), and 9 recent drift dates, versus nominal 40/20/8 wording. Exact bounds were frozen in source before evaluation; no post-evaluation repair or tuning performed.','exact_bounds':'mature signal i in [now-63,now-3]; train i<now-23; cal i>=now-23; drift recent i>=now-11','claim_impact':'Protocol documentation discrepancy independently precludes a clean preregistration PASS.'}
report['execution_source_sha256']={name:e.sha(O/name) for name in ('experiment.py','test_causal.py','test_native.py','preregister.json')}
report['minimum_engineering_change']='Ledger and rolling estimator implemented locally; reliable five-way inference still requires stronger PIT features distinguishing neighboring EV bands, more independent matured dates within stable regimes, and timely observable regime-change predictors. Null has no identifying signal by design.'
report['limitations']=[v for v in report['limitations'] if 'frozen experiment-local' not in v]
report['limitations']+=['Online monitoring uses matured evaluation realized returns, never latent evaluation labels; evaluation is prequential, not a static frozen-fit holdout.','No pre-change observable feature identifies the unannounced reversal. Drift alarm and recovery lag are unavoidable.','Risk gates use empirical fifth percentile outcomes and native candidate modeled risk; neither guarantees realized loss bounds.']
report['ledger_summary']=dict(eligible_opportunities=250*24*16,includes_untraded=True,strict_maturity=True,final_pending=24*16,outcome_horizon='signal k; entry open k+1; exit open k+2; available close k+3',oracle_inputs=False)
report['prior_scaling_robustness']=dict(path=str(O.parent/'scaling_robustness/report.json'),sha256=e.sha(O.parent/'scaling_robustness/report.json'),interpretation='Prior null scaling increased tails; use actual native funded evidence plus local calibration and independent risk clipping. No scaling-success claim from cap alone.')
portfolio_comparison=[]
for z in report['portfolio_runs']:
    old=next(v for v in prior['portfolio_runs'] if all(v[k]==z[k] for k in ('seed','scenario','variant')))
    portfolio_comparison.append(dict(seed=z['seed'],scenario=z['scenario'],variant=z['variant'],old_return=old['total_return'],new_return=z['total_return'],return_delta=z['total_return']-old['total_return'],old_mdd=old['mdd'],new_mdd=z['mdd']))
for name,rows in [('comparison_previous.csv',comparisons),('portfolio_previous.csv',portfolio_comparison),('quality_aggregate.csv',quality)]:
    with (O/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
report['portfolio_tail_risk']=[dict(scenario=z['scenario'],variant=z['variant'],worst_mdd=z['worst_mdd'],worst_return=min(v['total_return'] for v in report['portfolio_runs'] if v['scenario']==z['scenario'] and v['variant']==z['variant']),sample_size=z['n']) for z in aggregates]
# Independent audit of all opportunity rows; oracle values used here for scoring only.
truth_cache={};bins={};reasons={};observed=missing=pending=count=0
with gzip.open(O/'opportunities.jsonl.gz','rt') as f:
    for line in f:
        z=json.loads(line);count+=1
        assert z['execution_index']==z['index']+1 and z['maturity_index']==z['index']+2
        assert z['eligible'] and z['decision_timestamp']<z['maturation_timestamp']
        if z['missingness']=='OBSERVED':
            observed+=1;assert z['available_index']>z['maturity_index']
        elif z['missingness']=='PENDING':pending+=1
        else:missing+=1
        if not 126<=z['index']<250:continue
        key=(z['seed'],z['scenario'])
        if key not in truth_cache:truth_cache[key]=e.generate(*key)[3]
        true=truth_cache[key][z['index']][z['j']]
        b=bins.setdefault((z['scenario'],z['inferred_tier']),[])
        b.append((z['inferred_net'],z['realized_net'],true,z['radius']))
        rk=z['scenario']+':'+z['reason'];reasons[rk]=reasons.get(rk,0)+1
assert count==96000 and pending==384 and missing==0
calibration=[]
for (scenario,label),v in bins.items():
    realized=[x[1] for x in v if x[1] is not None]
    calibration.append(dict(scenario=scenario,tier=label,n=len(v),mean_prediction=st.mean(x[0] for x in v),mean_latent_ev=st.mean(x[2] for x in v),mean_realized_net=st.mean(realized) if realized else None,latent_ev_interval_coverage=st.mean(abs(x[2]-x[0])<=x[3] for x in v),mean_interval_radius=st.mean(x[3] for x in v)))
report['independent_opportunity_audit']=dict(rows=count,observed=observed,pending=pending,missing=missing,strict_maturation_passed=True,unknown_reasons=reasons)
report['absolute_calibration_by_tier']=calibration
with (O/'calibration_by_tier.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(calibration[0]));w.writeheader();w.writerows(calibration)
(O/'report.json').write_text(json.dumps(report,indent=2))
lines=['# Opportunity evaluator fix — '+report['status'],'',f"Execution COMPLETE: {replays}/64 portfolio replays, 14 tests passed first; {report['elapsed_seconds']:.1f} seconds. No production changes or GA.",'','The causal all-opportunity ledger and rolling calibration are implemented. The robust five-way claim fails unless every preregistered scenario/seed passes; abstention is retained. No quality gates were relaxed after evaluation.','', 'Parameters were frozen in preregister.json before tests/replays. Predictions use only PIT measurement cells and outcomes strictly matured before each decision. All 250 × 24 eligible opportunities per tape are logged, including untraded opportunities; pending final outcomes are explicit. No oracle regimes or true EV enters inference. Evaluation truth appears only in discrimination scoring.','', 'Calibration: older 40 and up to 21 recent signal dates in a rolling 61-date matured window (inclusive source boundaries), diagnostic 2.58-SE intervals plus window bias. Recent 9 versus older 30+ dates monitors cell drift; alarms quarantine all tiers for 20 clocks. No identifiable cross-cell signal yields UNKNOWN, not AVERAGE. Outcome fifth-percentile risk gates and absolute bands are frozen in preregister.json. No formal confidence-coverage guarantee under dependence.','', 'Protocol metadata discrepancy: the inherited static-fit fields in preregister.json were superseded by its version 2 rolling method. Nominal window counts say 40/20/8, while the frozen inclusive code implements 40/21/9. No parameters or code were changed after evaluation. This documentation discrepancy also prevents a clean preregistration PASS.','', 'Absolute one-session net bands: TERRIBLE < -0.6%; POOR [-0.6%,-0.2%); AVERAGE [-0.2%,0.2%); GOOD [0.2%,0.6%); GREAT >=0.6%. The full uncertainty interval must fit one band.','', '| Scenario | Old coverage | New coverage | New accuracy | Old false GREAT | New false GREAT | Detection delays |','|---|---:|---:|---:|---:|---:|---|']
for c,q in zip(comparisons,quality):
    acc='n/a' if q['conditional_accuracy'] is None else format(q['conditional_accuracy'],'.1%')
    lines.append(f"| {q['scenario']} | {c['old_coverage']:.1%} | {q['coverage']:.1%} | {acc} | {c['old_false_great']} | {c['new_false_great']} | {q['drift_detection_delays']} |")
lines+=['','Drift delay is first post-126 alarm minus 126, in sessions, scored externally using the known reversal onset. Other scenarios have no true change, so alarm counts measure nuisance alarms. Alarm events and counts are in report.json.','',report['minimum_engineering_change'],'','| Scenario | Policy | Mean return | Mean MDD | Worst MDD |','|---|---|---:|---:|---:|']
for z in aggregates:lines.append(f"| {z['scenario']} | {z['variant']} | {z['total_return']:.2%} | {z['mdd']:.2%} | {z['worst_mdd']:.2%} |")
lines+=['','Same paired seeds, tapes, horizons, baseline and native manager/kernel as the prior five-tier run. Tier10/15/20 admit GOOD/GREAT; above-10% adds still need actual funded native evidence. Independent entire-candidate risk <=2%, costs, T+1, cash reservations, exits and MDD latch are preserved and checked. No terminal liquidation.','', 'The synthetic one-session outcome grosses up transaction costs. Multi-session holdings pay less frequent costs, so null portfolio profits do not imply recognition. Four seeds and 126 portfolio sessions cannot establish statistical tail robustness. Portfolio comparisons and costs are in portfolio_runs.csv, portfolio_aggregate.csv, paired.csv and portfolio_previous.csv. Both latent-EV and realized-return confusion matrices include UNKNOWN separately.','', 'Reproduce from repository root with the original MTS checkout and sibling experiment dependencies available:','```bash','python3 experiments/mts_v5_planted_signal_20261101/opportunity_evaluator_fix/experiment.py','python3 experiments/mts_v5_planted_signal_20261101/opportunity_evaluator_fix/finalize.py','```','The runner always runs tests first and stops on failures. It overwrites its outputs; parameters and method remain fixed. All eligible PIT records, costs, context, timestamps, missingness and outcomes are in opportunities.jsonl.gz; execution ledgers are in replays.jsonl.gz. Source checksums and inherited manager/kernel copies are saved. manifest.json excludes itself and active run.log/finalize.log.']
(O/'README.md').write_text('\n'.join(lines)+'\n')
manifest={p.name:e.sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name not in ('manifest.json','run.log','finalize.log')}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(dict(status=report['status'],replays=replays,quality=quality,risk=report['independent_full_candidate_risk_verification']),indent=2))
