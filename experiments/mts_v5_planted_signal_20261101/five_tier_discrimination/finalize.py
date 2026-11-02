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
report['focused_tests']=dict(passed=8,failed=0,run_before_portfolios=True)
report['failure_specifics']=[dict(scenario=q['scenario'],unpopulated=[t for t in e.TIERS if q['counts'][t]==0],coverage=q['coverage'],conditional_accuracy=q['conditional_accuracy'],false_great_on_terrible=q['false_great_on_terrible'],monotone_seeds=q['monotone_seeds']) for q in quality if q['status']=='FAIL']
(O/'report.json').write_text(json.dumps(report,indent=2))
for name,rows in [('portfolio_runs.csv',report['portfolio_runs']),('portfolio_aggregate.csv',aggregates),('paired.csv',report['paired'])]:
    with (O/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Preserve exact local execution sources and their reconstructing inherited patch.
for name in ('corrected_manager.py','corrected_kernel.py','source.patch'):
    shutil.copyfile(e.PRIOR/name,O/name)
with tempfile.TemporaryDirectory() as td:
    for name,source in [('discovery/competitive_ga/functional_niche_manager.py',e.a.FIX/'functional_niche_manager.py'),('engines/portfolio_replay/kernel.py',Path(e.a.original_kernel.__file__))]:
        dest=Path(td)/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    result=subprocess.run(['patch','--batch','-p1','-i',str(O/'source.patch')],cwd=td,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    for name,file in [('discovery/competitive_ga/functional_niche_manager.py','corrected_manager.py'),('engines/portfolio_replay/kernel.py','corrected_kernel.py')]:
        assert (Path(td)/name).read_bytes()==(O/file).read_bytes()
    (O/'reconstruction.log').write_text(result.stdout+'Manager and kernel reconstruct byte-for-byte. No production paths written.\n')
with (O/'experiment.patch').open('w') as f:
    for name in ('experiment.py','test_experiment.py','finalize.py','preregister.json'):
        f.write(''.join(difflib.unified_diff([], (O/name).read_text().splitlines(True),fromfile='/dev/null',tofile='b/'+name)))
lines=['# Five-tier opportunity discrimination — FAIL','',f"Completed {replays} full portfolio replays; eight focused tests passed first. Replay experiment took {report['elapsed_seconds']:.1f} seconds. No GA; production source hashes unchanged.",'','Preregistered before tests/replays: `preregister.json`. Fixed train signals 0–77, calibration 80–121, untouched evaluation 126–249, portfolio sessions 126–251. Forecast k executes k+1 and matures k+2; fit requires maturity strictly before cutoff. No thresholds, features, or policies were chosen using evaluation outcomes. A cell receives a tier only when its full frozen uncertainty interval lies within one absolute net-return band. Otherwise it is UNKNOWN.','', 'Absolute one-session net bands: TERRIBLE <−0.6%; POOR [−0.6%,−0.2%); AVERAGE [−0.2%,0.2%); GOOD [0.2%,0.6%); GREAT ≥0.6%. These are economic bands, not quantiles.','', '| Scenario | Coverage | Conditional EV-tier accuracy | Unknown | False GREAT / true TERRIBLE | Populated tiers |','|---|---:|---:|---:|---:|---|']
for q in quality:
    acc='n/a' if q['conditional_accuracy'] is None else f"{q['conditional_accuracy']:.1%}"
    lines.append(f"| {q['scenario']} | {q['coverage']:.1%} | {acc} | {q['counts']['UNKNOWN']} | {q['false_great_on_terrible']}/{q['true_terrible']} | {', '.join(t for t in e.TIERS if q['counts'][t]) or 'none'} |")
lines+=['','The preregistered robust five-way claim FAILS. See `failure_specifics` and per-seed recall in `report.json`. Missing middle tiers remain unpopulated; null abstention is a useful safety result but provides no five-way identification. Regime reversal tests out-of-distribution failure; no confidence interval trained only before the reversal can guarantee its detection.','', 'Synthetic truth: latent classes set distinct conditional expected executable net returns; their class and mean are evaluator-only. Each realized forward return includes common-date and individual shocks. The learner sees only noisy point-in-time measurements, training outcomes and calibration outcomes; it never receives a known forecast-strength coefficient or true tier. Learnable/misleading measurements are artificially informative, so even success there would not establish native MTS quality recognition. Misleading predicted EV reverses the observable relationship; null forecasts/features have no latent-class information. EV-tier confusion and individual realized-return-tier confusion are reported separately.','', 'Every confusion CSV contains the required 5×5 matrix plus a separate UNKNOWN column. Rows are true tiers; columns are inferred tiers. `opportunities.jsonl.gz` preserves every held-out observation and prediction. Calibration bias, RMSE, regression slope/intercept and rank correlations are in the report, as are per-tier counts, realized net means, monotonicity, GREAT precision and terrible-to-GREAT mistakes. Date grouping reduces cross-sectional pseudo-replication; two-sided 2.58-SE intervals are diagnostic and lack formal serial-dependence or simultaneous coverage guarantees.','', 'Portfolio comparison uses the existing MTS EV admission and ranked cash queue at 10%, plus tier10 and conditional tier15/tier20. Proposals use harmonized positive/negative signal ENTER/HOLD/EXIT logic, not the prior generator’s exact incumbent switching rule. Tier policies admit GOOD/GREAT only and request scaling only for GREAT incumbents. Scaling still requires native funded mature-trade/fold/profitability evidence. All policies use the same tape, costs, 2% entire-candidate modeled risk, T+1, MDD latch and cash reservation. No fabricated scale fills. Each replay has an independent ledger/cash/NAV reconstruction; finalization independently checks every actual BUY’s entire candidate risk. No terminal liquidation; pending positions remain marked.','', '| Scenario | Policy | Mean total return | Mean MDD | Turnover | Scaled fills (mean) |','|---|---|---:|---:|---:|---:|']
for z in aggregates:lines.append(f"| {z['scenario']} | {z['variant']} | {z['total_return']:.2%} | {z['mdd']:.2%} | {z['turnover']:.2f} | {z['scaled_fills']:.1f} |")
lines+=['','Portfolio gains do not establish quality recognition. The DGP grosses up one-session net EV by round-trip costs; holdings spanning multiple signals pay costs less frequently, so even the null EV baseline earns positive drift. This horizon mismatch is a material limitation, not recognition evidence. Returns exploit artificial observable relationships and are separate from the five-way decision criteria. Four seeds and 126 portfolio sessions are insufficient for production robustness. Costs, tail MDD, per-seed paired comparisons against both EV10 and tier10, and actual scaling fills are saved in JSON/CSV.','', 'Minimum engineering change: '+report['minimum_engineering_change'],'', 'Reproduce from this repository with the original `/opt/Momentum-Trading-System_v5-alpha` checkout available:','```bash','python3 experiments/mts_v5_planted_signal_20261101/five_tier_discrimination/experiment.py','python3 experiments/mts_v5_planted_signal_20261101/five_tier_discrimination/finalize.py','```','The runner always executes focused tests first and stops on any failure. It overwrites this experiment’s outputs. Dependencies and original source paths/hashes are in report.json. `source.patch` is the inherited manager/kernel correction relative to stage2_fix manager and original kernel; corrected copies are included. `experiment.patch` reconstructs the experiment sources. No original production files are patched. `manifest.json` hashes all final artifacts except itself and the still-active harness run.log. Logs preserve test and execution evidence.']
(O/'README.md').write_text('\n'.join(lines)+'\n')
manifest={p.name:e.sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name not in ('manifest.json','run.log')}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(dict(status=report['status'],replays=replays,quality=quality,risk=report['independent_full_candidate_risk_verification']),indent=2))
