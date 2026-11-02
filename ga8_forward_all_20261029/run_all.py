"""Isolated exhaustive phase-1 replay. Resume by rerunning this file."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import sys,json,hashlib,sqlite3,shutil,fcntl,time,csv
from pathlib import Path
from dataclasses import asdict
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
SRC=Path('/opt/mts/ga8/production_500_20261029')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(name,v):
 p=OUT/name;t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');t.replace(p)
lock=(OUT/'runner.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
# Freeze source to avoid concurrent edits changing a resumed replay.
if not (OUT/'source').exists():
 for package in ('ga8','ga9'):
  dest=OUT/'source'/package;dest.mkdir(parents=True)
  for p in (ROOT/package).glob('*.py'):shutil.copy2(p,dest/p.name)
 shutil.copy2(ROOT/'ga8_forward_stop75_20261029/run_forward.py',OUT/'source/previous_forward.py')
sys.path.insert(0,str(OUT/'source'))
from ga8.engine import Gene,Manager,load_panel,replay,identity
from ga8.long_run import decode
from ga8.run import RAW
sys.path.insert(0,str(OUT/'source'))
import previous_forward as prior
prior.OUT=OUT

def gate(m):
 return (m['cagr']>1.5*abs(m['max_drawdown']) and abs(m['max_drawdown'])<.20
         and (m.get('closed_trades') is None or m['closed_trades']>=30))
def canonical(row):
 genes,manager=decode(row);gg=list(map(asdict,genes))
 for g in gg:
  # These selectors are provably unused by engine.scores in these branches.
  if g['entry_tree']:g.pop('family');g.pop('second');g.pop('op')
  elif g['op']=='single':g.pop('second')
 return hashlib.sha256(json.dumps([gg,asdict(manager)],sort_keys=True).encode()).hexdigest()

def enumerate_all():
 db=sqlite3.connect(f'file:{SRC}/chromosome_library.sqlite?mode=ro',uri=True)
 db.backup(sqlite3.connect(OUT/'catalog_snapshot.sqlite'));db.close()
 db=sqlite3.connect(OUT/'catalog_snapshot.sqlite')
 candidates={};seen=set();count=0;sources={};conflicts=0
 evidence=(OUT/'training_observations.jsonl').open('w')
 def consume(row,source,generation):
  nonlocal count,conflicts
  count+=1;k=canonical(row);seen.add(k)
  if not gate(row['metrics']):return
  obs=dict(source=source,generation=generation,id=row['id'],behavior_sha256=k,metrics=row['metrics'])
  evidence.write(json.dumps(obs)+'\n')
  if k not in candidates:candidates[k]=dict(row,behavior_sha256=k,source_ids=[],observations=0)
  r=candidates[k];r['observations']+=1
  if row['id'] not in r['source_ids']:r['source_ids'].append(row['id'])
  if r['metrics']!=row['metrics']:conflicts+=1
 # Catalog preserves evaluations that generation frontiers alone cannot recover.
 for ident,generation,m,g,manager,parents in db.execute('SELECT e.id,e.generation,e.metrics_json,c.genes_json,c.manager_json,c.parent_ids_json FROM evaluations e JOIN chromosomes c ON c.id=e.id WHERE e.phase=1 ORDER BY e.generation,e.id'):
  consume(dict(id=ident,genes=json.loads(g),manager=json.loads(manager),parents=json.loads(parents),metrics=json.loads(m)),'catalog',generation)
 db.close()
 hashes={}
 for p in sorted(SRC.glob('generations.jsonl*')):
  hashes[str(p)]=sha(p);n=0
  with p.open() as f:
   for line in f:
    d=json.loads(line)
    if d.get('phase')!=1:continue
    for row in d.get('rows',[]):consume(row,p.name,d.get('fold_generation'));n+=1
  sources[p.name]=n
 # Frozen checkpoint/frontiers add any retained evaluated chromosomes.
 for name in ('checkpoint.json','status.json'):
  p=SRC/'manual_stop_75_20261029'/name;hashes[str(p)]=sha(p)
  d=json.loads(p.read_text())
  def walk(v):
   if isinstance(v,dict):
    if all(k in v for k in ('id','genes','manager','metrics')):consume(v,'frozen_'+name,d.get('fold_generation'))
    else:
     for val in v.values():walk(val)
   elif isinstance(v,list):
    for val in v:walk(val)
  if d.get('phase')==1:walk(d)
 evidence.close()
 rows=sorted(candidates.values(),key=lambda r:r['behavior_sha256'])
 write('qualifiers.json',rows)
 write('manifest.json',dict(scope='ALL distinct qualifying phase-1 genomes; no cap or forward selection',training_gate='CAGR > 1.5*abs(MDD), abs(MDD)<0.20, closed_trades>=30 when available',training_start='2022-01-01',training_end_exclusive='2024-01-01',forward_start='2024-01-01',forward_end_exclusive='2025-01-01',initial_nav=100000,phase1_observations=count,distinct_phase1_behaviors=len(seen),qualifiers=len(rows),qualifying_metric_discrepancies=conflicts,journal_phase1_counts=sources,source_hashes=hashes,catalog_snapshot_sha256=sha(OUT/'catalog_snapshot.sqlite'),qualifiers_sha256=sha(OUT/'qualifiers.json'),code_hashes={str(p.relative_to(OUT)):sha(p) for p in (OUT/'source').rglob('*.py')},deduplication='Full SHA256 of default-normalized ordered genes and manager; ignore only inactive score selectors. Gene order preserved because tie execution can depend on it.',reference='ga8.forward_catalog.forward_all; isolated implementation uses requested gates and fsync checkpoint; never writes production library'))
 return rows

rows=json.loads((OUT/'qualifiers.json').read_text()) if (OUT/'manifest.json').exists() else enumerate_all()
print('ALL qualifiers:',len(rows),flush=True)
assert sha(OUT/'qualifiers.json')==json.loads((OUT/'manifest.json').read_text())['qualifiers_sha256']
p,audit=load_panel(RAW,end='2025-01-01')
dates=p.dates[(p.dates>='2024-01-01')&(p.dates<'2025-01-01')]
if not (OUT/'benchmarks.json').exists():
 spy,spy_audit=prior.load_primary(prior.SPY,prior.BenchmarkPolicy('broad_us'),'2025-01-01',dates)
 benchmarks={}
 for name,panel in [('SPY',spy),('equal_weight_DEV79',p)]:
  r=prior.passive(panel,dates);assert [x['date'] for x in r['equity']]==dates.strftime('%Y-%m-%d').tolist()
  write(name+'.json',r);benchmarks[name]=r['metrics']
 write('benchmarks.json',benchmarks)
 write('data_metadata.json',dict(raw=str(RAW),raw_sha256=sha(RAW),spy=str(prior.SPY),spy_sha256=sha(prior.SPY),raw_audit=audit,spy_audit=spy_audit,symbols=p.symbols,sessions=len(dates),first=str(dates[0]),last=str(dates[-1]),QQQ='Absent from DEV79 and previous forward metadata reports no real QQQ parquet under /opt/mts.',conventions=['Fresh $100000 cash per chromosome and benchmark; identical 252 sessions.','Jan 2 close decision, earliest Jan 3 open execution.','5bp adverse slippage and 1bp commission; T+2 for GA8; dividend receivables nonspendable; no terminal liquidation.','No forward fitting or selection.'],limitations=['Retrospective DEV79 universe; complete historical PIT/delisted coverage unproven.','Chronological out-of-training replay, not prospectively sealed experiment.','Equal-weight fixed 79 sleeves, GEV cash until regular listing.']))
benchmarks=json.loads((OUT/'benchmarks.json').read_text())
results_path=OUT/'results.jsonl';done={}
if results_path.exists():
 with results_path.open('rb+') as f:
  while True:
   pos=f.tell();line=f.readline()
   if not line:break
   try:r=json.loads(line)
   except json.JSONDecodeError:f.truncate(pos);break
   done[r['behavior_sha256']]=r
started=time.time()
with results_path.open('a') as f:
 for row in rows:
  k=row['behavior_sha256']
  if k in done:continue
  genes,manager=decode(row);r=replay(p,genes,manager,'2024-01-01','2025-01-01',True)
  assert [x['date'] for x in r['equity']]==dates.strftime('%Y-%m-%d').tolist()
  m=r['metrics'];record=dict(behavior_sha256=k,id=row['id'],source_ids=row['source_ids'],training=row['metrics'],forward=m,forward_success=gate(m),beats_benchmark={n:m['final_nav']>b['final_nav'] for n,b in benchmarks.items()})
  f.write(json.dumps(record,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno());done[k]=record
  write('checkpoint.json',dict(eligible=len(rows),completed=len(done),remaining=len(rows)-len(done),last_id=row['id'],elapsed_this_invocation=time.time()-started))
  if len(done)%10==0:print('completed',len(done),'/',len(rows),flush=True)
import numpy as np
all_results=[done[r['behavior_sha256']] for r in rows]
def dist(vals):
 return dict(zip(['min','p05','p25','median','p75','p95','max'],map(float,np.quantile(vals,[0,.05,.25,.5,.75,.95,1]))))
summary=dict(eligible=len(rows),tested=len(all_results),forward_successes=sum(r['forward_success'] for r in all_results),forward_success_rate=sum(r['forward_success'] for r in all_results)/len(rows) if rows else None,benchmarks=benchmarks,benchmark_wins={n:sum(r['beats_benchmark'][n] for r in all_results) for n in benchmarks},distributions={period:{metric:dist([r[period][metric] for r in all_results]) for metric in ['cagr','max_drawdown','calmar','final_nav','closed_trades']} for period in ['training','forward']} if rows else {},winners=sorted(all_results,key=lambda r:r['forward']['final_nav'],reverse=True)[:10],losers=sorted(all_results,key=lambda r:r['forward']['final_nav'])[:10])
write('summary.json',summary)
with (OUT/'per_chromosome.csv').open('w') as f:
 fields=['behavior_sha256','id','forward_success']+[a+'_'+b for a in ['training','forward'] for b in ['cagr','max_drawdown','calmar','final_nav','closed_trades']]+['beats_'+n for n in benchmarks]
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in all_results:
  out={k:r[k] for k in fields[:3]}
  for a in ['training','forward']:
   for b in ['cagr','max_drawdown','calmar','final_nav','closed_trades']:out[a+'_'+b]=r[a].get(b)
  out.update({'beats_'+n:v for n,v in r['beats_benchmark'].items()});w.writerow(out)
print(json.dumps({k:v for k,v in summary.items() if k not in ['winners','losers','distributions']},indent=2),flush=True)
