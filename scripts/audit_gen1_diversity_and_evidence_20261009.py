"""Nonselecting, fail-closed genome diversity and support audit, DEV80 only."""
import json,hashlib,pathlib,collections,math
root=pathlib.Path('Research/Runs/gen1-merit-screen-20261008');out=root/'scientific_certification_20261009';out.mkdir(exist_ok=True)
parents=[json.loads(s) for s in open(root/'horizon_grouped_pareto_20261009/provisional_168_priority.jsonl')]
catalog={r['index']:r for r in (json.loads(s) for s in open(root/'all_candidates.jsonl'))}
curves={r['index']:r for r in (json.loads(s) for s in open(root/'phaseC_parent_study_20261009/results.jsonl'))}
def canonical(r):return json.dumps({'side':r['side'],'chromosomes':r['chromosomes']},sort_keys=True,separators=(',',':'))
groups=collections.defaultdict(list);behavior=collections.defaultdict(list);records=[]
for p in parents:
 i=p['index'];r=catalog[i];curve=curves[i]['points'];fingerprint=hashlib.sha256(canonical(r).encode()).hexdigest()
 groups[fingerprint].append(i)
 # Diagnostic only: same direction and exact 126-point sign/finite pattern.
 signature=(r['side'],tuple('+' if isinstance(x.get('ev_net'),(int,float)) and math.isfinite(x['ev_net']) and x['ev_net']>0 else '-' if isinstance(x.get('ev_net'),(int,float)) and math.isfinite(x['ev_net']) else '?' for x in curve))
 behavior[signature].append(i)
 records.append({'index':i,'side':r['side'],'families':r['families'],'genome_sha256':fingerprint,'valid_horizons':sum(isinstance(x.get('ev_net'),(int,float)) and math.isfinite(x['ev_net']) for x in curve)})
duplicates=[v for v in groups.values() if len(v)>1]
report={'status':'DESCRIPTIVE_DIVERSITY_EVIDENCE_NOT_CERTIFIED','genomes':len(records),'unique_canonical_genomes':len(groups),'exact_duplicate_groups':duplicates,'unique_coarse_horizon_signatures':len(behavior),'coarse_signature_collisions':[v for v in behavior.values() if len(v)>1],'family_combinations':dict(collections.Counter('+'.join(r['families']) for r in records)),'side_counts':dict(collections.Counter(r['side'] for r in records)),'behavioral_similarity_threshold_approved':False,'parent_selection_unchanged':True,'gen2_authorized':False}
(out/'diversity_diagnostic.json').write_text(json.dumps(report,indent=2));(out/'diversity_records.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in records));print(json.dumps({k:v if k!='coarse_signature_collisions' else len(v) for k,v in report.items()},indent=2))
