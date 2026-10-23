"""Persistent, fail-closed sequence: wait for v3, resume Diversity, then compare evidence."""
import json,os,pathlib,subprocess,time,sys,traceback
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
ROOT=pathlib.Path('/opt/mts');GA=ROOT/'ga6';V3=GA/'runs/structural_v3_calibrated_active';DIV=GA/'runs/ga6_ev_swing40_diversity_v2_20261021';OUT=GA/'runs/post_v3_comparison_20261022';OUT.mkdir(exist_ok=True)
STATUS=OUT/'sequence_status.json'
def write(stage,**kw):
 STATUS.write_text(json.dumps(dict(stage=stage,updated=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),**kw),indent=2))
def alive(pid):
 try:os.kill(pid,0);return pathlib.Path('/proc/'+str(pid)+'/stat').read_text().split()[2]!='Z'
 except (ProcessLookupError,FileNotFoundError):return False
def analyze():
 import csv,sqlite3,collections
 from ga6.portfolio_pareto_20261021 import fitness
 groups=collections.defaultdict(list)
 con=sqlite3.connect('file:'+str(V3/'structural_manifest.sqlite')+'?mode=ro',uri=True)
 cache=sqlite3.connect('file:'+str(V3/'structural_evaluations.sqlite')+'?mode=ro',uri=True)
 # Each candidate may have multiple occurrences; unique structural definitions only.
 candidates=con.execute('select definition_json from candidates').fetchall()
 # Aggregate reliable generation summaries separately from individually replayable results.
 structural=[]
 for path in sorted(V3.glob('generation_*.json')):
  d=json.loads(path.read_text())
  for niche,v in d['per_niche'].items():structural.append(dict(system='structural_v3',generation=d['generation'],niche=niche,fitness=v['best_fitness'],completed_trades=v['completed_trades'],avg_sessions=v['avg_sessions_per_trade']))
 diversity=[]
 with (DIV/'all_evaluations.jsonl').open() as f:
  for line in f:
   d=json.loads(line);r=d['result'];m=r.get('ga6_completed_position_metrics',{})
   diversity.append(dict(system='diversity',generation=d['generation'],niche=d['origin_niche'],fitness=d['fitness'],completed_trades=m.get('completed_trades'),avg_sessions=m.get('avg_sessions'),win_rate=m.get('win_rate'),net_ev=m.get('net_ev_entry_equity'),ev_lcb=m.get('net_ev_lower_confidence_95'),cagr=r.get('cagr_diagnostic'),mdd=r.get('mdd_diagnostic'),chromosome_id=d['chromosome_id']))
 with (OUT/'diversity_chromosome_evidence.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=diversity[0]);w.writeheader();w.writerows(diversity)
 with (OUT/'structural_niche_generation_evidence.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=structural[0]);w.writeheader();w.writerows(structural)
 rows=[]
 for system,data in [('diversity',diversity),('structural_v3',structural)]:
  for niche in sorted({r['niche'] for r in data}):
   sub=[r for r in data if r['niche']==niche];best=max(sub,key=lambda r:r['fitness'])
   rows.append(dict(system=system,niche=niche,observations=len(sub),best_fitness=best['fitness'],best_generation=best['generation'],best_completed_trades=best['completed_trades'],best_avg_sessions=best['avg_sessions']))
 with (OUT/'niche_comparison.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 # A strategy is not declared tradable based on in-sample fitness alone.
 summary=dict(structural_generations=max(x['generation'] for x in structural),diversity_generations=max(x['generation'] for x in diversity),structural_best=max(x['fitness'] for x in structural),diversity_best=max(x['fitness'] for x in diversity),structural_unique_definitions=len(candidates),diversity_evaluation_rows=len(diversity),niche_comparison=rows,tradeability='NOT ESTABLISHED: requires same-window candidate-level replay, independent forward data, portfolio drawdown and cost checks',limitations=['Structural v3 starts 2025-01-01; original Diversity run starts 2005-09-14','Diversity resumes 200-chromosome population; structural v3 uses 400','Structural summary is niche-level; Diversity ledger is chromosome-level','These are development fitness observations, not independent tradability evidence'])
 (OUT/'comparison_report.json').write_text(json.dumps(summary,indent=2));return summary
try:
 write('waiting_for_structural_v3',pid=467776)
 while alive(467776):time.sleep(30)
 ck=V3/'structural_checkpoint.json';reports=sorted(V3.glob('generation_*.json'))
 if not ck.exists() or not reports:raise RuntimeError('Missing structural checkpoint or generation reports')
 latest=json.loads(reports[-1].read_text())['generation'];completed=json.loads(ck.read_text())['generation']
 if completed<latest:raise RuntimeError('Structural checkpoint behind generation report')
 # V3 ends either at 1000 generations or its explicit stagnation stop.
 monitor=V3/'stagnation_watch_status.json';ms=json.loads(monitor.read_text()) if monitor.exists() else {}
 if completed<1000 and ms.get('stop_reason')!='100_completed_generations_without_fitness_improvement':raise RuntimeError('V3 stopped unexpectedly; refusing to auto-resume Diversity')
 write('diversity_resuming',structural_generation=completed)
 cmd=[str(ROOT/'.venv/bin/python'),'ga6/production_portfolio_diversity_20261021.py','--features','ga5_redesign/exploratory79_ga4_enriched.parquet','--policy-file','ga5_redesign/exploratory79_policy.json','--output',str(DIV),'--generations','1000','--population','200','--workers','8','--stagnation','100','--production','--entry-mode','unrestricted']
 with (OUT/'diversity_resume.log').open('a') as log:
  result=subprocess.run(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT)+':'+str(ROOT/'ga5_redesign')},stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('Diversity resume failed with exit code '+str(result.returncode))
 write('analyzing')
 summary=analyze();write('analysis_complete',structural_best=summary['structural_best'],diversity_best=summary['diversity_best'],tradeability=summary['tradeability'])
except Exception as exc:
 write('failed_closed',error=str(exc),traceback=traceback.format_exc());raise
