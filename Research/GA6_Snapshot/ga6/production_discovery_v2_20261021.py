"""Versioned GA6 discovery integration runner; NOT CERTIFIED for production.
Development feedback and executable grouped grammar remain release blockers.
"""
import argparse,base64,hashlib,json,pickle,random,sys,time,os,math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from dataclasses import asdict
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
sys.path.insert(0,str(Path(__file__).resolve().parent.parent / "ga5_redesign"))
from niche_seeds import initial
from ga6.portfolio_pareto_20261021 import fitness, rank_scored
from ga6.breeder_portfolio_20261021 import breed_ga6
from ga6.upgrade_reuse_20261021.discovery_population import propose
from ga6.upgrade_reuse_20261021.discovery_allocation import Observation,ACTIVITIES

from ga6.fast_portfolio_evaluator_20261021 import evaluate
from optimizer_v3 import NICHES
from unified_evolution import breed
from evolution_controls import breed_next,diversity
from ga5_chromosome_contract import Genome
from canonical_engine import ResultCache,digest_file
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from runner_v4 import engine_fingerprint
from exit_objectives import pareto_front

_WORKER_PREPARED=None
_WORKER_POLICY=None

def _worker_init(frame,blocked,membership,veto,cash_yield,niche_labels,entry_mode):
 global _WORKER_PREPARED,_WORKER_POLICY
 _WORKER_PREPARED=frame if isinstance(frame,PreparedSessions) else PreparedSessions(frame)
 _WORKER_POLICY=(blocked,membership,veto,cash_yield,niche_labels,entry_mode)

def _worker_evaluate(genome):
 blocked,membership,veto,cash_yield,niche_labels,entry_mode=_WORKER_POLICY
 return evaluate(_WORKER_PREPARED,genome,blocked=blocked,membership=membership,risk_veto=veto,annual_cash_yield=cash_yield,niche_labels=niche_labels if entry_mode=="origin" else None)

def run(argv=None):
 p=argparse.ArgumentParser()
 for arg in ('features','policy-file','output'):p.add_argument('--'+arg,required=True)
 p.add_argument('--generations',type=int,default=1)
 p.add_argument('--population',type=int,default=200)
 p.add_argument('--workers',type=int,default=min(8,len(os.sched_getaffinity(0))))
 p.add_argument('--diagnostic-only',action='store_true')
 p.add_argument('--production',action='store_true')
 p.add_argument('--stagnation',type=int,default=100)
 p.add_argument('--entry-mode',choices=('origin','unrestricted'),default='unrestricted')
 a=p.parse_args(argv)
 if a.diagnostic_only==a.production:raise ValueError('Specify exactly one of --diagnostic-only or --production')
 if a.population<len(NICHES)*2 or a.generations<0 or a.stagnation<1 or not 1<=a.workers<=len(os.sched_getaffinity(0)):raise ValueError('Invalid budget or worker count')
 source=Path(a.features);manifest=json.loads(source.with_suffix('.manifest.json').read_text())
 if manifest.get('engine')!='ga5-research-v4' or not manifest.get('source_sha256'):raise ValueError('Unverified feature manifest')
 frame=pd.read_parquet(source)
 if not {'dividends','stock_splits'}.issubset(frame.columns):raise ValueError('Corporate actions required')
 from ga5_feature_adapter import LEGACY
 from ga5_chromosome_contract import FEATURES
 available={name for name in FEATURES if LEGACY.get(name,name) in frame.columns}
 if len(available)<len(FEATURES):raise ValueError('Missing chromosome feature columns: '+str(sorted(FEATURES-available)))
 if frame.ticker.nunique()!=79 or 'SMCI' in set(frame.ticker):raise ValueError('DEV79 governance violation')
 frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
 prepared=PreparedSessions(frame)
 labels_path=Path(__file__).resolve().parent.parent / "ga5_redesign" / "dev79_niche_ga_v1"/"labels.parquet"
 if not labels_path.is_file():raise ValueError("DEV79 niche labels required")
 label_frame=pd.read_parquet(labels_path)
 niche_labels={(str(r.date)[:10],r.ticker):r.research_niche for r in label_frame.itertuples(index=False)}
 for key in prepared.membership_keys:niche_labels.setdefault(key,None)
 policy=json.loads(Path(a.policy_file).read_text())
 membership={(d,t):v for d,t,v in policy['membership']}
 veto=policy['risk_veto'];blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
 if not prepared.membership_keys.issubset(membership) or not prepared.dates.issubset(veto):raise ValueError('Incomplete policies')
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 # Include the unrestricted engine in the cache fingerprint.
 code=hashlib.sha256((digest_file(Path(__file__).resolve().parent / "fast_portfolio_evaluator_20261021.py")+digest_file(Path(__file__).resolve().parent / "selection.py")+engine_fingerprint()+digest_file(Path(__file__))+digest_file(Path(__file__).resolve().parent.parent / "ga5_redesign" / "unified_evolution.py")+digest_file(Path(__file__).resolve().parent.parent / "ga5_redesign" / "evolution_controls.py")+digest_file(Path(__file__).resolve().parent / "breeder_portfolio_20261021.py")+digest_file(Path(__file__).resolve().parent.parent / "ga5_redesign" / "optimizer_v3.py")+digest_file(Path(__file__).resolve().parent.parent / "ga5_redesign" / "niche_seeds.py")+digest_file(Path(__file__).resolve().parent.parent / "ga5_redesign" / "exit_objectives.py")+digest_file(Path(__file__).resolve().parent / "position_equity_risk_20261021.py")+digest_file(Path(__file__).resolve().parent / "fast_portfolio_evaluator_20261021.py")+digest_file(Path(__file__).resolve().parent / "portfolio_pareto_20261021.py")+digest_file(Path(__file__).resolve().parent.parent / "ga5_redesign" / "shadow_signals.py")+digest_file(Path(__file__).parent.parent/'ga5_chromosome_contract.py')+digest_file(labels_path)+digest_file(Path(__file__).resolve().parent / 'niche_evidence.py')+digest_file(Path(__file__).resolve().parent / 'path_replay.py')+digest_file(Path(__file__).resolve().parent / 'counterfactuals.py')+digest_file(Path(__file__).resolve().parent / 'prospective_policy.py')+digest_file(Path(__file__).resolve().parent / 'prospective_replay.py')+digest_file(Path(__file__).resolve().parent / 'policy_genes.py')+digest_file(Path(__file__).resolve().parent / 'policy_research.py')+digest_file(Path(__file__).resolve().parent / 'fitness_policy.py')+digest_file(Path(__file__).resolve().parent / 'chronological_validation.py')+digest_file(Path(__file__).resolve().parent / 'policy_evolution_oos.py')+digest_file(Path(__file__).resolve().parent / 'episode_uncertainty.py')+digest_file(Path(__file__).resolve().parent / "upgrade_reuse_20261021" / "discovery_population.py")+digest_file(Path(__file__).resolve().parent / "upgrade_reuse_20261021" / "discovery_allocation.py")+digest_file(Path(__file__).resolve().parent / "upgrade_reuse_20261021" / "development_feedback_ledger.py")+a.entry_mode).encode()).hexdigest()
 data=digest_file(source);policy_hash=digest_file(Path(a.policy_file))
 rng=random.Random(6106);cache=ResultCache(out/'evaluations.sqlite')
 seed_members=[initial(n) for n in NICHES]
 members,_=breed_next([(0.0,g,{}) for g in seed_members],rng,a.population)
 best=None;history=[]
 discovery_observations={}
 candidate_origins={}
 generation_start=time.monotonic()
 checkpoint=out/'checkpoint_unified.json'
 ledger=out/'all_evaluations.jsonl'
 start=0
 if checkpoint.exists():
  state=json.loads(checkpoint.read_text())
  if (state['data'],state['policy'],state['code'],state['population'])!=(data,policy_hash,code,a.population):raise ValueError('Checkpoint fingerprint mismatch')
  start=state['generation'];rng.setstate(pickle.loads(base64.b64decode(state['rng'])))
  members=[Genome(**g) for g in state['members']];history=state['history']
  if state['best']:best=state['best']
  discovery_observations={k:Observation(**v) for k,v in state.get('discovery_observations',{}).items()}
  candidate_origins=state.get('candidate_origins',{})
 try:
  with ProcessPoolExecutor(max_workers=a.workers,initializer=_worker_init,initargs=(prepared,blocked,membership,veto,policy['cash_proxy_annual_yield'],niche_labels,a.entry_mode)) as pool:
   for generation in __import__("itertools").count(start):
    if a.generations and generation>=a.generations:break
    scored=[];missing=[]
    generation_start=time.monotonic()
    for genome in members:
     key=cache.key(genome,data,'DEV79_FULL','ga6:'+policy_hash+':'+code)
     result=cache.get(key)
     if result is None:missing.append((genome,key))
     else:scored.append((fitness(result),genome,result))
    if missing:
     for (genome,key),result in zip(missing,pool.map(_worker_evaluate,[g for g,_ in missing])):
      cache.put(key,result)
      scored.append((fitness(result),genome,result))
    scored.sort(key=lambda v:(-v[0],v[1].identity()))
    scored=rank_scored(scored)
    niche_ranks=None
    if generation==0 and not any(item[2].get("signal_trace",{}).get("executed_buys",0)>0 for item in scored):
     diagnostic={"status":"PREFLIGHT_FAILED_ZERO_TRADES","population":len(scored),"signals":{k:sum(item[2].get("signal_trace",{}).get(k,0) for item in scored) for k in ("feature_valid","feature_missing","signal_enter","niche_match","niche_reject","scheduled_entries","executed_buys","executed_sells")}}
     (out/"preflight_failure.json").write_text(json.dumps(diagnostic,indent=2))
     raise RuntimeError("GA preflight failed: zero executed BUY fills; "+json.dumps(diagnostic["signals"]))
    with ledger.open("a") as fh:
     for score,genome,result in scored:
      fh.write(json.dumps({"generation":generation+1,"chromosome_id":genome.identity(),"origin_niche":genome.niche,"genome":asdict(genome),"fitness":score,"result":result},default=str)+"\n")
    if best is None or scored[0][0]>best['fitness']:
     best={'fitness':scored[0][0],'genome':asdict(scored[0][1]),'result':scored[0][2]}
    history.append({'generation':generation+1,'unique':len({g.identity() for _,g,_ in scored}),'niches_represented':len({g.niche for _,g,_ in scored}),'best_fitness':scored[0][0]})
    # Pareto comparisons use complete historical trade outcomes for research
    # ranking only. Future selector decisions must remain chronological.
    eligible=scored
    front=list(range(min(len(scored),a.population//4)))
    # Rank nondominated candidates by independently measured portfolio fitness;
    # do not privilege arbitrary ordering from the Pareto implementation.
    pareto_elites=[eligible[i] for i in front]
    parent_count=max(2,a.population//4)
    parents=[g for _,g,_ in pareto_elites[:parent_count]]
    parents.extend(g for _,g,_ in scored if g.identity() not in {x.identity() for x in parents})
    parents=parents[:parent_count]
    history[-1]["niche_eligible_counts"]={n:sum(g.niche==n for _,g,_ in scored) for n in NICHES}
    history[-1]["niche_leaders"]={n:next((g.identity() for _,g,_ in scored if g.niche==n),None) for n in NICHES}
    history[-1]['niche_counts']={n:sum(g.niche==n for _,g,_ in scored) for n in NICHES}
    history[-1]['distinct_gene_patterns']=len({(g.entry_feature,g.exit_feature,g.hold_feature,g.regime_feature,g.sizing_feature,g.replace_feature) for _,g,_ in scored})
    history[-1]['fitness_mean']=sum(v[0] for v in scored)/len(scored)
    history[-1]['fitness_median']=sorted(v[0] for v in scored)[len(scored)//2]
    history[-1]['best_ever_fitness']=best['fitness']
    history[-1]['exit_pareto_count']=len(front)
    history[-1]['exit_metric_eligible']=len(eligible)
    # Development-feedback rewards are NOT YET IMPLEMENTED.
    # Track trial counts and provenance, but prohibit in-sample fitness rewards.
    elapsed=max(.001,time.monotonic()-generation_start)
    counts={a:0 for a in ACTIVITIES};novel={a:0 for a in ACTIVITIES}
    for score,g,_ in scored:
     activity=candidate_origins.get(g.identity())
     if activity in counts:
      counts[activity]+=1
      # Do not count positive fitness as novelty or validation.
    for activity in ACTIVITIES:
     previous=discovery_observations.get(activity,Observation(0,0,0.0))
     discovery_observations[activity]=Observation(previous.trials+counts[activity],previous.novel+novel[activity],previous.compute_seconds+elapsed*counts[activity]/max(1,len(scored)),previous.uncertainty,previous.stable_fraction,previous.diverse_fraction)
    # Until purged dev-feedback and delayed-credit ledger exist, allocation stays frozen.
    members,offspring_diversity=propose(scored,rng,a.population,generation+1,None)
    candidate_origins={g.identity():activity for g,activity in zip(members,offspring_diversity.get('origins',[]))}
    history[-1]['next_population_diversity']=offspring_diversity
    history[-1]['discovery_observations']={k:asdict(v) for k,v in discovery_observations.items()}
    history[-1]['adaptive_reward_status']='DISABLED_PENDING_INDEPENDENT_DEV_FEEDBACK'
    state={'data':data,'policy':policy_hash,'code':code,'population':a.population,'generation':generation+1,'rng':base64.b64encode(pickle.dumps(rng.getstate())).decode(),'members':[asdict(g) for g in members],'history':history,'best':best,'discovery_observations':{k:asdict(v) for k,v in discovery_observations.items()},'candidate_origins':candidate_origins}
    tmp=checkpoint.with_suffix('.tmp');tmp.write_text(json.dumps(state));tmp.replace(checkpoint)
    print(json.dumps({"generation":generation+1,"best":best["fitness"],"niches":history[-1]["niches_represented"],"gene_patterns":history[-1]["distinct_gene_patterns"]}),flush=True)
    if len(history)>=a.stagnation+1 and max(h["best_ever_fitness"] for h in history[-a.stagnation:])<=history[-a.stagnation-1]["best_ever_fitness"]+1e-8:
     print("STAGNATION_STOP",generation+1,flush=True);break
 finally:cache.close()
 report={'status':'PRODUCTION_RESEARCH' if a.production else 'DIAGNOSTIC_ONLY','architecture':'GA6 conservative completed-position EV fitness; niche-protected evolutionary population','entry_mode':a.entry_mode,'research_validity':'NICHE_ENTRY_HOLD_EXIT_SINGLE_TRADE_RETROSPECTIVE_NOT_OOS','evaluations':len(history)*a.population,'history':history,'best':best,'discovery_observations':{k:asdict(v) for k,v in discovery_observations.items()},'candidate_origins':candidate_origins}
 (out/'report.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'status':report['status'],'evaluations':report['evaluations'],'history':history,'best_fitness':best['fitness']},indent=2))
if __name__=='__main__':run()
