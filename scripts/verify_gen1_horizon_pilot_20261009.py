"""Independent fail-closed pilot output verification, DEV80 only."""
import json,pathlib,sys
import numpy as np,pandas as pd
from Core.layered_ga.gen1_path_study_split import validate_assignment
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
def verify():
 a={r['genome_index']:r for r in map(json.loads,(ROOT/'original_4360_train_horizon_20261009/assignments.jsonl').open())}
 o=ROOT/'matched_horizon_v4_20261009'
 m=json.loads((o/'manifest.json').read_text())
 results=[json.loads(s) for s in (o/'results.jsonl').open()]
 p=pd.read_parquet(o/'heldout_event_predictions.parquet')
 errors=[]
 def check(ok,msg):
  if not ok:errors.append(msg)
 check(m.get('scope')=='DEV80' and m.get('protected_banks_touched') is False,'scope')
 check(m.get('genomes_processed')==12,'pilot population')
 check(len(a)==4360,'complete horizon assignments')
 check(len(results)==sum(max(1,len(validate_assignment(a[i]))) for i in range(12)),'checkpoint result coverage')
 check(len(p)==m.get('predictions'),'prediction count')
 check(sum(r['status']=='HELDOUT_DIAGNOSTIC_UNCERTIFIED' for r in results)==m.get('diagnostics'),'diagnostic count')
 expected={(r['genome_index'],r['checkpoint']):r for r in results if r['status']=='HELDOUT_DIAGNOSTIC_UNCERTIFIED'}
 check(len(expected)==m.get('diagnostics'),'duplicate diagnostics')
 if len(p):
  check(p[['genome_index','checkpoint','event_id']].duplicated().sum()==0,'duplicate prediction keys')
  check(p['genome_index'].between(0,11).all(),'genome scope')
  check(p['failure_probability'].between(0,1).all() and p['baseline_probability'].between(0,1).all(),'probability range')
  check(np.isfinite(p[['failure_probability','baseline_probability','terminal_net','checkpoint_net','mean_neighbor_distance']].to_numpy(dtype=float)).all(),'nonfinite values')
  check(p['failure_outcome'].isin([0,1]).all(),'binary outcome')
  check(((p['terminal_net']<=0).astype(int)==p['failure_outcome']).all(),'terminal label mismatch')
  check((p['checkpoint_net']<0).all(),'not distressed')
  check((pd.to_datetime(p['decision_date'])>=pd.Timestamp('2021-01-01')).all(),'heldout start')
  check((pd.to_datetime(p['decision_date'])<pd.Timestamp('2026-09-14')).all(),'heldout end/purge')
  counts=p.groupby(['genome_index','checkpoint']).size().to_dict()
  for key,n in counts.items():
   check(key in expected,'unreported prediction key')
   if key in expected:check(n==expected[key]['test_n'],'heldout count '+str(key))
  for row in p[['genome_index','checkpoint','horizon','side']].drop_duplicates().itertuples(index=False):
   item=a[row.genome_index]
   check(row.checkpoint in validate_assignment(item) and row.horizon==item['horizon'] and row.side==item['side'],'assignment mismatch')
 report={'status':'PILOT_OUTPUT_CONTRACT_PASS_NOT_SCIENTIFIC_CERTIFICATION' if not errors else 'PILOT_OUTPUT_CONTRACT_FAIL',
 'errors':errors,'genomes':m['genomes_processed'],'diagnostics':len(expected),'predictions':len(p),
 'limits':['No independent feature-release lineage proof','No true episode-independence proof','No portfolio simulation or multiplicity certification']}
 (o/'verification.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
 if errors:sys.exit(1)
if __name__=='__main__':verify()
