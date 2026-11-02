"""Read-only-result analysis and documentation. Executes no tapes or portfolio replays."""
import csv,gzip,hashlib,json,statistics as st
from pathlib import Path
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def avg(xs):return st.mean(xs) if xs else None
def ranks(xs):
    order=sorted(range(len(xs)),key=xs.__getitem__);r=[0.]*len(xs);i=0
    while i<len(xs):
        j=i+1
        while j<len(xs) and xs[order[j]]==xs[order[i]]:j+=1
        for k in range(i,j):r[order[k]]=(i+j-1)/2
        i=j
    return r
def corr(x,y):
    x=ranks(x);y=ranks(y);mx=avg(x);my=avg(y);den=(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))**.5
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/den if den else None

def main():
    if (O/'raw_report.json').exists():r=json.loads((O/'raw_report.json').read_text())
    else:
        r=json.loads((O/'report.json').read_text());(O/'raw_report.json').write_text(json.dumps(r,indent=2))
    original=json.loads((O/'commitment.json').read_text());assert all(sha(p)==h for p,h in original['sources'].items())
    correction=json.loads((O/'corrected_benchmark_results.json').read_text());paired=[]
    for b in correction['runs']:
        c=next(x for x in r['portfolio_runs'] if x['seed']==b['seed'] and x['scenario']=='learnable' and x['variant']=='candidate')
        paired.append(dict(seed=b['seed'],scenario='learnable',candidate_return=c['total_return'],benchmark_return=b['total_return'],return_delta=c['total_return']-b['total_return'],cagr_delta=c['cagr']-b['cagr'],mdd_delta=c['mdd']-b['mdd'],cost_delta=c['costs']-b['costs']))
    with (O/'corrected_benchmark_paired.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
    audits={};funded={};tierstats={};daily={}
    with gzip.open(O/'opportunities.jsonl.gz','rt') as f:
        for line in f:
            z=json.loads(line);key=(z['seed'],z['scenario'],z['variant']);a=audits.setdefault(key,dict(n=0,false_great=0,false_great_net_sum=0.,false_great_loss_sum=0.,horizon_mismatch_max=0.,funded=0))
            a['n']+=1;a['funded']+=z['funded'];a['horizon_mismatch_max']=max(a['horizon_mismatch_max'],abs(z['horizon_mismatch']))
            if z['true_ev']==-.012 and z['inferred_tier']=='GREAT':a['false_great']+=1;a['false_great_net_sum']+=z['realized_net'];a['false_great_loss_sum']+=min(0,z['realized_net'])
            if z['funded']:funded[(z['seed'],z['scenario'],z['variant'],z['index'],z['j'])]=z
            tierstats.setdefault((z['scenario'],z['variant'],z['inferred_tier']),[]).append(z['realized_net'])
            daily.setdefault((*key,z['index']),[[],[]]);daily[(*key,z['index'])][0].append(z['inferred_net']);daily[(*key,z['index'])][1].append(z['realized_net'])
    maxerr=0.;cashmin=1e99;riskmax=0.;tradecount=0
    with gzip.open(O/'replays.jsonl.gz','rt') as f:
        for line in f:
            z=json.loads(line);cashmin=min(cashmin,min(d['cash'] for d in z['daily']))
            if z['variant'] not in ['candidate','iteration2']:continue
            for t in z['trades']:
                row=funded[(z['seed'],z['scenario'],z['variant'],t['signal'],t['j'])];assert t['exit_index']==t['entry_index']+1
                maxerr=max(maxerr,abs(t['net']-row['realized_net']));riskmax=max(riskmax,t['modeled_risk']);tradecount+=1
    assert maxerr<1e-12 and cashmin>=-1e-8 and riskmax<=.02
    cells=[]
    for key,a in audits.items():cells.append(dict(seed=key[0],scenario=key[1],variant=key[2],mean_daily_spearman=avg([v for k,xy in daily.items() if k[:3]==key and (v:=corr(*xy)) is not None]),**a))
    with (O/'ledger_audit.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(cells[0]));w.writeheader();w.writerows(cells)
    for score in r['discrimination']:
        if score['variant']=='iteration2':
            score['date_mean_predictive_interval_coverage']=None
            score['date_mean_interval_note']='Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis.'
    r['post_freeze_benchmark_correction']=dict(reason=correction['reason'],additional_replays=4,evaluated_scenarios=['learnable'],incomplete_scenarios=['null','reversal','outer_noise'],untouched_test=False,runs=correction['runs'],paired=paired,invalid_original_rows="All variant=benchmark rows in metrics.csv and corresponding paired comparisons are invalid as independent controls; retained as evidence of ranking confound.")
    r['total_replays_including_phase_a']=62;r['compute_accounting']=dict(initial_phase_a_seconds=1.968,runner_seconds=r['elapsed_seconds'],benchmark_correction_seconds=correction['elapsed_seconds'],total_measured_seconds=1.968+r['elapsed_seconds']+correction['elapsed_seconds'],phase_a_replays=6,phase_b_replays=52,post_freeze_control_correction_replays=4,limit=64,stopped=True)
    r['artifact_audit']=dict(funded_trade_matches=tradecount,max_net_ledger_error=maxerr,min_cash=cashmin,max_modeled_risk=riskmax,frozen_sources_match=True)
    r['recommendation_status']={
      'P1_gate':'IMPLEMENTED sensor/full disagreement; no price-only veto, train-only threshold; stable coverage recovers.',
      'P2_independent_dates':'IMPLEMENTED 734 sessions,400 fit/200 cal dates, original bands. Radii pass but per-seed five-tier support fails.',
      'P3_outer_holdout':'PARTIAL four OS entropy seeds after local hash commitment, separate noise variant; trusted public timestamp unavailable. All evaluated tapes now viewed.',
      'P4_disjoint_calibration':'IMPLEMENTED embargoed chronological disjoint ranges; mutation tests show calibration cannot alter point coefficients. Statistical correlation need not literally be zero in finite samples.',
      'P5_sequential_monitor':'IMPLEMENTED cell/look union bound with stated DGP subGaussian envelope; stable0/12 but only4 independent seeds. Reversal22-session lag is unsafe.',
      'P6_horizon_ledger':'IMPLEMENTED all-opportunity one-session open-to-exit ledger, matched funded horizons, costs/cash/final liquidation/risk/gap audits. Original variable holding manager not replayed; synthetic one-session harness only.',
      'P7_real_PIT':'ADAPTER/AUDIT ONLY; no accepted real rows or real OOS IC. Local provisional artifacts lack complete revision/release provenance. NO alpha claim.'}
    r['real_pit_audit']['local_evidence']=[dict(path=str(p),sha256=sha(p),reason=reason) for p,reason in [(O.parents[2]/'pilot_2019_sample.csv','Annual summarized provisional observations; no release/revision provenance.'),(O.parents[2]/'reports/offline-provisional-2019/observations.csv','Monthly provisional observations; no release/vintage/source-hash fields.'),(O.parents[2]/'manifest.json','Explicit certified=false, PIT coverage unverified;2019/2020 contaminated.')]]
    r['limitations']=['Four seeds do not establish a <=5% stable alarm probability;0/12 paired scenario units is not12 independent seeds.','Conditional mean intervals and latent-individual/realized tier confusion are different estimands. Date_mean_predictive_interval_coverage is a diagnostic hit rate for date means, not nominal prediction coverage.','Sensor/full gate threshold calibrated only on fit distribution; no formal conformal reliability guarantee.','Benchmark control correction is post-freeze, with learnable-only coverage; no independent benchmark evidence for other scenarios.','No real SGOV data, SGOV-relative return unavailable. Cash zero is a synthetic control.','Source freeze manifests cover new core files; imported original dependency hashes were not committed comprehensively before seed generation.','Injected sensors and cost-grossup DGP cannot establish real alpha. Fresh seeds do not make the inherited DGP untouched.','Original baseline estimator unmodified, but its portfolio policy uses new one-session harness and has126-date warmup rather than candidate400 fit/200 cal dates.','CAGR/MDD from synthetic126-session windows and open marks only; no intraday risk or aggregate2% risk guarantee.']
    r['engineering_blocker']='FAIL: five-tier support missing on2/4 stable seeds; reversal442 false GREAT before22-session latch and negative net return. Real PIT information and trusted timestamp absent; corrected independent benchmark coverage incomplete.'
    r['recommended_next_decision']='Do not promote or optimize this bundle. Retain as gate-repair evidence; first specify acceptable reversal exposure and acquire provenance-complete real PIT predictors. Use a new externally committed protocol for any future validation.'
    r['execution_status']='COMPLETE_PLANNED_RUN_WITH_INCOMPLETE_CORRECTED_BENCHMARK_COVERAGE'
    (O/'report.json').write_text(json.dumps(r,indent=2))
    # Human report is assembled below from measured aggregates, not a success claim.
    learn=[s for s in r['discrimination'] if s['variant']=='candidate' and s['scenario']=='learnable'];rev=[s for s in r['discrimination'] if s['variant']=='candidate' and s['scenario']=='reversal']
    lines=['# Iteration5: FAIL — bounded engineering experiment','',f"Nine unit/integration tests passed twice. Total62 portfolio replays:6 test probes,52 planned runs,4 post-freeze control corrections. Measured compute {r['compute_accounting']['total_measured_seconds']:.2f}s, below720s. No GA or production edits; every new file is in this directory. Existing unrelated workspace changes were left alone.",'','The gate repair restores stable coverage; it does not certify the bundle. Original bands remain ±0.2%/±0.6%. All three middle radii are below0.002 on4/4 learnable seeds, yet only2/4 seeds support every tier. Radius alone is insufficient when a fitted center approaches a boundary. No widened bands or forced classes were used.','',f"Stable learnable coverage ranges {min(s['coverage'] for s in learn):.1%}–{max(s['coverage'] for s in learn):.1%}; conditional individual-latent tier accuracy {min(s['conditional_accuracy'] for s in learn):.1%}–{max(s['conditional_accuracy'] for s in learn):.1%}. Stable false GREAT/TERRIBLE count0. Conditional cell-mean interval coverage20/20 learnable cells, and20/20 outer-noise cells; this small synthetic sample establishes no nominal coverage guarantee.",'',f"Reversal: {sum(s['false_great_on_terrible'] for s in rev)} true-TERRIBLE opportunities labeled GREAT before the22-session return-drift latch on every seed. Mean candidate reversal return {avg([m['total_return'] for m in r['portfolio_runs'] if m['variant']=='candidate' and m['scenario']=='reversal']):.2%}. Zero stable alarms across12 seed/scenario units, but only4 independent seeds; even0/4 gives a52.7% one-sided95% upper bound on seed alarm probability. Reported0/12 upper bound is descriptive and assumes independence that paired scenarios do not have.",'','## Measured portfolio results','', 'Arithmetic means of per-seed metrics. Dollar costs on initial$100,000; all entry/exit costs paid, one-session horizon, T+1 sale proceeds, terminal liquidation. These large injected-signal returns are not real alpha.','', '| Scenario / policy | Return | CAGR | MDD | Costs |','|---|---:|---:|---:|---:|']
    for scen in ['learnable','null','reversal','outer_noise']:
        for var in ['candidate','iteration2','scaled']:
            ms=[m for m in r['portfolio_runs'] if m['scenario']==scen and m['variant']==var]
            if ms:lines.append(f"| {scen} / {var} | {avg([m['total_return'] for m in ms]):.2%} | {avg([m['cagr'] for m in ms]):.2%} | {avg([m['mdd'] for m in ms]):.2%} | ${avg([m['costs'] for m in ms]):,.0f} |")
    bs=correction['runs'];lines.append(f"| learnable / corrected equal universe | {avg([m['total_return'] for m in bs]):.2%} | {avg([m['cagr'] for m in bs]):.2%} | {avg([m['mdd'] for m in bs]):.2%} | ${avg([m['costs'] for m in bs]):,.0f} |")
    lines+=['','Original benchmark rows are INVALID independent controls: purchase ranking used forecasts under cash scarcity. The corrected equal-notional control accepts prices only and checks equal entries across all24 names. It ran on four already viewed learnable tapes, consuming four spare replay slots; other scenarios remain incomplete. Corrected comparisons are descriptive after evaluation. Cash control is0 return/CAGR/MDD/cost; real SGOV comparison is unavailable.','',f"Maximum measured per-trade modeled risk {riskmax:.4%}; no gap-loss exceedances in the primary replays. An explicit50% gap test demonstrates realized losses can exceed modeled risk. Funded candidate/baseline ledger net reconciliation error {maxerr:.2g}; no horizon mismatch. Tier metrics cover all opportunities, including unfunded and abstentions; these sums are not attainable portfolio returns.",'','## Method and evidence','', 'Read the full external review and original experiment code; all original reports were parsed. 734 synthetic sessions,24 assets, random class/sensor draws with original sensor noise and original noise law. Outer variant increases return noise25%. Fit signals0–399, calibration403–602, test606–731. Outcomes are usable at signal+3; fit/cal/test execution intervals are disjoint. Each date-cell mean counts once; under this iid-date DGP dates are independent. Cross-cell dependence remains and is covered by union bounds. More complex serial dependence is not validated.','', 'Sensor-cell date means and full-model lag-price slopes fit only training data. The99th percentile disagreement threshold and identifiability filter use training only. Independent calibration widens uncertainty through bias and SE, never changes coefficients. Approximate cell intervals use2.576SE with no individual-class guarantee. The monitor uses a conservative0.018 subGaussian envelope for the prescribed synthetic law, five cells and at most26 looks, with total alpha0.05. This envelope is not a learned real-market guarantee.','', 'Iteration2 predict is imported unchanged on the last126 warmup+126 test sessions of the same fresh tapes. Bar conversion preserves exact net returns under its inherited multiplicative costs. Its calibration pooling violation is retained and explicitly uncertified. Candidate has a longer fit, so this is a paired engineering comparison, not a pure gate-only ablation. The full-model ungated ablation isolates the gate on the candidate fit. Scaled15% allocations are learnable-only; see paired.csv for incremental returns/MDD/costs.','', 'Confusion matrices for individual latent and realized tiers, all-opportunity recalls, GREAT→TERRIBLE and TERRIBLE→GREAT, per-cell diagnostics, conditional mean interval coverage, drift reasons/lags, and seed-level metrics are in report.json. tier_metrics.csv holds support and net returns; ledger_audit.csv includes daily rank IC and realized loss sums for false GREAT. opportunities.jsonl.gz includes every test opportunity, actual funded flags/debits and open-to-exit outcomes; replays.jsonl.gz contains funded trades and daily cash/NAV.','', 'preregister.json and core Python SHA256 hashes were committed locally before seeds.json was drawn from OS entropy. No trusted external/public timestamp or hardware RNG attestation exists. Fresh-seed tapes were untouched at generation; they are now viewed. The inherited DGP and developer choices were informed by earlier work. No untouched test remains, and the benchmark correction is explicitly post-freeze. Original core hashes still match commitment.json. No outcome-based tuning or reruns of the candidate occurred.','', 'PIT readiness: local policy/manifest and provisional CSV headers show no complete release/revision/vintage provenance. No real rows were admitted or fabricated. pit_schema.json and validate_pit provide a strict row adapter, not source authenticity or statistical certification. Real OOS IC>0.1 cannot be assessed.','', '## Recommendations implemented versus blocked','']
    for k,v in r['recommendation_status'].items():lines.append(f'- **{k}:** {v}')
    lines+=['','## Run and inspect','', '```bash','PYTHONPATH=/opt/Momentum-Trading-System_v5-alpha python3 -m unittest discover -s experiments/mts_v5_planted_signal_20261101/discrimination_iteration5 -p "test_*.py" -v','```','', 'Tests are rerunnable but execute three synthetic portfolio probes per invocation. The archived accounting includes exactly two test invocations; no more runs are scheduled. experiment.py refuses holdout reuse while commitment.json exists. Its archived frozen runner preserves the original benchmark bug for audit; use corrected_benchmark.replay_equal for a valid price-only equal-universe control. A future full experiment needs a new directory/protocol/commitment and its own replay budget; do not delete this commitment to claim a fresh test. finalize.py analyzes archived results without running portfolios. checksums.json covers artifacts; raw_report.json preserves the pre-correction machine output.','', '**Engineering blocker:** '+r['engineering_blocker'],'','**Next decision:** '+r['recommended_next_decision']]
    (O/'README.md').write_text('\n'.join(lines)+'\n')
    (O/'checksums.json').write_text(json.dumps({p.name:sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='checksums.json'},indent=2))
    print(r['status'],r['artifact_audit'],r['compute_accounting'])
if __name__=='__main__':main()
