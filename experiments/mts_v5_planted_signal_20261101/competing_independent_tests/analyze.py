"""Artifact-only analysis; zero portfolio replays, no changes to design."""
import json,math,statistics as st,hashlib,csv
from pathlib import Path
O=Path(__file__).resolve().parent

def mean(a):return st.mean(a) if a else None
def bisect(f,target):
 lo=0.;hi=1.
 for _ in range(70):
  mid=(lo+hi)/2
  if f(mid)>target:lo=mid
  else:hi=mid
 return (lo+hi)/2
def binomcdf(k,n,p):return sum(math.comb(n,j)*p**j*(1-p)**(n-j) for j in range(k+1))
def cp(k,n):return [0 if k==0 else bisect(lambda p:binomcdf(k-1,n,p),.975),1 if k==n else bisect(lambda p:binomcdf(k,n,p),.025)]
def ci(v):
 n=len(v);a=mean(v);t={2:12.706204736,6:2.570581836}[n];return dict(n=n,mean=a,t95=[a-t*st.stdev(v)/math.sqrt(n),a+t*st.stdev(v)/math.sqrt(n)],interpretation='descriptive t interval; normal seed-delta approximation, small n')
def main():
 r=json.loads((O/'results.json').read_text());rows=r['rows'];groups=[];paired=[];checks={}
 for stratum in ('primary','extended_secondary'):
  for arm in ('iteration6','A','B'):
   rr=[v for v in rows if v['stratum']==stratum and v['arm']==arm];stable=[v for v in rr if v['scenario'] in ('learnable','outer_noise','null')];learn=[v for v in rr if v['scenario']=='learnable'];rev=[v for v in rr if v['scenario'] in ('reversal','random_reversal')]
   seeds=set(v['seed'] for v in rr);alarmed=sum(any(v['false_alarm'] for v in stable if v['seed']==s) for s in seeds)
   checks[stratum+'/'+arm]=dict(stable_coverage=all(v['coverage']>=.15 for v in stable if v['scenario']!='null'),stable_false_great_zero=all(v['false_great']==0 for v in stable),stable_no_alarm=alarmed==0,five_tier_support=all(min(v['support'])>=20 for v in learn),rapid_detection=all(v['delay'] is not None and 3<=v['delay']<=8 for v in rev),adverse_loss_limit=all(v['adverse_return']>=-.05 and v['adverse_mdd']<=.05 for v in rev),null_abstention=all(v['coverage']==0 for v in stable if v['scenario']=='null'))
   for scenario in ('learnable','reversal','random_reversal','outer_noise','null'):
    a=[v for v in rr if v['scenario']==scenario];power=sum(v['delay'] is not None and 3<=v['delay']<=8 for v in a)
    groups.append(dict(stratum=stratum,arm=arm,scenario=scenario,n=len(a),return_mean=mean([v['total_return'] for v in a]),adverse_return_mean=mean([v['adverse_return'] for v in a]),mdd_mean=mean([v['mdd'] for v in a]),adverse_mdd_mean=mean([v['adverse_mdd'] for v in a]),costs_mean=mean([v['costs'] for v in a]),coverage_mean=mean([v['coverage'] for v in a]),coverage_range=[min(v['coverage'] for v in a),max(v['coverage'] for v in a)],false_great=sum(v['false_great'] for v in a),false_great_first3=sum(v['false_great_first3'] for v in a),false_great_post3=sum(v['false_great_post3'] for v in a),delays=[v['delay'] for v in a],support=[v['support'] for v in a],alarms=sum(v['first_alarm'] is not None for v in a),rapid_power95=cp(power,len(a)) if scenario in ('reversal','random_reversal') else None,seed_family_false_alarms=alarmed,seed_family_false_alarm95=cp(alarmed,len(seeds)),seed_family_false_alarm_one_sided95_upper=bisect(lambda p:binomcdf(alarmed,len(seeds),p),.05) if alarmed<len(seeds) else 1))
   if arm!='iteration6':
    for scenario in ('learnable','reversal','random_reversal','outer_noise','null'):
     aa=[v for v in rr if v['scenario']==scenario];base=[next(b for b in rows if b['stratum']==stratum and b['seed']==v['seed'] and b['scenario']==scenario and b['arm']=='iteration6') for v in aa]
     paired.append(dict(stratum=stratum,arm=arm,scenario=scenario,**{k:ci([v[k]-b[k] for v,b in zip(aa,base)]) for k in ('total_return','adverse_return','adverse_mdd','costs','coverage','false_great')}))
    ds=[v['total_return']-next(b['total_return'] for b in rows if b['stratum']==stratum and b['seed']==v['seed'] and b['scenario']=='learnable' and b['arm']=='iteration6') for v in learn]
    checks[stratum+'/'+arm]['stable_noninferiority_point']=mean(ds)>-.05
    checks[stratum+'/'+arm]['stable_noninferiority_t95']=ci(ds)['t95'][0]>-.05
 audit=all(a['min_cash']>=-1e-8 and a['pnl_error']<1e-6 and a['net_error']<1e-12 and a['cost_error']<1e-7 and a['horizon'] and a['no_funded_after_alarm'] for a in r['audits'])
 report=dict(execution_status=r['execution_status'],portfolio_replays=r['portfolio_replays'],elapsed_seconds=r['elapsed_seconds'],cpu_limit=1,tests=r['tests'],checks=checks,accounting_audit=audit,frozen_hashes_match=r['frozen_hashes_match'],groups=groups,paired=paired,arms={a:('PASS' if all(v for k,d in checks.items() if k.endswith('/'+a) for v in d.values()) else 'FAIL') for a in ('iteration6','A','B')},validity={'A':'INVALID e-process claim; literal code faithfully tested, direction failure retained','B':'VALID per-tape <=.01 under proved synthetic assumptions including .002 baseline uncertainty, .008 mixture test; see VALIDITY.md','baseline':'Inherited fixed-horizon engineering envelope; no new anytime guarantee'},not_testable=json.loads((O/'preregister.json').read_text())['not_testable'],uncertainty='Primary6 independent seeds, secondary2; paired scenarios are not independent. No population<=5% or real-market claim. t intervals descriptive; no multiplicity-adjusted superiority/noninferiority claim.',rows=rows,audits=r['audits'])
 (O/'report.json').write_text(json.dumps(report,indent=2))
 lines=['# Competing independent tests','',f"Execution {report['execution_status']}: {report['portfolio_replays']} portfolios, {report['tests']} tests, {report['elapsed_seconds']:.2f}s, one CPU. Primary6 seeds and separate extended-history2 seeds; each has5 scenarios x3 policies. Arm outcomes: {report['arms']}. Accounting audit: {audit}.",'','Primary comparator is exact frozen iteration6. Extended comparator uses its unchanged code with common600/300 split and is not the frozen configuration. No pooling. Arm A uses the explicit runnable detector and prioritized radius patch; the inconsistent full review is not uniquely testable. See preregister.json and VALIDITY.md for every ambiguity and impossibility. No mathematical repair to A.','', '| Stratum | Scenario | Arm | Return | Adverse return | MDD | Adverse MDD | Costs | Coverage | False GREAT (first3/post3) | Delays |','|---|---|---|---:|---:|---:|---:|---:|---:|---|---|']
 for g in groups:lines.append(f"| {g['stratum']} | {g['scenario']} | {g['arm']} | {g['return_mean']:.2%} | {g['adverse_return_mean']:.2%} | {g['mdd_mean']:.2%} | {g['adverse_mdd_mean']:.2%} | ${g['costs_mean']:,.0f} | {g['coverage_mean']:.1%} | {g['false_great']} ({g['false_great_first3']}/{g['false_great_post3']}) | {g['delays']} |")
 lines+=['','False GREAT = individual latent TERRIBLE predicted GREAT, not conditional-mean classification error. Non-reversal first3/post3 fields are0 by definition; total includes all dates. Random reversal adverse return begins at switch; full return includes earlier planted gains. Missing delay is non-detection/prechange alarm and counts as rapid-detection failure. Costs include both legs; MDD includes liquidation. Confusions also use individual realized returns in per-seed results.','']
 for key,c in checks.items():lines.append(f"- {key}: "+', '.join(k+'='+str(v) for k,v in c.items()))
 lines+=['','Paired learnable return differences vs comparator (95% descriptive seed t intervals):']
 for p in paired:
  if p['scenario']=='learnable':
   v=p['total_return'];lines.append(f"- {p['stratum']} {p['arm']}: {v['mean']:.2%}, interval [{v['t95'][0]:.2%}, {v['t95'][1]:.2%}].")
 lines+=['','False-alarm uncertainty (event=any stable scenario alarm on a seed; paired stable scenarios not independent):']
 for g in groups:
  if g['scenario']=='learnable':lines.append(f"- {g['stratum']} {g['arm']}: {g['seed_family_false_alarms']}/{g['n']}, exact two-sided95 interval {g['seed_family_false_alarm95']}, one-sided95 upper {g['seed_family_false_alarm_one_sided95_upper']:.1%}.")
 lines+=['','Five-tier support vectors by seed (TERRIBLE, POOR, AVERAGE, GOOD, GREAT):']
 for g in groups:
  if g['scenario']=='learnable':lines.append(f"- {g['stratum']} {g['arm']}: {g['support']}.")
 lines+=['','Arm A has no valid anytime error guarantee: one Gaussian null factor has exact expectation1.39894228; overlapping length2 windows with a fixed lambda already give expected two-factor product1.64872127. Its nonnegative lambda cannot respond to negative contrast shifts. Empirical alarms do not repair those defects. Arm B has a conditional synthetic proof, including fitted baseline uncertainty and mixture multiplicity, but may spend more samples detecting shifts. All numerical power intervals, paired economic/coverage/error intervals and per-seed failures are in report.json. Neither arm is promoted based on point estimates.','', 'Bounded comparison does not meet the review\'s request for20 independent reversal episodes: there are6 primary seeds, with two paired episodes each, and2 separate extended seeds. Claims about<=5% population false alarms or all-seed tier support are unsupported. Individual tier radii remain heuristic; Arm A\'s selection branch has no certified coverage. No real PIT features, public timestamp, real alpha, GA, production edits, automatic recovery or guaranteed2% realized loss. The modeled per-trade limit is unchanged.','', 'Reproduce: `cd experiments/mts_v5_planted_signal_20261101/competing_independent_tests && python3 analyze.py` re-audits artifacts with zero portfolios. `python3 -m unittest discover -s . -v` runs six tests with zero portfolios. `run.py` refuses a second fresh-seed run. To replay archived seeds, copy this entire directory and parent reference dependencies to a separate workspace, replace entropy draws by seeds.json values in that copy, delete generated outputs there, and execute run.py; record it as a separate replay outside this120-portfolio experiment. Python standard library only. Frozen copies preserve source; original dependencies verified before and after. checksums.json covers all artifacts; commitment.json froze runner, analyzer, tests, review and prereg before seed draws.']
 (O/'summary.md').write_text('\n'.join(lines)+'\n')
 with (O/'metrics.csv').open('w') as f:
  a=[{k:v for k,v in row.items() if not isinstance(v,(list,dict))} for row in rows];w=csv.DictWriter(f,fieldnames=list(a[0]));w.writeheader();w.writerows(a)
 (O/'checksums.json').write_text(json.dumps({str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.rglob('*')) if p.is_file() and '__pycache__' not in str(p) and p.name!='checksums.json'},indent=2))
 print(json.dumps({k:report[k] for k in ('execution_status','portfolio_replays','elapsed_seconds','arms','accounting_audit')},indent=2))
if __name__=='__main__':main()
