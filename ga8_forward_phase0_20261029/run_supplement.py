"""Verified Phase-0 supplement; never modifies production or Phase-1 outputs."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import sys,json,hashlib,sqlite3,time,fcntl
from pathlib import Path
from dataclasses import asdict
OUT=Path(__file__).resolve().parent
ALL=OUT.parent/'ga8_forward_all_20261029'
SRC=Path('/opt/mts/ga8/production_500_20261029')
sys.path.insert(0,str(ALL/'source'))
from ga8.long_run import decode
from ga8.engine import identity,load_panel,replay
from ga8.run import RAW

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(name,v):
 p=OUT/name;t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');t.replace(p)
def canonical(row):
 g,m=decode(row);gg=list(map(asdict,g))
 for x in gg:
  if x['entry_tree']:x.pop('family');x.pop('second');x.pop('op')
  elif x['op']=='single':x.pop('second')
 return hashlib.sha256(json.dumps([gg,asdict(m)],sort_keys=True).encode()).hexdigest()
def gate(m):return m['cagr']>1.5*abs(m['max_drawdown']) and abs(m['max_drawdown'])<.20 and (m.get('closed_trades') is None or m['closed_trades']>=30)
lock=(OUT/'runner.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
if not (OUT/'manifest.json').exists():
 paths=[SRC/'forward_2023.jsonl',SRC/'forward_2023.summary.json',SRC/'checkpoint.json.pre_survivors_only']
 before={str(p):sha(p) for p in paths}
 records=[json.loads(s) for s in paths[0].read_text().splitlines()]
 survivors=[r for r in records if r['forward_feasible']]
 summary=json.loads(paths[1].read_text());ids={r['id'] for r in survivors}
 assert len(survivors)==len(ids)==summary['forward_qualifying']==3
 assert ids=={r['id'] for r in summary['top_transferable'] if r['forward_feasible']}
 cp=json.loads(paths[2].read_text());parents=set()
 def walk(v):
  if isinstance(v,dict):
   parents.update(v.get('parents',[]))
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(cp);assert cp['phase']==1 and ids<=parents
 db=sqlite3.connect(f'file:{ALL}/catalog_snapshot.sqlite?mode=ro',uri=True);rows=[]
 for old in sorted(survivors,key=lambda r:r['id']):
  ident=old['id'];r=db.execute('SELECT first_phase,first_generation,genes_json,manager_json,parent_ids_json FROM chromosomes WHERE id=?',(ident,)).fetchone();assert r
  row=dict(id=ident,first_phase=r[0],first_generation=r[1],genes=json.loads(r[2]),manager=json.loads(r[3]),parents=json.loads(r[4]),phase0_evidence=old)
  assert identity(*decode(row))==ident
  assert any(json.loads(m)==old['train_metrics'] for m, in db.execute('SELECT metrics_json FROM evaluations WHERE id=? AND phase=0',(ident,)))
  row['behavior_sha256']=canonical(row);rows.append(row)
 db.close();assert before=={str(p):sha(p) for p in paths}
 write('cohort.json',rows)
 write('manifest.json',dict(cohort='phase0_forward_survivor',survivor_ids=sorted(ids),source_hashes=before,checkpoint_parent_ids=sorted(ids & parents),cohort_sha256=sha(OUT/'cohort.json'),phase1_manifest_sha256=sha(ALL/'manifest.json'),window=['2024-01-01','2025-01-01'],selection='All three saved 2023 survivors, user-approved before 2024 supplement; no 2024 selection',deduplication='Same canonical ordered normalized genes and manager as frozen Phase-1 job; memberships and source identities preserved',production_writes=False,evolution=False))
print('Frozen verified cohort; waiting for Phase-1 completion',flush=True)
while not (ALL/'summary.json').exists():time.sleep(10)
# Wait for writer to release its lock before reading final artifacts.
with (ALL/'runner.lock').open('r') as f:fcntl.flock(f,fcntl.LOCK_SH)
manifest=json.loads((OUT/'manifest.json').read_text());assert sha(ALL/'manifest.json')==manifest['phase1_manifest_sha256'];assert sha(OUT/'cohort.json')==manifest['cohort_sha256']
main=json.loads((ALL/'summary.json').read_text());quals=json.loads((ALL/'qualifiers.json').read_text());results=[json.loads(s) for s in (ALL/'results.jsonl').read_text().splitlines()]
assert main['tested']==main['eligible']==len(quals)==len(results)
assert len({r['behavior_sha256'] for r in results})==len(results)
for name,digest in json.loads((ALL/'manifest.json').read_text())['code_hashes'].items():assert sha(ALL/name)==digest
metadata=json.loads((ALL/'data_metadata.json').read_text());assert sha(RAW)==metadata['raw_sha256']
bench=json.loads((ALL/'benchmarks.json').read_text());merged={r['behavior_sha256']:dict(r,cohort_memberships=['phase1_training_qualifier'],cohort_evidence=[]) for r in results}
p=None;phase0=[];reused=0
for row in json.loads((OUT/'cohort.json').read_text()):
 k=row['behavior_sha256']
 if k in merged:
  r=merged[k];reused+=1
 else:
  if p is None:p,_=load_panel(RAW,end='2025-01-01')
  g,m=decode(row);full=replay(p,g,m,'2024-01-01','2025-01-01',True)
  dates=p.dates[(p.dates>='2024-01-01')&(p.dates<'2025-01-01')]
  assert [x['date'] for x in full['equity']]==dates.strftime('%Y-%m-%d').tolist()
  write(row['id']+'.json',full);m=full['metrics']
  r=dict(id=row['id'],behavior_sha256=k,source_ids=[row['id']],forward=m,forward_success=gate(m),beats_benchmark={n:m['final_nav']>b['final_nav'] for n,b in bench.items()},cohort_memberships=[],cohort_evidence=[]);merged[k]=r
 r['cohort_memberships'].append('phase0_forward_survivor')
 r['source_ids']=sorted(set(r['source_ids']+[row['id']]))
 r['cohort_evidence'].append(row)
 phase0.append(dict(survivor_id=row['id'],behavior_sha256=k,forward=r['forward'],forward_success=r['forward_success'],beats_benchmark=r['beats_benchmark'],cohort_memberships=r['cohort_memberships']))
write('phase0_summary.json',dict(survivors=phase0,benchmarks=bench,reused_phase1_replays=reused,new_replays=3-reused,QQQ=metadata['QQQ']))
with (OUT/'merged_results.jsonl').open('w') as f:
 for k,r in sorted(merged.items()):f.write(json.dumps(r,allow_nan=False)+'\n')
write('merged_summary.json',dict(status='complete',phase1_eligible=main['eligible'],phase1_tested=main['tested'],phase0_survivors=3,unique_behaviors=len(merged),cross_cohort_duplicates=reused,cohort_counts={'phase1_training_qualifier':len(results),'phase0_forward_survivor':3},forward_successes_unique=sum(r['forward_success'] for r in merged.values()),phase1_summary=main,phase0_outcomes=phase0,benchmarks=bench,QQQ=metadata['QQQ'],conventions=metadata['conventions'],limitations=metadata['limitations'],window=manifest['window'],source_result_sha256=sha(ALL/'results.jsonl'),source_summary_sha256=sha(ALL/'summary.json')))
print(json.dumps(json.loads((OUT/'phase0_summary.json').read_text()),indent=2),flush=True)
