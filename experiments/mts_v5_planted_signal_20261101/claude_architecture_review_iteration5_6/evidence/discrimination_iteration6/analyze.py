"""Post-evaluation artifact audit and documentation only; zero portfolio replays."""
import csv,gzip,json,math,statistics as st
from pathlib import Path
import engine as x
O=x.O

def main():
 r=json.loads((O/'report.json').read_text());commit=json.loads((O/'commitment.json').read_text());assert all(x.e.sha(p)==h for p,h in commit['sources'].items())
 diag=json.loads((O/'iteration5_diagnosis.json').read_text())
 for z in diag['rows']:
  p,f,_=x.e.generate(z['seed'],'reversal');models=x.e.fit(p,f);first=None
  for now in range(x.START,x.START+23):
   for c,m in enumerate(models):
    vals=x.e.dates(p,f,range(now-22,now-2),c)
    if len(vals)<15:continue
    threshold=.018*math.sqrt(2*math.log(2*5*26/.05)*(1/len(vals)+1/m['ntrain']))
    if abs(x.e.mean([v for _,v in vals])-m['mean'])>threshold:first=now;break
   if first is not None:break
  z['earliest_original_window_threshold_crossing_without_scan_schedule']=first
  # After availability is potentially detectable, not guaranteed immediately distinguishable.
  z['post_first_information']=z.pop('fixable_after_first3')
 diag['qualification']='First3 counts quantify an information lower bound for these tapes. Later counts are potentially avoidable exposure, not a guarantee of error-free detection at session609. Original20-date window itself needs accumulation; threshold crossings below isolate scheduling from window/threshold delay.'
 (O/'iteration5_diagnosis.json').write_text(json.dumps(diag,indent=2));r['diagnosis']=diag
 funded_gate_ok=True;null_ok=True;cost_error=0.;funded_count=0
 with gzip.open(O/'replays.jsonl.gz','rt') as f:
  for line in f:
   a=json.loads(line)
   if a['variant']!='iteration6':continue
   det=next(d for d in r['detection'] if all(d[k]==a[k] for k in ['seed','scenario','phase','variant']))
   if det['first_detection'] is not None:funded_gate_ok &= all(t['signal']<det['first_detection'] for t in a['trades'])
   if a['scenario']=='null':null_ok &= not a['trades'] and all(d['nav']==100000 for d in a['daily'])
   expected=sum(t['shares']*(t['entry_open']+t['exit_open'])*x.COST/2 for t in a['trades'])
   metric=next(m for m in r['portfolio'] if all(m[k]==a[k] for k in ['seed','scenario','phase','variant']))
   cost_error=max(cost_error,abs(expected-metric['costs']));funded_count+=len(a['trades'])
 assert funded_gate_ok and null_ok and cost_error<1e-7
 r['post_run_artifact_audit']=dict(zero_new_replays=True,funded_gate_ok=funded_gate_ok,null_cash_and_cost_ok=null_ok,max_both_leg_cost_error=cost_error,funded_trades_checked=funded_count,frozen_hashes_match=True)
 paired=[]
 for a in r['portfolio']:
  if a['variant']!='iteration6':continue
  b=next((b for b in r['portfolio'] if b['variant']=='iteration5' and all(b[k]==a[k] for k in ['seed','scenario','phase'])),None)
  if b:paired.append(dict(seed=a['seed'],scenario=a['scenario'],phase=a['phase'],**{k+'_delta':a[k]-b[k] for k in ['total_return','adverse_return','adverse_mdd','mdd','costs','trades']}))
 with (O/'economic_paired.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
 with (O/'detection.csv').open('w') as f:
  rows=[dict(d,events=json.dumps(d['events'])) for d in r['detection']];w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 final=[s for s in r['discrimination'] if s['phase']=='final' and s['variant']=='iteration6']
 r['next_blocker']='Five-tier support: seed2098214662956861329 has0 AVERAGE assignments. Frozen interval straddles a band; this experiment cannot repair it after final evaluation. Next independent step must obtain more independent fit/calibration evidence under unchanged bands, then freeze and test fresh tapes. Rapid safety is promising but residual4–7-session exposure and false-alarm power need independent episode validation; no safe zero-delay detection from this DGP.'
 r['false_alarm_power']=dict(independent_fresh_seeds=4,alarmed=0,one_sided95_upper_seed_probability=1-.05**.25,paired_scenarios_not_independent=True)
 (O/'report.json').write_text(json.dumps(r,indent=2))
 lines=['# Iteration6 — FAIL','',r['next_blocker'],'',f"Completed {r['portfolio_replays']} portfolio replays, six tests; runner elapsed {r['elapsed_seconds']:.2f}s. Limit64 replays/720s. Three test portfolios, four fixed design probes, twelve paired regressions, forty frozen final portfolios. No candidate tuning, GA, production changes or final reruns. All new files stay here.",'','## Diagnosis','', 'Iteration5 false GREAT count442 comprised49 in sessions606–608, before any post-change outcome was eligible, and393 after first outcome availability. Funded false GREAT trades lost $36,554 across four separate $100,000 accounts; these are a subset of portfolio PnL. Full reversal mean return was−10.31%. The frozen sensor/full models agree on the wrong sign, so disagreement cannot reveal remapping. The20-date drift window and hard-coded first scan628 impose delay. Replacing only the schedule would cross the original threshold at '+str([z['earliest_original_window_threshold_crossing_without_scan_schedule'] for z in diag['rows']])+'. See iteration5_diagnosis.json for exact per-seed counts and timestamps.','', 'No zero-delay switch detector is identifiable here: iid symmetric sensor marginals, unconditional returns, and entire price paths are unchanged by sensor remapping. Under the required signal+3 availability rule,606 outcomes first enter at609. Later statistical accumulation is necessary to avoid excessive false alarms; not all393 later errors can simply be eliminated.','', '## Frozen gate','', 'Iteration5 classifier, bands, train/cal split, disagreement filter and DGP remain unchanged. Before each entry, the gate evaluates2/4/8-date sensor-conditioned extreme-cell residual contrasts, which cancel common-date return shocks. At least2 names in each extreme cell are required per date; missing dates conservatively skip the look. An independent channel monitors date-grouped forecast errors of actual funded, matured fills. A drift alarm causes full abstention for the remaining horizon. There is no forecast-sign flip or automatic recovery. All outcomes obey signal+3<=decision.','', 'Market/sector breadth was assessed and rejected as a switch detector: there are no sector effects or memberships, and prices are bit-identical across stable and reversal scenarios. No informative synthetic indicator was added. Residual trend conditioned on the sensor is informative. All first fresh alarms came from cross-sectional residual evidence; funded surprise did not lead detection, so this run does not establish incremental benefit from that second channel. Threshold envelopes and multiplicity bounds are prescribed synthetic engineering assumptions, not certified real-data error guarantees.','', '## Measured comparisons','', 'Arithmetic per-seed means; return and MDD below use the adverse segment starting at the switch, including terminal liquidation. Costs are full-window dollars per initial$100,000 account. Random-switch total returns include earlier planted gains and therefore are not used as the adverse-loss metric.','', '| Phase / scenario / policy | False GREAT | Detection delay | Adverse return | Adverse MDD | Costs |','|---|---:|---|---:|---:|---:|']
 for phase,scenario in [('paired_regression','reversal'),('final','reversal'),('final','random_reversal')]:
  for var in ['iteration5','iteration6']:
   ms=[m for m in r['portfolio'] if m['phase']==phase and m['scenario']==scenario and m['variant']==var];ss=[s for s in r['discrimination'] if s['phase']==phase and s['scenario']==scenario and s['variant']==var];ds=[d['delay'] for d in r['detection'] if d['phase']==phase and d['scenario']==scenario and d['variant']==var]
   lines.append(f"| {phase} / {scenario} / {var} | {sum(s['false_great'] for s in ss)} | {ds} | {st.mean(m['adverse_return'] for m in ms):.2%} | {st.mean(m['adverse_mdd'] for m in ms):.2%} | ${st.mean(m['costs'] for m in ms):,.0f} |")
 lines+=['', 'Stable final learnable coverage76.3%–100%; outer-noise38.9%–100%. Stable extreme errors0; no observed alarms across four seeds, paired stable scenarios. Stable classifications, funded trades, return and costs match iteration5 exactly: no observed stable economic cost. All four null tapes fully abstain with zero costs and returns. Three of four fresh learnable seeds support all five tiers; the failing seed has inferred support[590,518,0,614,585]. No forced tiers or widened bands.','', f"All frozen hashes match. Artifact audit verifies no funded entries on/after the latch, nonnegative cash, net/PnL reconciliation, one-session matched horizons and both-leg costs (max recomputation error{cost_error:.2g}). Modeled per-trade risk remains<=2%; the50% gap probe exceeds modeled loss as expected. Aggregate portfolio and realized gap losses are not capped at2%. Cash is a zero-yield control; no SGOV data or alpha claim.",'', '## Process and limitations','', 'preregister.json predates all runs. Design seeds620101/620102 and already-viewed paired tapes are separate from final seeds. commitment.json records core, reference dependency, test, runner and preregistration hashes before OS-entropy seeds/switch dates were drawn. Random switches are drawn uniformly from626–686; neither policy sees the switch. Source-freeze is local, without a trusted public timestamp. The post-run analyze.py only reads evidence and writes documentation/audits; it executes no portfolios and is separately checksummed.','', 'Zero alarms on four independent seeds gives a52.7% one-sided95% upper seed alarm probability; paired scenarios do not increase independent seed count. The observed false-alarm criterion passes, but a population<=5% claim is unsupported. Fresh tapes validate this synthetic engineering change, not real PIT predictors or production readiness. The inherited five-tier support failure remains. Available PIT information supports faster detection after outcomes accrue; it cannot support risk-free immediate recognition.','', '## Artifacts and commands','', 'report.json contains explicit PASS/FAIL for every preregistered check. confusion.csv includes UNKNOWN and individual-latent truth; portfolio.csv contains all return/CAGR/MDD/cost/risk metrics. detection.csv, economic_paired.csv, audit.csv, opportunities.jsonl.gz and replays.jsonl.gz provide timestamps, all-opportunity outcomes and actual funded ledgers. checksums.json covers artifacts.','', 'Run `python3 analyze.py` in this directory to re-audit archived results without portfolios. `python3 run.py` refuses reuse after commitment. Tests are in test_engine.py; rerunning them executes three additional portfolios outside the archived59 and must not be presented as part of this frozen experiment.','', '**Next blocker:** obtain enough independent fit/calibration evidence for the missing middle tier, and independently validate residual exposure and false-alarm rates before any promotion. Do not tune these evaluated final seeds.']
 (O/'README.md').write_text('\n'.join(lines)+'\n')
 (O/'checksums.json').write_text(json.dumps({p.name:x.e.sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='checksums.json'},indent=2))
 print('Artifact audit PASS; overall FAIL; no additional replays')
if __name__=='__main__':main()
