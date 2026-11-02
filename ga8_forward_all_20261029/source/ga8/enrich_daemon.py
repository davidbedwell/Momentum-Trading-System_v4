"""Restartable low-priority automatic enrichment of newly qualified chromosomes."""
import os,sys,time,json,sqlite3,traceback,fcntl
from pathlib import Path
from .enrich_trades import main

def run(path):
 path=Path(path);lock=(path.parent/'enrichment.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 while True:
  try:
   db=sqlite3.connect(path,timeout=60)
   qualifying=db.execute('''SELECT count(distinct e.id) FROM evaluations e WHERE e.phase=0 AND json_extract(e.metrics_json,'$.cagr')>=.15 AND json_extract(e.metrics_json,'$.max_drawdown')<.20 AND json_extract(e.metrics_json,'$.calmar')>=2.0''').fetchone()[0]
   enriched=db.execute('SELECT count(*) FROM replay_trade_evidence WHERE training_phase=0').fetchone()[0];db.close()
   if qualifying>enriched:
    print(json.dumps(dict(event='enrich_start',qualifying=qualifying,enriched=enriched)),flush=True)
    main(path)
   time.sleep(60)
  except Exception as exc:
   print(json.dumps(dict(event='error',message=str(exc),trace=traceback.format_exc())),flush=True)
   time.sleep(60)
if __name__=='__main__':run(sys.argv[1])
