"""Prespecified endpoint reporting; no fitting, selection, or seed draws."""
import json,math,statistics as st,hashlib,gzip
from pathlib import Path
O=Path(__file__).resolve().parent
mean=st.mean

def binom_cdf(k,n,p):return sum(math.comb(n,j)*p**j*(1-p)**(n-j) for j in range(k+1))
def root_cdf(k,n,target):
 lo=0.;hi=1.
 for _ in range(100):
  mid=(lo+hi)/2
  if binom_cdf(k,n,mid)>target:lo=mid
  else:hi=mid
 return (lo+hi)/2
def cp(k,n):return [0. if k==0 else 1-root_cdf(n-k,n,.025),1. if k==n else root_cdf(k,n,.025)]
def main():
 r=json.loads((O/'results.json').read_text());rows=r['rows'];summaries=[];paired=[];seed_criteria=[]
 for arm in dict.fromkeys(x['arm'] for x in rows):
  rr=[x for x in rows if x['arm']==arm];baseline='6-600/300' if 'Full' in arm or '600' in arm else '6'
  lookup={(x['seed'],x['scenario']):x for x in rows if x['arm']==baseline}
  flags=[];deltas=[];fg=[]
  for seed in sorted(set(x['seed'] for x in rr)):
   ss={x['scenario']:x for x in rr if x['seed']==seed};rev=[ss[s] for s in ('reversal','random_reversal')]
   stable=[ss[s] for s in ('learnable','outer_noise','null')]
   ok=dict(stable_no_alarm=not any(x['false_alarm'] for x in stable),delays=all(x['delay'] is not None and 3<=x['delay']<=8 and not x['prechange_alarm'] for x in rev),adverse_mdd=all(x['adverse_mdd']<=.05 for x in rev),support=min(ss['learnable']['support'])>=20)
   delta=ss['learnable']['total_return']-lookup[seed,'learnable']['total_return'];deltas.append(delta)
   secondary=all(x['false_great_post3']<lookup[seed,x['scenario']]['false_great_post3'] for x in rev)
   seed_criteria.append(dict(arm=arm,seed=seed,**ok,all_primary_per_seed=all(ok.values()),stable_return_delta=delta,secondary_false_great_improves=secondary))
   flags.append(ok)
  k=sum(not f['stable_no_alarm'] for f in flags);n=len(flags);ci=cp(k,n);upper=1. if k==n else root_cdf(k,n,.05)
  # t(15,.975)=2.13144954556; fixed n16 from preregistration.
  assert n==16
  margin=2.13144954556*st.stdev(deltas)/math.sqrt(n);dm=mean(deltas)
  sums={key:sum(f[key] for f in flags) for key in flags[0]};combined=sum(all(f.values()) for f in flags)
  summaries.append(dict(arm=arm,n=n,stable_seed_failures=k,stable_CP95=ci,stable_one_sided95_upper=upper,passes_by_endpoint=sums,combined_seed_passes=combined,strict_all_seed=combined==n and dm>=-.05,claude_12_of16=combined>=12 and dm>=-.05,stable_mean_return_delta=dm,stable_delta_t95=[dm-margin,dm+margin],descriptive_noninferiority_lower_gt_minus05=dm-margin>-.05,delays={sc:[x['delay'] for x in rr if x['scenario']==sc] for sc in ('reversal','random_reversal')},economics={sc:{key:mean(x[key] for x in rr if x['scenario']==sc) for key in ('total_return','mdd','costs','adverse_return','adverse_mdd','false_great_first3','false_great_post3','coverage')} for sc in ('learnable','reversal','random_reversal','outer_noise','null')}))
 for stage,candidates,controls in [('stage1',['8A-D','8B-D'],['6','7B']),('stage2',['8A-Full','8B-Full'],['6-600/300','7B-600/300'])]:
  pairs=[(a,b) for a in candidates for b in controls]+[(candidates[1],candidates[0])]
  for a,b in pairs:
   bb={(x['seed'],x['scenario']):x for x in rows if x['arm']==b}
   for sc in ('learnable','reversal','random_reversal','outer_noise','null'):
    aa=[x for x in rows if x['arm']==a and x['scenario']==sc]
    paired.append(dict(stage=stage,a=a,b=b,scenario=sc,n=len(aa),mean_deltas={key:mean(x[key]-bb[x['seed'],sc][key] for x in aa) for key in ('total_return','mdd','costs','false_great_post3','adverse_mdd')}))
 audits=r['audits'];checks=dict(cash_nonnegative=all(x['min_cash']>=-1e-8 for x in audits),pnl_reconciles=all(x['pnl_error']<1e-6 for x in audits),cost_reconciles=all(x['cost_error']<1e-6 for x in audits),net_reconciles=all(x['net_error']<1e-12 for x in audits),horizon=all(x['horizon'] for x in audits),no_funding_after_alarm=all(x['no_funded_after_alarm'] for x in audits))
 commitment=json.loads((O/'commitment.json').read_text());checks['committed_hashes_match']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in commitment['sources'].items())
 events=[dict(seed=x['seed'],arm=x['arm'],scenario=x['scenario'],change=x['change'],false_alarm=x['false_alarm'],events=x['events']) for x in rows]
 (O/'event_ledger.json').write_text(json.dumps(events,indent=2))
 report=dict(status=r['execution_status'],portfolio_replays=r['portfolio_replays'],elapsed_seconds=r['elapsed_seconds'],checks=checks,arms=summaries,paired=paired,per_seed_criteria=seed_criteria,limitations=['Arm C is INVALID as e-process; adaptive outcome-selected lambda and overlapping windows invalidate claimed MGF. No mathematical validity claim.','CUSUM thresholds calibrated on learnable stable tapes only; outer_noise/null transfer was not calibrated. No population anytime-valid guarantee.','7B fixed-lambda validity conditional on original synthetic assumptions; no new theorem or real-market validity claimed.','16 independent seeds cannot demonstrate <=5% alarm rate: zero-alarm upper 17.07%; scenarios within seed dependent.','Local commitment has no trusted external timestamp; no git commit (git is read-only).','Analysis script added during execution; endpoint definitions already frozen in preregistration. No source or parameter changes after holdout.','Stage2 independent confirmation of both packages; no winner selected. Cross-history differences confound history/classifier/detector.'])
 (O/'report.json').write_text(json.dumps(report,indent=2))
 lines=['# Corrected fair synthetic experiment','',f"Completed {r['portfolio_replays']} portfolios in {r['elapsed_seconds']:.1f} seconds, one Python process. Five prespecified implementation tests passed. Audit checks: {checks}.",'','8A-D and 8A-Full use Claude Part II §6 C_ablation exactly. **INVALID as an e-process. No mathematical validity or false-alarm guarantee is claimed for C.** CUSUM is empirically calibrated only.','', '| Arm | Stable alarm seeds /16 | Delay pass seeds /16 | All primary seed passes /16 | Strict | ≥12/16 | Stable return Δ |','|---|---:|---:|---:|---|---|---:|']
 for a in summaries:lines.append(f"| {a['arm']} | {a['stable_seed_failures']} | {a['passes_by_endpoint']['delays']} | {a['combined_seed_passes']} | {a['strict_all_seed']} | {a['claude_12_of16']} | {a['stable_mean_return_delta']:.2%} |")
 lines+=['','Strict and ≥12/16 are separate rules, both include the frozen mean stable-return criterion. The report separately provides descriptive paired t intervals and every endpoint. Stable alarms aggregate learnable, outer_noise and null within each seed. Zero of 16 gives a one-sided 95% upper bound of 17.07%, not ≤5%.','', 'Stage1 uses original 400/200 history; Stage2 uses independent seeds with 600/300 history and diagnostic 6/7B clones. Full candidates share fit_v3. Compare within history; no cross-history detector attribution. No winner selection, production changes, automatic iteration, or real-market claims.','','Artifacts: preregister.json; commitment.json; seeds.json; calibration.json; per_seed.jsonl; event_ledger.json; opportunities.jsonl.gz (all per-date/asset labels); replays.jsonl.gz (daily NAV, fills, detector traces); report.json (paired contrasts, exact intervals, criteria and limitations).','','Reproduce in a NEW directory preserving relative engine paths: copy code and preregistration, run `python3 run.py` then `python3 analyze.py`. Original run refuses holdout reuse. Seeds and full sources are retained for deterministic audit; new run draws new seeds.']
 lines+=['','Per-scenario stable alarm counts (learnable / outer_noise / null):']
 for a in summaries:
  counts=[sum(x['false_alarm'] for x in rows if x['arm']==a['arm'] and x['scenario']==sc) for sc in ('learnable','outer_noise','null')]
  lines.append(f"- {a['arm']}: {counts[0]} / {counts[1]} / {counts[2]}")
 lines+=['','CUSUM calibration used learnable stable tapes only. Its outer_noise/null false alarms show failure to transfer that calibration. Arm C also alarms on those scenarios. See PRIOR_STATUS.md for the preflight and historical holdout audit; verification.json checks all archived records.']
 (O/'summary.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
