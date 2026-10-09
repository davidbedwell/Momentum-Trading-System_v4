"""Preflight original-horizon study contract against completed assignment rows; no promotion."""
import json,pathlib,collections
from Core.layered_ga.gen1_path_study_split import validate_assignment
R=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
P=R/'original_4360_train_horizon_20261009'
def run():
 progress=json.loads((P/'progress.json').read_text())
 rows=[json.loads(s) for s in (P/'assignments.jsonl').open()]
 assert len(rows)==progress['done']
 assert len({x['genome_index'] for x in rows})==len(rows)
 for x in rows:validate_assignment(x)
 status=collections.Counter(x['status'] for x in rows)
 horizons=collections.Counter(str(x['horizon']) for x in rows)
 report={'status':'ASSIGNMENT_CONTRACT_PREFLIGHT_PASS_NOT_CERTIFICATION',
 'checked':len(rows),'requested':progress['total'],'horizons':dict(horizons),
 'statuses':dict(status),'all_original_horizons_only':True,
 'full_population_ready':len(rows)==4360,'protected_banks_touched':False}
 print(json.dumps(report,indent=2))
if __name__=='__main__':run()
