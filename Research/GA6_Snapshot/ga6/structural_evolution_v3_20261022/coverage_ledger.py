"""Persistent breadth-first screening ledger. Never labels untested candidates evaluated."""
import sqlite3,json,pathlib,datetime
ROOT=pathlib.Path(__file__).resolve().parent
DB=ROOT/'structural_coverage.sqlite'
con=sqlite3.connect(DB)
con.execute('CREATE TABLE IF NOT EXISTS structures (id TEXT PRIMARY KEY, kind TEXT NOT NULL, arity INTEGER NOT NULL, definition_json TEXT NOT NULL, state TEXT NOT NULL DEFAULT \'UNTESTED\', trials INTEGER NOT NULL DEFAULT 0, score REAL, updated_utc TEXT)')
con.execute('CREATE INDEX IF NOT EXISTS idx_coverage ON structures(state,kind,arity)')
for name,kind in [('structural_catalog.jsonl','flat'),('grouped_two_block_catalog.jsonl','grouped_two_block')]:
 with (ROOT/name).open() as f:
  batch=[]
  for line in f:
   x=json.loads(line);batch.append((x['id'],kind,x['arity'],json.dumps(x,sort_keys=True)))
   if len(batch)>=1000:
    con.executemany('INSERT OR IGNORE INTO structures(id,kind,arity,definition_json) VALUES(?,?,?,?)',batch);batch=[]
  if batch:con.executemany('INSERT OR IGNORE INTO structures(id,kind,arity,definition_json) VALUES(?,?,?,?)',batch)
con.commit()
counts=con.execute('SELECT kind,state,COUNT(*) FROM structures GROUP BY kind,state').fetchall()
assert sum(x[2] for x in counts)==14652,counts
assert all(x[1]=='UNTESTED' for x in counts)
print(json.dumps({'database':str(DB),'counts':[{'kind':a,'state':b,'count':c} for a,b,c in counts],'schema':'persistent candidate state, trials, score; no claims of completed evaluation'},indent=2))
con.close()
