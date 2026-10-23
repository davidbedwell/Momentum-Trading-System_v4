"""Research-only candidate policy scoring, independent of evolved GA5 genomes."""
from statistics import mean
from ga6.prospective_replay import simulate
from ga6.policy_genes import fresh,mutate

def evaluate_policy(paths,genes,fee=.001,cash_daily=0.):
 reports=[simulate(p,genes.policy(),fee,cash_daily) for p in paths if len(p)>=3]
 if not reports:return {'eligible':False,'score':-1e9,'count':0}
 deltas=[x['incremental_net'] for x in reports]
 tail=mean(sorted(deltas)[:max(1,len(deltas)//20)])
 win=sum(x>0 for x in deltas)/len(deltas)
 score=100*mean(deltas)+20*tail
 return {'eligible':len(reports)>=50,'score':score if len(reports)>=50 else -1e6+len(reports),'count':len(reports),'mean_incremental':mean(deltas),'tail_incremental':tail,'beneficial_fraction':win,'mean_policy_net':mean(x['policy_net'] for x in reports),'mean_hold_net':mean(x['hold_net'] for x in reports)}

def evolve(paths,rng,population=32,generations=5):
 if population<4:raise ValueError('small population')
 members=[fresh(rng) for _ in range(population)];history=[]
 score_cache={}
 for generation in range(generations):
  scored=[]
  for g in members:
   key=tuple(sorted(g.__dict__.items()))
   if key not in score_cache:score_cache[key]=evaluate_policy(paths,g)
   scored.append((score_cache[key],g))
  scored.sort(key=lambda x:-x[0]['score'])
  history.append({'generation':generation+1,'best':scored[0][0],'genes':scored[0][1].__dict__})
  parents=[g for _,g in scored[:max(2,population//4)]]
  members=parents[:]
  while len(members)<population:members.append(mutate(rng.choice(parents),rng))
 return history
