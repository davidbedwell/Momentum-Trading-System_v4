"""Post-holdout artifact audit/supplement; no inference changes or replay calls."""
import json,hashlib,math,statistics as st,gzip
from pathlib import Path
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=json.loads((O/'commitment.json').read_text());assert all(sha(O/p)==h for p,h in c['sources'].items())
 r=json.loads((O/'report.json').read_text());rows=r['rows'];assert len(rows)==120==r['portfolio_replays']
 assert len({(v['seed'],v['stratum'],v['scenario'],v['arm']) for v in rows})==120
 archived=[json.loads(l) for l in (O/'per_seed.jsonl').read_text().splitlines()];assert archived==rows
 old=json.loads((O.parent/'discrimination_iteration6/seeds.json').read_text());new=json.loads((O/'seeds.json').read_text())
 assert not set(new['seeds'])&set(old['seeds'])
 assert sha(O/'frozen/iteration6_engine.py')==sha(O.parent/'discrimination_iteration6/engine.py')
 assert sha(O/'frozen/iteration5_reference.py')==sha(O.parent/'discrimination_iteration5/experiment.py')
 n=0
 with gzip.open(O/'replays.jsonl.gz','rt') as f:
  for line in f:
   v=json.loads(line);n+=1
   assert all(t.get('last_available',t['index']-3)<=t['index']-3 for t in v['trace'])
 assert n==120
 primary=[v for v in rows if v['stratum']=='primary'];pairs=[]
 for scenario in ('learnable','reversal','random_reversal','outer_noise','null'):
  a=[v for v in primary if v['scenario']==scenario and v['arm']=='A'];b=[next(b for b in primary if b['scenario']==scenario and b['arm']=='B' and b['seed']==v['seed']) for v in a]
  item=dict(scenario=scenario,direction='B minus A',n=6)
  for key in ('total_return','adverse_return','adverse_mdd','costs','false_great','coverage'):
   vals=[y[key]-x[key] for x,y in zip(a,b)];m=st.mean(vals);h=2.570581836*st.stdev(vals)/math.sqrt(6)
   item[key]=dict(mean=m,descriptive_t95=[m-h,m+h])
  pairs.append(item)
 stable=[v for v in rows if v['scenario'] in ('learnable','outer_noise','null')]
 alarms=[{k:v[k] for k in ('stratum','seed','scenario','arm','first_alarm','coverage')} for v in stable if v['first_alarm'] is not None]
 fail=[{k:v[k] for k in ('stratum','seed','scenario','arm','delay','adverse_return','adverse_mdd')} for v in rows if v['arm']=='B' and v['scenario'] in ('reversal','random_reversal') and (v['delay'] is None or not 3<=v['delay']<=8 or v['adverse_return']<-.05 or v['adverse_mdd']>.05)]
 supplement=dict(frozen_commitment_verified=True,archived_per_seed_matches=True,unique_portfolios=120,seed_overlap_iteration6=False,paired_B_minus_A=pairs,stable_alarm_details=alarms,B_failure_details=fail,zero_new_replays=True)
 r['post_run_audit']=supplement;(O/'report.json').write_text(json.dumps(r,indent=2))
 s=(O/'summary.md').read_text();s+='\nPost-run artifact audit verified all frozen commitment hashes,120 unique archived portfolios, seed separation from iteration6, and per-seed ledger equality. No new portfolios. Exact stable alarms and B episode failures are in report.json post_run_audit.\n\nDirect primary comparison B minus A (descriptive paired95% t intervals):\n'
 for p in pairs:
  if p['scenario'] in ('reversal','random_reversal'):
   v=p['adverse_return'];s+=f"- {p['scenario']} adverse return: {v['mean']:.2%}, interval [{v['descriptive_t95'][0]:.2%}, {v['descriptive_t95'][1]:.2%}].\n"
 s+='\nAVERAGE was supported on all6 primary seeds under every policy; the primary five-tier failures were missing POOR on one seed and GOOD on another. The literal radius patch did not change primary learnable support. Both extended seeds had five-tier support under every policy, so this small secondary sample does not establish a unique benefit from Claude\'s radius fix or guarantee support on future seeds.\n'
 (O/'summary.md').write_text(s)
 (O/'checksums.json').write_text(json.dumps({str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and '__pycache__' not in str(p) and p.name!='checksums.json'},indent=2))
 print(json.dumps(supplement,indent=2))
if __name__=='__main__':main()
