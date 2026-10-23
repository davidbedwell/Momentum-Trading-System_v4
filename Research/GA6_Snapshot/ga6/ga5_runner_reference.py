"""Unrestricted GA5 population runner, guarded research only.
All seven historical seeds share one breeding pool; labels are provenance.
"""
import argparse,base64,hashlib,json,pickle,random,sys,time,os,math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from dataclasses import asdict
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from niche_seeds import initial
from optimizer_v3 import NICHES
from fitness_niche_loss_control import fitness
from unified_evolution import breed
from evolution_controls import breed_next,diversity
from pareto_trade_objectives import breed_pareto
from ga5_chromosome_contract import Genome
from canonical_engine import ResultCache,digest_file
from guarded_evaluator_niche_single_exit import evaluate,PreparedSessions
from runner_v4 import engine_fingerprint
from exit_objectives import pareto_front

_WORKER_PREPARED=None
_WORKER_POLICY=None

def _worker_init(frame,blocked,membership,veto,cash_yield,niche_labels,entry_mode):
 global _WORKER_PREPARED,_WORKER_POLICY
 _WORKER_PREPARED=frame if isinstance(frame,PreparedSessions) else PreparedSessions(frame)
 _WORKER_POLICY=(blocked,membership,veto,cash_yield,niche_labels if entry_mode=="origin" else None)

def _worker_evaluate(genome):
 blocked,membership,veto,cash_yield,niche_labels=_WORKER_POLICY
 return evaluate(_WORKER_PREPARED,genome,blocked=blocked,membership=membership,risk_veto=veto,annual_cash_yield=cash_yield,niche_labels=niche_labels)

def run(argv=None):
 p=argparse.ArgumentParser()
 for arg in ('features','policy-file','output'):p.add_argument('--'+arg,required=True)
 p.add_argument('--generations',type=int,default=1)
 p.add_argument('--population',type=int,default=28)
 p.add_argument('--workers',type=int,default=min(8,len(os.sched_getaffinity(0))))
 p.add_argument('--diagnostic-only',action='store_true')
 p.add_argument('--stagnation',type=int,default=100)
 p.add_argument('--entry-mode',choices=('origin','unrestricted'),default='origin')
 a=p.parse_args(argv)
 if not a.diagnostic_only:raise ValueError('Research-only; explicit diagnostic flag required')
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
 labels_path=Path(__file__).with_name("dev79_niche_ga_v1")/"labels.parquet"
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
 code=hashlib.sha256((engine_fingerprint()+digest_file(Path(__file__))+digest_file(Path(__file__).with_name('unified_evolution.py'))+digest_file(Path(__file__).with_name('evolution_controls.py'))+digest_file(Path(__file__).with_name('pareto_trade_objectives.py'))+digest_file(Path(__file__).with_name('optimizer_v3.py'))+digest_file(Path(__file__).with_name('niche_seeds.py'))+digest_file(Path(__file__).with_name('exit_objectives.py'))+digest_file(Path(__file__).with_name('guarded_evaluator_niche_single_exit.py'))+digest_file(Path(__file__).with_name('shadow_niche_single_exit.py'))+digest_file(Path(__file__).with_name('fitness_niche_loss_control.py'))+digest_file(Path(__file__).with_name('shadow_signals.py'))+digest_file(Path(__file__).parent.parent/'ga5_chromosome_contract.py')+digest_file(labels_path)+a.entry_mode).encode()).hexdigest()
 data=digest_file(source);policy_hash=digest_file(Path(a.policy_file))
 rng=random.Random(1700);cache=ResultCache(out/'evaluations.sqlite')
 seed_members=[initial(n) for n in NICHES]
 members,_=breed_next([(0.0,g,{}) for g in seed_members],rng,a.population)
 best=None;history=[]
 checkpoint=out/'checkpoint_unified.json'
 ledger=out/'all_evaluations.jsonl'
 start=0
 if checkpoint.exists():
  state=json.loads(checkpoint.read_text())
  if (state['data'],state['policy'],state['code'],state['population'])!=(data,policy_hash,code,a.population):raise ValueError('Checkpoint fingerprint mismatch')
  start=state['generation'];rng.setstate(pickle.loads(base64.b64decode(state['rng'])))
  members=[Genome(**g) for g in state['members']];history=state['history']
  if state['best']:best=state['best']
 try:
  with ProcessPoolExecutor(max_workers=a.workers,initializer=_worker_init,initargs=(prepared,blocked,membership,veto,policy['cash_proxy_annual_yield'],niche_labels,a.entry_mode)) as pool:
   for generation in __import__("itertools").count(start):
    if a.generations and generation>=a.generations:break
    scored=[];missing=[]
    for genome in members:
     key=cache.key(genome,data,'DEV79_FULL','unified:'+policy_hash+':'+code)
     result=cache.get(key)
     if result is None:missing.append((genome,key))
     else:scored.append((fitness(result),genome,result))
    if missing:
     for (genome,key),result in zip(missing,pool.map(_worker_evaluate,[g for g,_ in missing])):
      cache.put(key,result)
      scored.append((fitness(result),genome,result))
    scored.sort(key=lambda v:(-v[0],v[1].identity()))
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
    eligible=[item for item in scored if item[2]['exit_objectives']['count']>=20]
    front=pareto_front([item[2]['exit_objectives'] for item in eligible])
    # Rank nondominated candidates by independently measured portfolio fitness;
    # do not privilege arbitrary ordering from the Pareto implementation.
    pareto_elites=sorted((eligible[i] for i in front),key=lambda item:(-item[0],item[1].identity()))
    parent_count=max(2,a.population//4)
    parents=[g for _,g,_ in pareto_elites[:parent_count]]
    parents.extend(g for _,g,_ in scored if g.identity() not in {x.identity() for x in parents})
    parents=parents[:parent_count]
    history[-1]['niche_counts']={n:sum(g.niche==n for _,g,_ in scored) for n in NICHES}
    history[-1]['distinct_gene_patterns']=len({(g.entry_feature,g.exit_feature,g.hold_feature,g.regime_feature,g.sizing_feature,g.replace_feature) for _,g,_ in scored})
    history[-1]['fitness_mean']=sum(v[0] for v in scored)/len(scored)
    history[-1]['fitness_median']=sorted(v[0] for v in scored)[len(scored)//2]
    history[-1]['best_ever_fitness']=best['fitness']
    history[-1]['exit_pareto_count']=len(front)
    history[-1]['exit_metric_eligible']=len(eligible)
    members,offspring_diversity=breed_pareto(scored,rng,a.population)
    history[-1]["next_population_diversity"]=offspring_diversity
    state={'data':data,'policy':policy_hash,'code':code,'population':a.population,'generation':generation+1,'rng':base64.b64encode(pickle.dumps(rng.getstate())).decode(),'members':[asdict(g) for g in members],'history':history,'best':best}
    tmp=checkpoint.with_suffix('.tmp');tmp.write_text(json.dumps(state));tmp.replace(checkpoint)
    print(json.dumps({"generation":generation+1,"best":best["fitness"],"niches":history[-1]["niches_represented"],"gene_patterns":history[-1]["distinct_gene_patterns"]}),flush=True)
    if len(history)>=a.stagnation+1 and max(h["best_ever_fitness"] for h in history[-a.stagnation:])<=history[-a.stagnation-1]["best_ever_fitness"]+1e-8:
     print("STAGNATION_STOP",generation+1,flush=True);break
 finally:cache.close()
 report={'status':'DIAGNOSTIC_ONLY','architecture':'niche-protected evolutionary population','entry_mode':a.entry_mode,'research_validity':'NICHE_ENTRY_HOLD_EXIT_SINGLE_TRADE_RETROSPECTIVE_NOT_OOS','evaluations':len(history)*a.population,'history':history,'best':best}
 (out/'report.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'status':report['status'],'evaluations':report['evaluations'],'history':history,'best_fitness':best['fitness']},indent=2))
if __name__=='__main__':run()
