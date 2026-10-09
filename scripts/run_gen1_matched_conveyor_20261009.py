"""Restartable, fail-closed full DEV80 Gen1 matched-path conveyor."""
import argparse,json,pathlib,subprocess,sys,time
import pandas as pd
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008/matched_horizon_v4_full_20261009')
def main(batch):
 ROOT.mkdir(parents=True,exist_ok=True)
 assignments=pathlib.Path('Research/Runs/gen1-merit-screen-20261008/original_4360_train_horizon_20261009/assignments.jsonl')
 if sum(1 for _ in assignments.open())!=4360:raise RuntimeError('Incomplete frozen assignments')
 start=time.time()
 for offset in range(0,4360,batch):
  size=min(batch,4360-offset)
  directory=ROOT/f'batch_{offset:04d}_{offset+size:04d}'
  marker=directory/'verified.json'
  if marker.exists():
   m=json.loads(marker.read_text())
   if m.get('status')=='PASS' and m.get('start_index')==offset and m.get('batch_size')==size:continue
  command=[sys.executable,'scripts/run_gen1_horizon_matched_full_20261009.py','--start-index',str(offset),'--limit',str(size)]
  subprocess.run(command,check=True)
  manifest=json.loads((directory/'manifest.json').read_text())
  results=[json.loads(s) for s in (directory/'results.jsonl').open()]
  predictions=pd.read_parquet(directory/'heldout_event_predictions.parquet')
  if manifest['genomes_processed']!=size or len(predictions)!=manifest['predictions'] or len({r['genome_index'] for r in results})!=size:
   raise RuntimeError('Batch output reconciliation failed '+str(offset))
  if len(predictions):
   assignment_rows=[json.loads(x) for x in assignments.open()]
   expected_indices={r['genome_index'] for r in assignment_rows[offset:offset+size]}
   if predictions[['genome_index','checkpoint','event_id']].duplicated().any() or not predictions['genome_index'].isin(expected_indices).all():
    raise RuntimeError('Duplicate or out-of-batch predictions')
  marker.write_text(json.dumps({'status':'PASS','start_index':offset,'batch_size':size,'predictions':len(predictions)}))
  (ROOT/'progress.json').write_text(json.dumps({'done':offset+size,'total':4360,'elapsed_seconds':round(time.time()-start,1)}))
  print('VERIFIED',offset+size,'of 4360',flush=True)
 print('FULL_CONVEYOR_COMPLETE_OUTPUT_CONTRACT_ONLY',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--batch',type=int,default=12)
 a=p.parse_args()
 if not 1<=a.batch<=100:raise ValueError('Batch outside 1..100')
 main(a.batch)
