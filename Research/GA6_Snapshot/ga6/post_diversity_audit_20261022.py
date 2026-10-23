"""Post-run profitability, drawdown and exact-definition deduplication audit."""
import csv,json,hashlib,sqlite3,pathlib,collections,math
BASE=pathlib.Path('/opt/mts/ga6/runs');OUT=BASE/'post_v3_comparison_20261022';OUT.mkdir(exist_ok=True)
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(obj):return hashlib.sha256(canonical(obj).encode()).hexdigest()
def number(v):
 try:
  f=float(v);return f if math.isfinite(f) else None
 except (TypeError,ValueError):return None
def run():
 systems=collections.defaultdict(dict);counts=collections.Counter();duplicates=collections.Counter();collisions=[]
 def add(system,definition,fitness,result,niche,generation):
  key=digest(definition);counts[system]+=1
  if key in systems[system]:
   duplicates[system]+=1;old=systems[system][key]
   if old['definition']!=canonical(definition):collisions.append((system,key))
   return
  m=result.get('ga6_completed_position_metrics',{});p=result.get('ga6_portfolio_diagnostics',{})
  systems[system][key]=dict(system=system,definition_hash=key,niche=niche,first_generation=generation,fitness=number(fitness),completed_trades=m.get('completed_trades'),win_rate=m.get('win_rate'),avg_sessions=m.get('avg_sessions'),net_ev=m.get('net_ev_entry_equity'),ev_lcb=m.get('net_ev_lower_confidence_95'),cagr=result.get('cagr_diagnostic'),mdd=result.get('mdd_diagnostic'),calmar=result.get('calmar_diagnostic'),turnover=p.get('annualized_two_way_turnover'),fee_drag=p.get('fee_drag_starting_capital'),definition=canonical(definition))
 div=BASE/'ga6_ev_swing40_diversity_v2_20261021'
 with (div/'all_evaluations.jsonl').open() as f:
  for line in f:
   r=json.loads(line);add('diversity',r['genome'],r['fitness'],r['result'],r['origin_niche'],r['generation'])
 st=BASE/'structural_v3_calibrated_active';manifest=sqlite3.connect('file:'+str(st/'structural_manifest.sqlite')+'?mode=ro',uri=True);cache=sqlite3.connect('file:'+str(st/'structural_evaluations.sqlite')+'?mode=ro',uri=True)
 from ga6.portfolio_pareto_20261021 import fitness
 # Evaluation keys are cache fingerprints, not chromosome IDs. Match through trial provenance.
 query='select c.definition_json,o.generation,t.cache_key,e.result from candidates c join occurrences o on o.structural_id=c.structural_id join (select trial_id,cache_key from (select trial_id,cache_key from temp.missing)) t on t.trial_id=o.trial_id join evaluations e on e.key=t.cache_key'
 # Manifest definitions are unique; cached results are joined by their documented hash recipe.
 import hashlib
 from ga5_redesign.canonical_engine import digest_file
 source=pathlib.Path('/opt/mts/ga5_redesign/exploratory79_ga4_enriched.parquet');policy=pathlib.Path('/opt/mts/ga5_redesign/exploratory79_policy.json')
 modules=('structural_runner_diagnostic.py','structural_batch.py','structural_candidate.py','structural_population.py','structural_portfolio_evaluator.py','structural_decision.py','family_logic.py','discovery_allocation.py','development_feedback_ledger.py','tree_operators.py','thresholds.py','threshold_calibration.json')
 root=pathlib.Path('/opt/mts/ga6/structural_evolution_v3_20261022');code=hashlib.sha256(''.join(digest_file(root/n) for n in modules).encode()).hexdigest();data_hash=digest_file(source)+'2025-01-01'+'2026-09-15';policy_hash=digest_file(policy)
 for sid,raw in manifest.execute('select structural_id,definition_json from candidates'):
  d=json.loads(raw);key=hashlib.sha256(f'{code}:{data_hash}:{policy_hash}:{sid}'.encode()).hexdigest();hit=cache.execute('select result from evaluations where key=?',(key,)).fetchone()
  if hit is None:raise RuntimeError('Missing structural cached result for '+sid)
  r=json.loads(hit[0]);niche=d['genome']['niche'];add('structural_v3',{'entry_tree':d['entry_tree'],'genome':d['genome']},fitness(r),r,niche,None)
 allrows=[]
 for system,items in systems.items():
  for row in items.values():
   x={k:v for k,v in row.items() if k!='definition'};mdd=number(x['mdd']);ev=number(x['ev_lcb']);cagr=number(x['cagr']);n=int(x['completed_trades'] or 0)
   flags=[]
   if n<100:flags.append('under_100_completed_trades')
   if ev is None or ev<=0:flags.append('ev_lcb_not_positive')
   if cagr is None or cagr<=0:flags.append('cagr_not_positive')
   if mdd is None or abs(mdd)>.25:flags.append('mdd_over_25pct')
   x['development_screen']='PASS' if not flags else 'FAIL';x['flags']=';'.join(flags);allrows.append(x)
 if not allrows:raise RuntimeError('No evaluations')
 with (OUT/'unique_chromosome_profitability_drawdown.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
 with (OUT/'unique_chromosome_definitions.jsonl').open('w') as f:
  for system,items in systems.items():
   for key,row in items.items():f.write(json.dumps({'system':system,'definition_hash':key,'definition':json.loads(row['definition'])},sort_keys=True)+'\n')
 niche=[]
 for system in sorted(systems):
  for n in sorted({r['niche'] for r in systems[system].values()}):
   rows=[r for r in allrows if r['system']==system and r['niche']==n];best=max(rows,key=lambda r:number(r['ev_lcb']) if number(r['ev_lcb']) is not None else -100)
   niche.append(dict(system=system,niche=n,unique_chromosomes=len(rows),development_passes=sum(r['development_screen']=='PASS' for r in rows),best_ev_lcb=best['ev_lcb'],best_cagr=best['cagr'],best_mdd=best['mdd'],best_hash=best['definition_hash']))
 with (OUT/'niche_profitability_drawdown.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(niche[0]));w.writeheader();w.writerows(niche)
 report=dict(status='COMPLETE',counts=dict(counts),unique={s:len(v) for s,v in systems.items()},duplicate_occurrences=dict(duplicates),hash_collisions=collisions,development_passes={s:sum(r['development_screen']=='PASS' for r in allrows if r['system']==s) for s in systems},tradeability='NOT PROVEN: independent forward validation and matched-window portfolio replay required',comparability='Different evaluation windows: do not rank raw CAGR or MDD across systems as matched',outputs=['unique_chromosome_profitability_drawdown.csv','unique_chromosome_definitions.jsonl','niche_profitability_drawdown.csv'])
 (OUT/'profitability_drawdown_dedup_report.json').write_text(json.dumps(report,indent=2));return report
if __name__=='__main__':print(json.dumps(run(),indent=2))
