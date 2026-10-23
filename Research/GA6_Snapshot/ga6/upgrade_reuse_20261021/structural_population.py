"""Evolve executable grouped entry trees while retaining the full GA6 Genome."""
from collections import defaultdict
from copy import deepcopy
from dataclasses import replace
from scipy.stats import qmc
from ga5_feature_families import FAMILIES
from ga5_chromosome_contract import mutate,crossover
from ga5_redesign.optimizer_v3 import NICHES
from ga6.upgrade_reuse_20261021.structural_candidate import StructuralCandidate
from ga6.upgrade_reuse_20261021.discovery_allocation import allocate

def leaves(node):
 if 'family' in node:return [node]
 return [leaf for child in node['children'] for leaf in leaves(child)]

def random_tree(rng,activity='new_structures',parent=None,sobol_index=None):
 if activity=='sobol_refinement' and parent is not None:
  tree=deepcopy(parent)
  nodes=leaves(tree)
  sampler=qmc.Sobol(d=len(nodes),scramble=True,seed=6106)
  if sobol_index is not None and sobol_index>0:
   sampler.fast_forward(sobol_index)
  point=sampler.random(1)[0]
  for leaf,value in zip(nodes,point):
   leaf['threshold']=round(float(2*value-1),6)
  return tree
 n=rng.randint(2,min(8,len(FAMILIES)))
 families=rng.sample(list(FAMILIES),n)
 def leaf(f):return {'family':f,'threshold':round(rng.uniform(-1,1),6),'comparison':rng.choice(('>=','<='))}
 if activity=='new_structures' and n>=4 and rng.random()<.5:
  pivot=rng.randint(2,n-2)
  return {'op':rng.choice(('AND','OR')),'children':[{'op':rng.choice(('AND','OR')),'children':[leaf(f) for f in families[:pivot]]},{'op':rng.choice(('AND','OR')),'children':[leaf(f) for f in families[pivot:]]}]}
 return {'op':rng.choice(('AND','OR')),'children':[leaf(f) for f in families]}

def propose_structural(scored,rng,population=400,generation=0,observations=None):
 if not scored:raise ValueError('Missing evaluated structural parents')
 by_niche=defaultdict(list)
 for score,c,result in sorted(scored,key=lambda x:-x[0]):by_niche[c.genome.niche].append(c)
 if any(not by_niche[n] for n in NICHES):raise ValueError('Missing protected niche')
 out=[];seen=set();origins=[]
 def add(c,activity):
  if c.identity() in seen:return False
  seen.add(c.identity());out.append(c);origins.append(activity);return True
 for n in NICHES:
  for c in by_niche[n][:10]:add(c,'protected_niche')
 if len(out)>population:raise ValueError('Protected elites exceed budget')
 remaining=population-len(out)
 targets=allocate(observations,remaining,generation) if remaining>=4 else {a:0 for a in allocate()}
 for activity,target in targets.items():
  count=0
  for attempt in range(max(500,target*150)):
   if count>=target:break
   niche=NICHES[(generation+attempt+len(out))%len(NICHES)]
   parents=by_niche[niche][:20];parent=rng.choice(parents)
   if activity=='new_structures':
    genome=parent.genome;tree=random_tree(rng,activity)
   elif activity=='sobol_refinement':
    genome=parent.genome;tree=random_tree(rng,activity,parent.entry_tree,sobol_index=generation*10000+attempt)
   elif activity=='evolution':
    other=rng.choice(parents)
    genome=mutate(crossover(parent.genome,other.genome,rng),rng)
    tree=deepcopy(rng.choice((parent.entry_tree,other.entry_tree)))
    tree=random_tree(rng,'sobol_refinement',tree,sobol_index=generation*10000+attempt)
   else:
    genome=mutate(parent.genome,rng)
    tree=random_tree(rng,activity)
   if add(StructuralCandidate(genome,tree),activity):count+=1
  if count<target:raise RuntimeError('Structural novelty exhausted: '+activity)
 return out,{'origins':origins,'counts':{a:origins.count(a) for a in set(origins)},'niches':len({c.genome.niche for c in out})}
