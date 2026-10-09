"""Verify all Gen1 genomes retain their original nine horizon benchmarks."""
import json,pathlib,collections
R=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
EXPECTED=(1,2,3,5,7,10,15,20,63)
rows=[json.loads(x) for x in (R/'all_candidates.jsonl').open()]
assert len(rows)==4360 and len({r['index'] for r in rows})==4360
for r in rows:
 horizons=tuple(int(p['horizon']) for p in r['horizons'])
 if horizons!=EXPECTED:raise ValueError(f"Incomplete original horizon grid for {r['index']}: {horizons}")
 if r['side'] not in ('LONG','SHORT'):raise ValueError('invalid direction')
assignments=[json.loads(x) for x in (R/'original_4360_train_horizon_20261009/assignments.jsonl').open()]
assert {a['genome_index'] for a in assignments}=={r['index'] for r in rows}
report={'status':'FULL_POPULATION_HORIZON_GRID_VERIFIED_NOT_PIT_CERTIFIED','genomes':len(rows),'original_horizons':EXPECTED,'original_horizon_evaluations':len(rows)*len(EXPECTED),'later_preferred_horizon_missing':sum(a['horizon'] is None for a in assignments),'excluded_due_to_later_assignment':0,'scope':'DEV80','protected_banks_accessed':False,'exit_cap_sessions':63,'qualification':'Presence of benchmark evaluations does not certify a viable signal or executable event.'}
out=R/'exit_ga_salvage_audit_20261009';out.mkdir(exist_ok=True)
(out/'population_contract.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
