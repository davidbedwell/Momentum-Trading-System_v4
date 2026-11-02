"""Frozen reporting only; no candidate fitting or selection."""
import json,math,statistics as st,hashlib,itertools
from pathlib import Path
O=Path(__file__).resolve().parent
SC=['learnable','reversal','random_reversal','outer_noise','null'];AR=['6','7B','8B-D','8B-Cal']
def dump(n,x):(O/n).write_text(json.dumps(x,indent=2))
def main():
 r=json.loads((O/'results.json').read_text());rows=r['rows'];n=24;summary={};pairs=[]
 lookup={(x['arm'],x['seed'],x['scenario']):x for x in rows}
 for arm in AR:
  ss={}
  for sc in SC:
   rr=[x for x in rows if x['arm']==arm and x['scenario']==sc]
   ss[sc]=dict(n=len(rr),false_alarms=sum(x['false_alarm'] for x in rr),three_session=sum(x['delay']==3 and not x['prechange_alarm'] for x in rr),misses=sum(x['delay'] is None for x in rr),mean_return=st.mean(x['total_return'] for x in rr),mean_adverse_mdd=st.mean(x['adverse_mdd'] for x in rr),max_adverse_mdd=max(x['adverse_mdd'] for x in rr),mean_false_great=st.mean(x['false_great'] for x in rr),mean_false_great_first3=st.mean(x['false_great_first3'] for x in rr),mean_false_great_post3=st.mean(x['false_great_post3'] for x in rr))
  summary[arm]=ss
 for a,b in itertools.combinations(AR,2):
  for sc in SC:
   aa=[x for x in rows if x['arm']==a and x['scenario']==sc];stats={}
   for key in ('total_return','adverse_mdd','false_great','false_great_post3'):
    ds=[x[key]-lookup[b,x['seed'],sc][key] for x in aa];mu=st.mean(ds);margin=2.06865761*st.stdev(ds)/math.sqrt(n)
    stats[key]=dict(mean_a_minus_b=mu,descriptive_t95=[mu-margin,mu+margin],per_seed=ds)
   pairs.append(dict(a=a,b=b,scenario=sc,stats=stats))
 cand=summary['8B-Cal'];checks=dict(stable_zero_alarms=all(cand[s]['false_alarms']==0 for s in ('learnable','outer_noise','null')),reversal_three_session=all(cand[s]['three_session']>=18 and cand[s]['false_alarms']==0 for s in ('reversal','random_reversal')),adverse_mdd=all(cand[s]['max_adverse_mdd']<=.05 for s in ('reversal','random_reversal')),outer_noise_return=cand['outer_noise']['mean_return']-summary['8B-D']['outer_noise']['mean_return']>=-.05,false_great=all(cand[s]['mean_false_great_post3']<=summary['8B-D'][s]['mean_false_great_post3'] for s in ('reversal','random_reversal')))
 audits=r['audits'];verification=dict(complete=len(rows)==480,cash=all(x['min_cash']>=-1e-8 for x in audits),pnl=all(x['pnl_error']<1e-6 for x in audits),cost=all(x['cost_error']<1e-6 for x in audits),net=all(x['net_error']<1e-12 for x in audits),horizon=all(x['horizon'] for x in audits),no_funding_after_alarm=all(x['no_funded_after_alarm'] for x in audits))
 c=json.loads((O/'commitment.json').read_text());verification['source_hashes']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in c['sources'].items())
 lock=json.loads((O/'threshold_lock.json').read_text());verification['threshold_lock']=hashlib.sha256((O/'calibration.json').read_bytes()).hexdigest()==lock['calibration_sha256']
 events=[{k:x[k] for k in ('seed','scenario','arm','change','first_alarm','delay','prechange_alarm','false_alarm','events')} for x in rows];dump('event_ledger.json',events)
 delays=[x for x in events if x['scenario'] in ('reversal','random_reversal')];dump('per_seed_reversal_delays.json',delays)
 limitations=['24 independent holdout seeds; paired scenarios within seed are dependent. No multiplicity correction.','With zero alarms in 24 seeds, one-sided95 binomial upper is '+str(1-.05**(1/24))+'. Nonzero observed rates do not establish population control.','Calibration is empirical on 32 seeds, three stable scenarios; no anytime-valid or real-market guarantee.','Threshold maxima across scenarios may sacrifice reversal speed; calibration never used reversal tapes.','Paired t intervals are descriptive with n24 and possibly non-normal bounded outcomes. Misses and prealarms stay explicit; no complete-case mean-delay claim.','Seed exclusion scans accessible uncompressed repository evidence; compressed artifacts rely on companion seed manifests. No guarantee about inaccessible external experiments.','Local hashes/timestamps are auditable but lack trusted external timestamp. No prior results used to select thresholds.','Single fixed original400/200 history; no extended-history confirmation. Synthetic generator and criteria are inherited or prespecified; no deployment inference.']
 report=dict(status='PASS' if all(checks.values()) else 'FAIL',criteria=checks,verification=verification,summary=summary,paired=pairs,limitations=limitations,elapsed_seconds=r['elapsed_seconds'],replays=r['portfolio_replays']);dump('report.json',report)
 lines=['# 8B calibration validation', '',f"Candidate **{report['status']}**. Completed 480 paired portfolios on 24 untouched holdout seeds in {r['elapsed_seconds']:.1f}s. No further tuning.",'', 'Only the two CUSUM alarm thresholds change. Frozen corrected engine, drift constants, training mean baseline, date clock, classifier, execution and latch are shared verbatim. Original 8B-D retains its archived thresholds. All arms use original400/200 history.','', 'Threshold rule: each channel is max(0.018, 1.1 × maximum unlatched statistic over all dates of 32 calibration seeds × learnable/outer_noise/null). No reversal calibration. Exact seeds and rule were committed before calibration; threshold lock precedes holdout generation.','', 'Criteria: '+json.dumps(checks), 'Audit checks: '+json.dumps(verification),'', '| Arm | Learnable FA | Outer noise FA | Null FA | Reversal 3-session /24 | Random reversal 3-session /24 | Outer noise mean return | Reversal max adverse MDD | Random max adverse MDD |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 for arm in AR:
  q=summary[arm];lines.append(f"|{arm}|{q['learnable']['false_alarms']}|{q['outer_noise']['false_alarms']}|{q['null']['false_alarms']}|{q['reversal']['three_session']}|{q['random_reversal']['three_session']}|{q['outer_noise']['mean_return']:.2%}|{q['reversal']['max_adverse_mdd']:.2%}|{q['random_reversal']['max_adverse_mdd']:.2%}|")
 cal=json.loads((O/'calibration.json').read_text());lines+=['',f"Original thresholds: {cal['original_thresholds']}; calibrated thresholds: {cal['thresholds']}.",'', '| Seed | Scenario | 6 delay | 7B delay | 8B-D delay | 8B-Cal delay |','|---|---|---:|---:|---:|---:|']
 for seed in json.loads((O/'seeds.json').read_text())['holdout']:
  for sc in ('reversal','random_reversal'):
   vals=[]
   for arm in AR:
    x=lookup[arm,seed,sc];vals.append('PREALARM' if x['prechange_alarm'] else str(x['delay']) if x['delay'] is not None else 'MISS')
   lines.append('|'+str(seed)+'|'+sc+'|'+'|'.join(vals)+'|')
 lines+=['','False GREAT is latent AWFUL classified GREAT after executed gating; first3/post3 splits, all scenario means and every paired per-seed return/MDD/false-GREAT contrast are in report.json. Reversal false alarms are prechange alarms; nonreversal false alarms are any latch. Misses count in the 3-session denominator. No post-alarm entries are funded; existing positions finish normally.','', '## Confidence limitations','']+['- '+v for v in limitations]+['','## Audit artifacts','','preregister.json and seeds.json: exact rule, criteria, seeds and scan inventory. commitment.json: pre-calibration source hashes. threshold_lock.json: pre-holdout calibration hash. calibration.json: all calibration date traces and maxima. event_ledger.json and per_seed_reversal_delays.json: alarms, timing and censoring. per_seed.jsonl/results.json: every endpoint and execution audit. replays.jsonl.gz: all fills, NAV and detector traces. opportunities.jsonl.gz: every asset/date label and funding status. tests.log: unit tests. Reproduce only in a separate folder; run.py refuses existing commitment.']
 (O/'summary.md').write_text('\n'.join(lines)+'\n')
 dump('checksums.json',{str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in O.iterdir() if p.is_file() and p.name!='checksums.json'})
 assert all(verification.values()),verification
if __name__=='__main__':main()
