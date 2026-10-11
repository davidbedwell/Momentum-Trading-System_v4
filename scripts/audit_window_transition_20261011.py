#!/usr/bin/env python3
"""Read-only checkpoint/journal integrity audit, safe while GA is running."""
import json,pathlib,collections,datetime
base=pathlib.Path('/home/ubuntu/Momentum-Trading-System_v4/Research/Runs/thirteen-window-normal-20261011')
windows=[(2,5),(6,10),(11,15),(16,20),(21,25),(26,30),(31,35),(36,40),(41,45),(46,50),(51,55),(56,60),(61,65)]
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'windows':[]}
for lo,hi in windows:
 d=base if lo==2 else base/f'window_{lo:02d}_{hi:02d}'
 item={'window':[lo,hi],'path':str(d),'issues':[]}
 cp=d/'state.json'
 if not cp.exists():item['status']='NOT_STARTED';report['windows'].append(item);continue
 try:
  state=json.loads(cp.read_text());g=state['generation'];item.update(status='COMPLETED' if state.get('completed') else 'ACTIVE_OR_PAUSED',generation=g,stop_reason=state.get('stop_reason'))
  config=state.get('config',{});item['config_window']=config.get('window');item['config_horizons']=config.get('horizons')
  if config.get('window')!=[lo,hi]:item['issues'].append('CONFIG_WINDOW_MISMATCH')
  counts={};candidates=set();evaluated=set();last=-1
  for filename,kind in [('candidates.jsonl','c'),('evaluations.jsonl','e')]:
   file=d/filename
   if not file.exists():item['issues'].append('MISSING_'+filename);continue
   with file.open() as f:
    for lineno,line in enumerate(f,1):
     try:r=json.loads(line)
     except json.JSONDecodeError:
      item['issues'].append(f'PARTIAL_JSON_{filename}_{lineno}');break
     key=r.get('genome_hash')
     if kind=='c':
      if key in candidates:item['issues'].append('DUPLICATE_CANDIDATE')
      candidates.add(key);counts[r.get('generation')]=counts.get(r.get('generation'),0)+1
     else:
      if key in evaluated:item['issues'].append('DUPLICATE_EVALUATION')
      evaluated.add(key)
  if evaluated-candidates:item['issues'].append('ORPHAN_EVALUATIONS')
  if counts:
   mx=max(counts)
   if sorted(counts)!=list(range(mx+1)):item['issues'].append('NONCONTIGUOUS_GENERATIONS')
   for gen,n in counts.items():
    expected=(config.get('initial_population_count') if gen==0 else config.get('batch'))
    if expected is not None and n!=expected:item['issues'].append(f'PARTIAL_GENERATION_{gen}')
   if mx>g+1:item['issues'].append('JOURNAL_AHEAD_CHECKPOINT')
   if mx==g+1 and not (d/'pending.json').exists():item['issues'].append('MISSING_PENDING')
   if mx<g:item['issues'].append('CHECKPOINT_AHEAD')
  item.update(candidates=len(candidates),evaluations=len(evaluated),unevaluated=len(candidates-evaluated),highest_candidate_generation=max(counts) if counts else None,pending=(d/'pending.json').exists())
  if state.get('completed') and candidates-evaluated:item['issues'].append('COMPLETED_WITH_UNEVALUATED')
 except Exception as e:item['issues'].append(type(e).__name__+':'+str(e)[:200])
 report['windows'].append(item)
print(json.dumps(report,indent=2))
(base/'transition_checkpoint_audit.json').write_text(json.dumps(report,indent=2)+'\n')
