"""Research-only Pareto-guided parent selection with niche quotas and crowding."""
from collections import Counter
from math import isfinite
from dataclasses import replace
from ga5_chromosome_contract import crossover,mutate
from evolution_controls import diversity,gene_signature
from optimizer_v3 import NICHES

KEYS=('target_success_gt5','win_rate','adverse_excursion','tail_loss')
def objective(item):
 _,g,r=item;s=r.get('shadow',{});e=r.get('exit_objectives',{})
 n=int(s.get('closed_trades') or 0)
 if n<50 or (s.get('mean_net_return') or 0)<=0:return None
 vals=(s.get('success_gt5_rate'),s.get('win_rate'),e.get('adverse'),e.get('tail'))
 if any(v is None or not isfinite(float(v)) for v in vals):return None
 return tuple(float(v) for v in vals)
def ranks_and_crowding(scored):
 vals=[objective(x) for x in scored]
 valid=[i for i,v in enumerate(vals) if v is not None]
 dominates=[[] for _ in scored];n=[0]*len(scored);front=[i for i in valid if True]
 for i in valid:
  for j in valid:
   if i==j:continue
   a,b=vals[i],vals[j]
   if all(x>=y for x,y in zip(a,b)) and any(x>y for x,y in zip(a,b)):dominates[i].append(j)
   elif all(x<=y for x,y in zip(a,b)) and any(x<y for x,y in zip(a,b)):n[i]+=1
 fronts=[];cur=[i for i in valid if n[i]==0]
 while cur:
  fronts.append(cur);nxt=[]
  for i in cur:
   for j in dominates[i]:
    n[j]-=1
    if n[j]==0:nxt.append(j)
  cur=nxt
 rank={};crowd={}
 for level,f in enumerate(fronts):
  for i in f:rank[i]=level;crowd[i]=0.
  for k in range(len(KEYS)):
   ordered=sorted(f,key=lambda i:vals[i][k]);lo=vals[ordered[0]][k];hi=vals[ordered[-1]][k]
   crowd[ordered[0]]=float('inf');crowd[ordered[-1]]=float('inf')
   if hi>lo:
    for z in range(1,len(ordered)-1):crowd[ordered[z]]+=(vals[ordered[z+1]][k]-vals[ordered[z-1]][k])/(hi-lo)
 return rank,crowd,len(valid),len(fronts)
def breed_pareto(scored,rng,population):
 if population<2*len(NICHES):raise ValueError('Population too small')
 rank,crowd,valid,front_count=ranks_and_crowding(scored)
 indexed=list(enumerate(scored))
 ordered=sorted(indexed,key=lambda x:(rank.get(x[0],10**6),-crowd.get(x[0],0),-x[1][0],x[1][1].identity()))
 by={n:[x for x in ordered if x[1][1].niche==n] for n in NICHES}
 if any(not v for v in by.values()):raise ValueError('Missing niche')
 out=[];seen=set();sig=Counter()
 def add(g):
  if not g.valid() or g.identity() in seen:return False
  out.append(g);seen.add(g.identity());sig[gene_signature(g)]+=1;return True
 for niche in NICHES:add(by[niche][0][1][1])
 minimum=max(2,population//(len(NICHES)*5))
 for niche in NICHES:
  tries=0
  while sum(g.niche==niche for g in out)<minimum:
   tries+=1
   if tries>20000:raise RuntimeError('Niche quota failed')
   pool=by[niche][:max(1,len(by[niche])//3)]
   a=rng.choice(pool)[1][1];b=rng.choice(pool)[1][1]
   add(mutate(crossover(a,b,rng),rng))
 elite_limit=min(population//5,population-len(out));kept=0
 for i,(score,g,r) in ordered:
  if kept>=elite_limit:break
  if add(g):kept+=1
 # 80% Pareto-guided selection; 20% unrestricted exploration.
 guided=[x[1][1] for x in ordered[:max(len(NICHES),population//2)]]
 allparents=[x[1][1] for x in ordered]
 attempts=0
 while len(out)<population:
  attempts+=1
  if attempts>population*2000:raise RuntimeError('Unique offspring exhausted')
  niche=min(NICHES,key=lambda x:sum(g.niche==x for g in out)) if rng.random()<.3 else rng.choice(NICHES)
  pool=by[niche][:max(1,len(by[niche])//2)]
  a=rng.choice(pool)[1][1]
  b=rng.choice(guided if rng.random()<.8 else allparents)
  child=mutate(crossover(a,replace(b,niche=a.niche),rng),rng)
  if sig[gene_signature(child)]>=max(3,population//20) and rng.random()<.9:continue
  add(child)
 stats=diversity(out)
 if stats['unique_chromosomes']!=population or stats['niches_represented']!=len(NICHES):raise RuntimeError('Diversity invariant failed')
 stats.update({'pareto_evidence_eligible':valid,'pareto_fronts':front_count,'selection':'pareto_crowding_with_niche_quotas','guided_parent_probability':.8})
 return out,stats
