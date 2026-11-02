"""Independent completion and integrity checks; run after run_all.py."""
import sys,json,hashlib,sqlite3
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'source'))
from ga8.engine import load_panel,replay
from ga8.long_run import decode
from ga8.run import RAW

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
m=json.loads((P/'manifest.json').read_text());rows=json.loads((P/'qualifiers.json').read_text())
assert sha(P/'qualifiers.json')==m['qualifiers_sha256']
assert all(sha(P/k)==v for k,v in m['code_hashes'].items())
assert all(sha(k)==v for k,v in m['source_hashes'].items())
db=sqlite3.connect(f'file:{P}/catalog_snapshot.sqlite?mode=ro',uri=True)
n=db.execute("SELECT count(distinct id) FROM evaluations WHERE phase=1 AND json_extract(metrics_json,'$.cagr')>1.5*abs(json_extract(metrics_json,'$.max_drawdown')) AND abs(json_extract(metrics_json,'$.max_drawdown'))<0.20 AND (json_extract(metrics_json,'$.closed_trades') IS NULL OR json_extract(metrics_json,'$.closed_trades')>=30)").fetchone()[0]
assert n==len(rows),(n,len(rows))
results=[json.loads(l) for l in (P/'results.jsonl').open()]
assert len(results)==len(rows)==len({r['behavior_sha256'] for r in results})
assert {r['behavior_sha256'] for r in results}=={r['behavior_sha256'] for r in rows}
assert all(r['forward']['sessions']==252 for r in results)
bench=json.loads((P/'benchmarks.json').read_text())
previous=json.loads((P.parent/'ga8_forward_stop75_20261029/summary.json').read_text())
for name,b in bench.items():
 for key in ('cagr','max_drawdown','calmar','final_nav','closed_trades'):
  assert b[key]==previous['results'][name][key]
frozen=json.loads((P.parent/'ga8_forward_stop75_20261029/frozen_portfolio.json').read_text())
winner=next(r for r in results if frozen['id'] in r['source_ids'])
for k in ('cagr','max_drawdown','calmar','final_nav','closed_trades'):assert winner['forward'][k]==previous['results']['GA8'][k]
p,_=load_panel(RAW,end='2025-01-01')
for row in (rows[0],rows[len(rows)//2],rows[-1]):
 g,manager=decode(row);actual=replay(p,g,manager,'2022-01-01','2024-01-01')['metrics']
 assert actual==row['metrics'],row['id']
report=dict(completed=True,qualifiers=len(rows),results=len(results),independent_sql_gate_count=n,unique_and_complete=True,all_forward_sessions=252,source_journals_and_frozen_snapshot_unchanged=True,frozen_code_unchanged=True,training_parity_checks=3,previous_winner_forward_exact_parity=True,benchmark_exact_parity=True,runner_sha256=sha(P/'run_all.py'))
(P/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
