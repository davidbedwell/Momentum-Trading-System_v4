"""Report-only summaries and artifact checks; executes no portfolios."""
from pathlib import Path
import json,statistics as st,hashlib,gzip
P=Path(__file__).resolve().parent
r=json.loads((P/'report.json').read_text());runs=r['runs']
r['paired']=[p for p in r['paired'] if p['reference']!='same seed existing 15%']
keys=('cagr','mdd','calmar','exposure','turnover','scaled_fills','full_target_fills','risk_rejections','cap_rejections','cash_rejections','unique_rejected')
for q in ('weak','misnull'):
    rr=[z for z in runs if z['quality']==q and z['control']=='existing' and z['variant']=='scale20']
    dd=[{k:z[k]-next(b for b in runs if b['quality']==q and b['control']=='existing' and b['variant']=='scale15' and b['seed']==z['seed'])[k] for k in keys} for z in rr]
    r['paired'].append(dict(quality=q,control='existing',variant='scale20',reference='same seed existing 15%',n=len(rr),cagr_wins=sum(d['cagr']>1e-12 for d in dd),mean_delta={k:st.mean(d[k] for d in dd) for k in keys},median_delta={k:st.median(d[k] for d in dd) for k in keys},min_cagr_delta=min(d['cagr'] for d in dd),max_cagr_delta=max(d['cagr'] for d in dd),per_seed=[dict(seed=z['seed'],**d) for z,d in zip(rr,dd)]))
for g in r['aggregates']:
    rr=[z for z in runs if (z['quality'],z['control'],z['variant'])==(g['quality'],g['control'],g['variant'])]
    g['totals']={k:sum(z[k] for z in rr) for k in ('scaled_fills','full_target_fills','risk_rejections','cap_rejections','cash_rejections','unique_rejected','reservation_opportunities')}
    g['tail']['median_cagr']=st.median(z['cagr'] for z in rr)
    g['tail']['min_calmar']=min(z['calmar'] for z in rr)
for p in r['paired']:
    p['n']=len(p['per_seed'])
    p['median_delta']={k:st.median(z[k] for z in p['per_seed']) for k in p['mean_delta']}
with gzip.open(P/'completed_replays.jsonl.gz','rt') as f:
    records=[json.loads(l) for l in f]
assert len(records)==94
assert len({(z['seed'],z['quality'],z['control'],z['variant']) for z in records})==94
assert all(len([z for z in runs if z['quality']==q and z['control']=='existing' and z['variant']==v])==12 for q in ('weak','misnull') for v in ('ev','scale15','scale20'))
assert r['full_portfolio_attempts_upper_bound']==96
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in r['source_sha256'].items())
r['max_actual_candidate_loss']=max(z['max_actual_candidate_loss'] for z in runs)
r['max_reconciliation_error']=max(z['max_reconciliation_error'] for z in runs)
r['costs']={'execution':__import__('experiment').r.s1.COSTS,'round_trip':__import__('experiment').r.s1.ROUND_TRIP}
r['artifact_validation']={'complete_gzip_records':94,'unique_run_keys':94,'all_primary_groups_have_12_seeds':True,'source_hashes_rechecked':True}
r['conclusions']=['Weak signals: 15% adds 0.475 percentage points mean CAGR versus 10%, with 0.085 points more mean MDD; 20% provides no material incremental benefit and no full 20% fills.', 'Misnull: 15/20% increase sample mean CAGR by 1.370/2.549 points but worsen worst-seed CAGR and maximum MDD; 8 of 12 paired CAGR improvements do not validate predictive reliability.', 'Hypothetical gate produces no above-10% adds and matches same-seed 10% outcomes for all 11 control seeds; this is a diagnostic denial control, not a validated production gate.']
(P/'report.json').write_text(json.dumps(r,indent=2))
lines=['# Scaling robustness — completed','',
'Completed all 72 primary comparisons: weak and confidently miscalibrated null signals, 10/15/20% caps, seeds 1101–1112, 252 sessions. Also completed 22 hypothetical reliability-gate controls on seeds 1101–1111. Synthetic diagnostic only; no historical-alpha or production calibration claim.','',
'All 10 tests passed before portfolio execution. `test_reliability.py` is now beside the runner; its resolved path and import were checked. `run_tests.py` resolves paths from its own location, so it works from any working directory. Tests cover standalone cost-inclusive loss clipping, other holdings not consuming the candidate budget, cash reservation/release, T+1, MDD exits, reliability warmup and exclusion of current/future outcomes. See `resume_tests.log`.','',
'Budget: 28 prior attempts conservatively counted (26 saved, one result-assembly failure, up to one interrupted run), 68 new attempts, 96 total upper bound. Reused 26 records; no additional attempts are available. Portfolio resume elapsed %.1f seconds. No GA or production changes.'%r['elapsed_seconds'],'',
'| Signal | Gate | Cap | Seeds | Mean CAGR | Mean MDD | Mean Calmar | Exposure | Turnover | Above-10% adds | Full target fills | Worst CAGR | Worst MDD |',
'|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for g in r['aggregates']:
    m=g['means'];t=g['tail'];cap={'ev':10,'scale15':15,'scale20':20}[g['variant']]
    lines.append(f"| {g['quality']} | {g['control']} | {cap}% | {g['n']} | {m['cagr']:.2%} | {m['mdd']:.2%} | {m['calmar']:.3f} | {m['exposure']:.2%} | {m['turnover']:.2f} | {g['totals']['scaled_fills']} | {g['totals']['full_target_fills']} | {t['min_cagr']:.2%} | {t['max_mdd']:.2%} |")
lines+=['','Turnover is total traded notional divided by daily NAV, summed over the 252-session run. Fill counts are sums across seeds; performance columns are seed means. Full target counts apply to incumbent scaling adds only; 10% entry fills are not counted as scaling.','',
'| Signal | Gate | Comparison | Mean CAGR delta (pp) | Mean MDD delta (pp) | Mean Calmar delta | CAGR wins | CAGR delta range (pp) |','|---|---|---|---:|---:|---:|---:|---:|']
for p in r['paired']:
    cap={'scale15':15,'scale20':20}[p['variant']];ref='15' if '15%' in p['reference'] else '10';d=p['mean_delta']
    lines.append(f"| {p['quality']} | {p['control']} | {cap}% vs {ref}% | {100*d['cagr']:.3f} | {100*d['mdd']:.3f} | {d['calmar']:.3f} | {p['cagr_wins']}/{p['n']} | {100*p['min_cagr_delta']:.3f} to {100*p['max_cagr_delta']:.3f} |")
lines+=['',
'Every comparison uses the same verified tape, costs, callback logic, T+1 rules, exits and 20% MDD admission latch. Existing evidence pools funded exits; its realized inputs depend on portfolio fills, so identical causal evidence logic does not imply identical realized evidence across caps. There is no independent predictive calibration claim.','',
'The hypothetical gate additionally requires 30 matured forecast dates, positive average observed net return, and nonnegative mean forecast error plus two standard errors. Forecast k executes k+1 and matures k+2; only outcomes strictly before the current close are read. Date averages avoid counting correlated stocks as independent. The two-SE margin is an unvalidated diagnostic under serial dependence. These controls are separately labeled and use 11 seeds, compared with their same-seed existing 10% baselines.','',
'Each actual BUY independently satisfies full post-add candidate weight × (max(2%% stop, candidate gap) + round-trip cost) ≤2%%. Other holdings do not consume this trade budget. Maximum checked candidate loss: %.8f; maximum NAV/cash/quantity reconciliation error: %.3g. Risk/cap/cash rejection flags overlap: `runs` stores unique rejection unions and exact overlap counts, so marginal counts must not be added.'%(r['max_actual_candidate_loss'],r['max_reconciliation_error']),'',
'Actual above-10% adds require an incumbent BUY with resulting opening weight above 10.001%; passive drift is excluded. Full targets require opening weight at least requested target minus 1e-9. `report.json` contains every run, paired per-seed changes, rejection counts, tails, latch seeds and fill counts.','',
'The prior archive SHA-256 and generating runner, manager, kernel and patch hashes matched `prior_manifest.json`. Its gzip trailer was truncated at interruption. Only 26 complete JSON records were recovered; their individual hashes and run identities are in `replay_verification`. All were revalidated through 252-session ledger/cost/T+1/NAV/risk and scaling-fill reconstruction. Incomplete trailing content was discarded. `completed_replays.jsonl.gz` is a complete, readable 94-record archive. Pending orders were absent from the old archive and are omitted from comparison metrics.','',
'`source.patch` reconstructs both corrected experiment modules byte-for-byte from the Stage2_fix manager and original production kernel (`reconstruction.log`). Source paths and SHA-256 values are recorded and rechecked in `report.json`. The patch is incremental to Stage2_fix; its prior manager fixes are required. No original production source was changed.','',
'Artifacts: `experiment.py` retains the checksummed prior generating source; `resume_experiment.py` performs the bounded resume and persists its attempt ledger before each run; `finalize_report.py` adds report-only summaries; `prior_report.json` and prior error logs preserve the failure history. `manifest.json` hashes final artifacts.']
(P/'README.md').write_text('\n'.join(lines)+'\n')
manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in P.iterdir() if f.is_file() and f.name not in ('manifest.json','resume.log')}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'status':r['status'],'attempts':96,'elapsed':r['elapsed_seconds'],'max_loss':r['max_actual_candidate_loss'],'primary':[(g['quality'],g['variant'],g['means']['cagr'],g['totals']['scaled_fills']) for g in r['aggregates'] if g['control']=='existing']},indent=2))
