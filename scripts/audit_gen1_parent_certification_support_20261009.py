#!/usr/bin/env python3
"""Non-selecting audit of frozen 168 provisional parents; no thresholds promoted."""
import collections,hashlib,json,pathlib,statistics
root=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
manifest=root/'horizon_grouped_pareto_20261009/provisional_168_priority.jsonl'
rows=[json.loads(x) for x in manifest.open()]
assert len(rows)==168 and len({x['index'] for x in rows})==168
assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='5d1195e23b51f07c03c81629ceebb145ffbb0b3113c6d8d46d15050a310621b3'
report={'status':'DESCRIPTIVE_ONLY_NOT_CERTIFIED','parent_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'parent_count':len(rows),'side_counts':dict(collections.Counter(x['side'] for x in rows)),'effective_n':{'minimum':min(x['effective_n'] for x in rows),'median':statistics.median(x['effective_n'] for x in rows),'below_30':sum(x['effective_n']<30 for x in rows),'below_50':sum(x['effective_n']<50 for x in rows)},'provisional_lcb95':{'nonpositive_count':sum(x['lcb95']<=0 for x in rows),'positive_count':sum(x['lcb95']>0 for x in rows)},'per_window':{},'lowest_effective_n_indices':[x['index'] for x in sorted(rows,key=lambda x:x['effective_n'])[:10]],'interpretation':'Provisional confidence intervals are not certified multiplicity-adjusted or episode-independent. Counts are descriptive; no parent excluded or selected. No protected banks loaded.'}
for w in sorted({x['allocation_window'] for x in rows}):
 group=[x for x in rows if x['allocation_window']==w]
 report['per_window'][w]={'count':len(group),'effective_n_median':statistics.median(x['effective_n'] for x in group),'nonpositive_lcb95':sum(x['lcb95']<=0 for x in group)}
out=root/'scientific_certification_20261009/parent_support_audit.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
