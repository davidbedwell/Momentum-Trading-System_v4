"""Six-worker restartable DEV80 conveyor with fail-closed per-batch checks."""
import argparse,concurrent.futures,json,os,pathlib,subprocess,sys,time
import pandas as pd
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008/matched_horizon_v4_full_20261009')
ASSIGN=pathlib.Path('Research/Runs/gen1-merit-screen-20261008/original_4360_train_horizon_20261009/assignments.jsonl')
def job(args):
 offset,size,ids=args
 folder=ROOT/f'batch_{offset:04d}_{offset+size:04d}'
 marker=folder/'verified.json'
 if marker.exists():
  m=json.loads(marker.read_text())
  if m.get('status')=='PASS' and m.get('start_index')==offset and m.get('batch_size')==size:
   return offset,size,int(m.get('predictions',0)),'REUSED'
 # Never trust incomplete output from a terminated worker.
 if not marker.exists():
  env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
  subprocess.run([sys.executable,'scripts/run_gen1_horizon_matched_full_20261009.py',
                  '--start-index',str(offset),'--limit',str(size)],check=True,env=env,
                 stdout=(folder.parent/f'batch_{offset:04d}.log').open('w'),
                 stderr=subprocess.STDOUT)
 manifest=json.loads((folder/'manifest.json').read_text())
 results=[json.loads(s) for s in (folder/'results.jsonl').open()]
 pred=pd.read_parquet(folder/'heldout_event_predictions.parquet')
 if manifest.get('scope')!='DEV80' or manifest.get('protected_banks_touched') is not False:
  raise RuntimeError(f'Scope breach batch {offset}')
 if manifest['genomes_processed']!=size or len(pred)!=manifest['predictions'] or {r['genome_index'] for r in results}!=set(ids):
  raise RuntimeError(f'Output reconciliation batch {offset}')
 if len(pred) and (pred[['genome_index','checkpoint','event_id']].duplicated().any() or not pred.genome_index.isin(ids).all()):
  raise RuntimeError(f'Prediction keys batch {offset}')
 marker.write_text(json.dumps({'status':'PASS','start_index':offset,'batch_size':size,'predictions':len(pred)}))
 return offset,size,len(pred),'VERIFIED'
def main(workers,batch):
 if workers!=6:raise ValueError('This run is frozen to six workers')
 rows=[json.loads(x) for x in ASSIGN.open()]
 if len(rows)!=4360:raise RuntimeError('Missing assignments')
 ROOT.mkdir(parents=True,exist_ok=True)
 tasks=[(i,min(batch,4360-i),[r['genome_index'] for r in rows[i:i+batch]]) for i in range(0,4360,batch)]
 start=time.time();completed=set()
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  future={pool.submit(job,t):t for t in tasks}
  for f in concurrent.futures.as_completed(future):
   try:i,n,count,status=f.result()
   except Exception as e:
    for other in future:other.cancel()
    (ROOT/'parallel_failure.json').write_text(json.dumps({'failed_batch':future[f][0],'error':repr(e)}))
    raise
   completed.update(range(i,i+n))
   record={'verified_genomes':len(completed),'total':4360,'elapsed_seconds':round(time.time()-start,1),'workers':workers,'latest_batch':i,'latest_status':status}
   (ROOT/'parallel_progress.json').write_text(json.dumps(record))
   print(json.dumps(record),flush=True)
 print('SIX_WORKER_CONVEYOR_OUTPUT_VERIFIED',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=6);p.add_argument('--batch',type=int,default=12)
 a=p.parse_args();main(a.workers,a.batch)
