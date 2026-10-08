"""Read-only, independent GA4 DEV80 lineage and risk audit."""
import json,hashlib,math,random,collections,statistics
from pathlib import Path
from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces
from Core.layered_ga.ga4_combination_genetics import propose,combine,chromosome_key
from Core.layered_ga.stage2_multiobjective_v3 import rank_candidates
from Core.layered_ga.stage2_nsga2_engine_v3 import Individual,environmental_selection
from Core.layered_ga.stage2_evaluator_v3 import CurveEvaluation
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint'
OUT=D/'ga4_postrun_audit'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(ch):return tuple(sorted(ch,key=chromosome_key))
def main():
 source=[D/'ga4_discovery_result.json',D/'ga4_discovery_budget.json',D/'checkpoint_manifest.json',D/'dev80_execution_arrays.npz']+sorted((D/'ga4_candidate_catalog').glob('*.json'))
 before={str(p.relative_to(D)):digest(p) for p in source}
 report=json.loads((D/'ga4_discovery_result.json').read_text());budget=report['budget'];manifest=json.loads((D/'checkpoint_manifest.json').read_text())
 records={}
 for p in sorted((D/'ga4_candidate_catalog').glob('*.json')):
  r=json.loads(p.read_text());assert r['fold']=='DEV80' and r['certified'] is False
  assert r['candidate_id'] not in records
  assert len(r['daily_horizon_evidence'])==63
  records[r['candidate_id']]=r
 assert len(records)==report['unique_evaluations']==report['candidate_records']==97
 assert manifest['dev37_opened'] is False
 spaces=stage2_search_spaces();rng=random.Random(budget['seed']);pool=[];cache={};lineage=[];counter=0;errors=[]
 def make(ch,parent_ids,generation):
  nonlocal counter
  ch=canonical(ch);key=tuple(chromosome_key(x) for x in ch)
  counter+=1;cid=f'c{counter:07d}'
  if key not in cache:
   encoded=[family+':'+json.dumps(genome,sort_keys=True,separators=(',',':'),allow_nan=False) for family,genome in ch]
   matches=[r for r in records.values() if r['chromosomes']==encoded]
   if len(matches)!=1:raise ValueError(f'Unmatched candidate {cid}: {len(matches)} matches')
   r=matches[0]
   curve=CurveEvaluation(r['side'],tuple({k:(float('nan') if v is None and k in ('ev_net','lcb95','mae_mean','mae_tail5') else v) for k,v in point.items()} for point in r['daily_horizon_evidence']),tuple(r['pareto_horizons']),tuple(tuple(x) for x in r['pareto_ranges']))
   cache[key]=(r['candidate_id'],curve)
  record_id,curve=cache[key]
  lineage.append({'individual_id':cid,'generation_born':generation,'parents':parent_ids,'candidate_id':record_id,'reused_cached_evidence':sum(x['candidate_id']==record_id for x in lineage)>0})
  return Individual({'chromosomes':ch},curve,cid)
 for _ in range(budget['population_size']):pool.append(make(propose(spaces,rng),[],0))
 ranks_summary=[]
 for g in range(budget['generations']):
  selected,ranks=environmental_selection(pool,budget['population_size'])
  saved=report['generations'][g]
  ids=[x.candidate_id for x in selected]
  if ids!=saved['selected']:errors.append({'generation':g,'error':'selection_order_mismatch','expected':saved['selected'],'actual':ids})
  if len(cache)!=saved['unique_evaluations']:errors.append({'generation':g,'error':'unique_evaluation_count_mismatch','expected':saved['unique_evaluations'],'actual':len(cache)})
  ranks_summary.append({'generation':g,'evaluated':len(pool),'selected_ids':ids,'ranked':[{ 'individual_id':x.candidate_id,'rank':[v if isinstance(v,int) or (isinstance(v,float) and math.isfinite(v)) else ('-Infinity' if v<0 else 'Infinity') for v in ranks.get(x.candidate_id,())]} for x in pool]})
  children=[]
  if g<budget['generations']-1:
   for _ in range(budget['population_size']):
    left,right=rng.sample(selected,2)
    child=combine(left.genome['chromosomes'],right.genome['chromosomes'],rng)
    children.append(make(child,[left.candidate_id,right.candidate_id],g+1))
  pool=selected+children
 if len(cache)!=97:errors.append({'error':'total_unique_mismatch','actual':len(cache)})
 if counter!=120:errors.append({'error':'total_individual_mismatch','actual':counter})
 risk=[]
 for r in records.values():
  points=r['daily_horizon_evidence'];usable=[p for p in points if isinstance(p.get('lcb95'),(int,float)) and math.isfinite(p['lcb95'])]
  positive=[p for p in usable if p['lcb95']>0]
  worst_cvar=min((p['cvar5'] for p in points if isinstance(p.get('cvar5'),(int,float)) and math.isfinite(p['cvar5'])),default=None)
  worst_mae=min((p['mae_tail5'] for p in points if isinstance(p.get('mae_tail5'),(int,float)) and math.isfinite(p['mae_tail5'])),default=None)
  best=max(usable,key=lambda p:p['lcb95']) if usable else None
  risk.append({'candidate_id':r['candidate_id'],'chromosomes':len(r['chromosomes']),'positive_lcb_horizons':len(positive),'best_horizon':best['horizon'] if best else None,'best_lcb95':best['lcb95'] if best else None,'best_horizon_cvar5':best.get('cvar5') if best else None,'best_horizon_mae_tail5':best.get('mae_tail5') if best else None,'worst_cvar5_across_horizons':worst_cvar,'worst_mae_tail5_across_horizons':worst_mae,'max_n':max(p['n'] for p in points),'nonzero_horizons':sum(p['n']>0 for p in points)})
 risk.sort(key=lambda x: (x['best_lcb95'] is not None,x['best_lcb95'] or -999),reverse=True)
 summary={'lineage_replay_exact':not errors,'errors':errors,'individuals':counter,'unique_candidates':len(cache),'candidate_catalog_count':len(records),'generations':len(ranks_summary),'positive_lcb_candidates':sum(x['positive_lcb_horizons']>0 for x in risk),'zero_observation_candidates':sum(x['nonzero_horizons']==0 for x in risk),'best_lcb_candidate':risk[0],'multiple_testing_adjusted':False,'independent_heldout_validated':False,'portfolio_catastrophic_risk_certified':False,'checkpoint_manifest_search_started':manifest['search_started'],'source_hashes':before}
 after={str(p.relative_to(D)):digest(p) for p in source}
 assert before==after,'Source changed during audit'
 OUT.mkdir(exist_ok=True)
 for name,value in [('summary.json',summary),('lineage.json',lineage),('selection_replay.json',ranks_summary),('risk_all_candidates.json',risk)]:
  p=OUT/name
  if p.exists():assert json.loads(p.read_text())==value,'Existing audit conflict: '+name
  else:p.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
 print(json.dumps({'replay_exact':summary['lineage_replay_exact'],'errors':errors,'individuals':counter,'unique_candidates':len(cache),'positive_lcb_candidates':summary['positive_lcb_candidates'],'zero_observation_candidates':summary['zero_observation_candidates'],'best_lcb_candidate':risk[0],'originals_unchanged':before==after,'audit_dir':str(OUT)},default=str),flush=True)
if __name__=='__main__':main()
