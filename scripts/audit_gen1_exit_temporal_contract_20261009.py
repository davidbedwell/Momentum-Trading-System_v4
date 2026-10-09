"""Fail-closed preflight for DEV80 path integration; no protected banks accessed."""
import json,pathlib,collections,datetime
R=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
A=R/'original_4360_train_horizon_20261009/assignments.jsonl'
rows=[json.loads(line) for line in A.open()]
ids=[x['genome_index'] for x in rows]
if len(ids)!=len(set(ids)) or len(rows)!=4360:raise ValueError('invalid assignment identities')
allowed={1,2,3,5,7,10,15,20,63}
counts=collections.Counter();issues=[]
for r in rows:
 h=r['horizon'];counts[str(h)]+=1
 if h is not None and h not in allowed:issues.append(['horizon',r['genome_index'],h])
 if h is None and r['status']!='INSUFFICIENT_TRAIN_SUPPORT':issues.append(['unsupported',r['genome_index']])
 if h==1 and r['checkpoints']:issues.append(['h1_checkpoint',r['genome_index']])
# Key temporal invariant: at decision on T+t close, the fill must occur at T+1+t open;
# endpoint_return[:,t-1] is only valid for that fill if original array's provenance verifies this convention.
report={'status':'BLOCKED_PENDING_EXECUTION_ARRAY_PROVENANCE','scope':'DEV80','assignments':len(rows),'horizon_counts':dict(counts),'issues':issues[:20], 'protected_banks_accessed':False,
 'critical_requirements':['Prove endpoint_return column t-1 is executable T+1+t open relative to entry open T+1','Prove PIT context effective_date T+t is available before T+1+t open','Prove price and cost conventions for dynamic earlier exits and short borrow','Prove no post-horizon path used for feature construction','Reconcile entry signals and all eligible events before GA fitness']}
if issues:report['status']='FAILED_ASSIGNMENT_CONTRACT'
out=R/'exit_ga_salvage_audit_20261009';out.mkdir(exist_ok=True)
(out/'temporal_preflight.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
