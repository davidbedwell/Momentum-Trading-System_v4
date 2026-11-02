"""Non-destructive, restartable extraction of existing per-chromosome evidence."""
import sqlite3,json,sys,time
from pathlib import Path

def run(path):
 db=sqlite3.connect(path,timeout=60);db.execute('PRAGMA busy_timeout=60000')
 db.execute('CREATE TABLE IF NOT EXISTS extracted_evidence (id TEXT PRIMARY KEY, best_discovery_metrics_json TEXT, evaluations INTEGER NOT NULL, qualifying INTEGER NOT NULL, closed_trades_reported INTEGER, fill_count INTEGER, avg_exposure REAL, origin_regime_status TEXT NOT NULL, trade_success_status TEXT NOT NULL, transfer_status TEXT NOT NULL)')
 ids=db.execute('SELECT id FROM chromosomes').fetchall();done=0;start=time.monotonic()
 for (cid,) in ids:
  ev=db.execute('SELECT metrics_json FROM evaluations WHERE id=?',(cid,)).fetchall()
  if not ev:continue
  m=[json.loads(x[0]) for x in ev]
  best=max(m,key=lambda x:(x.get('feasible',False),x.get('cagr',-1),-x.get('max_drawdown',1)))
  qualifying=int(any(x.get('cagr',0)>=.15 and x.get('max_drawdown',1)<.2 and x.get('calmar',0)>=2 for x in m))
  db.execute('INSERT OR REPLACE INTO extracted_evidence VALUES (?,?,?,?,?,?,?,?,?,?)',(cid,json.dumps(best),len(m),qualifying,best.get('closed_trades'),best.get('fills'),best.get('exposure'),'pending_trade_attribution','pending_funded_fill_replay','pending_forward_evidence'))
  done+=1
  if done%1000==0:db.commit()
 db.commit();print(json.dumps(dict(enriched=done,qualifying=db.execute('select sum(qualifying) from extracted_evidence').fetchone()[0],seconds=round(time.monotonic()-start,2))),flush=True)
if __name__=='__main__':run(Path(sys.argv[1]))
