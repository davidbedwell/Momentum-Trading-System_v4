"""DEV80-only Phase D evidence inventory; descriptive, not certification."""
import json, pathlib, math, statistics, hashlib, collections, time
root=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
out=root/'phaseD_diagnostic_20261009';out.mkdir(exist_ok=True)
assert json.load(open(root/'phaseC_parent_study_20261009/manifest.json'))['candidate_count']==168
rows=[json.loads(x) for x in open(root/'phaseC_parent_study_20261009/results.jsonl')]
assert len(rows)==168 and len({r['index'] for r in rows})==168
report=[]
for r in rows:
 pts=r['points'];valid=[p for p in pts if isinstance(p.get('ev_net'),(int,float)) and math.isfinite(p['ev_net'])]
 positives=[p for p in valid if p['ev_net']>0]
 best=max(valid,key=lambda p:p['ev_net']) if valid else None
 report.append({'index':r['index'],'side':r['side'],'window':r['allocation_window'],'valid_horizons':len(valid),'positive_horizons':len(positives),'positive_fraction':len(positives)/len(valid) if valid else None,'best_ev_horizon':best['horizon'] if best else None,'best_ev_net':best['ev_net'] if best else None,'best_effective_n':best['effective_n'] if best else None,'worst_finite_cvar5':min((p['cvar5'] for p in valid if isinstance(p.get('cvar5'),(int,float)) and math.isfinite(p['cvar5'])),default=None),'max_adverse_tail_magnitude':max((-p['mae_tail5'] for p in valid if isinstance(p.get('mae_tail5'),(int,float)) and math.isfinite(p['mae_tail5'])),default=None)})
with open(out/'diagnostics.jsonl','w') as f:
 for r in report:f.write(json.dumps(r)+'\n')
summary={'status':'DESCRIPTIVE_PHASE_D_EVIDENCE_ONLY_NOT_CERTIFIED','candidates':len(report),'with_positive_horizon':sum(r['positive_horizons']>0 for r in report),'with_no_valid_horizons':sum(r['valid_horizons']==0 for r in report),'sides':dict(collections.Counter(r['side'] for r in report)),'source_sha256':hashlib.sha256((root/'phaseC_parent_study_20261009/results.jsonl').read_bytes()).hexdigest(),'unresolved':['episode-level dependence','selection multiplicity','independent market era stability','execution lifecycle and portfolio MDD','genome and behavioral diversity','matched passive comparisons'],'scope':'DEV80 only','parent_selection_unchanged':True,'gen2_authorized':False}
(out/'manifest.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
