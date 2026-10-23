"""GA6-H independent evolutionary scheduler. Diagnostic fitness adapters only.
Production certification requires a validated causal portfolio evaluator.
"""
import argparse, json, os, pickle, random, base64, hashlib, math
from dataclasses import asdict
from itertools import combinations
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from context_free_genome import Genome,random_genome
from genetic_operators import tree_crossover,structural_mutation

from discovery_fitness import OBJECTIVES,validate as validate_discovery,update_archive
def nondominated(records):
    """Maximize all objectives; deterministic NSGA-II style front ordering."""
    n=len(records);dominated=[[] for _ in records];counts=[0]*n;front=[[]]
    for i in range(n):
        a=records[i][1]
        for j in range(i+1,n):
            b=records[j][1]
            ab=all(a[k]>=b[k] for k in OBJECTIVES) and any(a[k]>b[k] for k in OBJECTIVES)
            ba=all(b[k]>=a[k] for k in OBJECTIVES) and any(b[k]>a[k] for k in OBJECTIVES)
            if ab:dominated[i].append(j);counts[j]+=1
            elif ba:dominated[j].append(i);counts[i]+=1
    front[0]=[i for i in range(n) if counts[i]==0]
    seen=sum(map(len,front))
    while seen<n:
        nxt=[]
        for i in front[-1]:
            for j in dominated[i]:
                counts[j]-=1
                if counts[j]==0:nxt.append(j)
        if not nxt:
            remaining=[i for i,c in enumerate(counts) if c>0]
            if not remaining:break
            nxt=remaining
        front.append(nxt);seen+=len(nxt)
    return front

def crowding(front,records):
    distance={i:0.0 for i in front}
    if len(front)<3:return {i:float('inf') for i in front}
    for k in OBJECTIVES:
        ordered=sorted(front,key=lambda i:(records[i][1][k],records[i][0].identity()))
        lo=records[ordered[0]][1][k];hi=records[ordered[-1]][1][k]
        distance[ordered[0]]=distance[ordered[-1]]=float('inf')
        if hi>lo:
            for j in range(1,len(ordered)-1):
                distance[ordered[j]]+=(records[ordered[j+1]][1][k]-records[ordered[j-1]][1][k])/(hi-lo)
    return distance

def rank_records(records):
    result=[]
    for rank,front in enumerate(nondominated(records)):
        distance=crowding(front,records)
        result.extend(sorted(front,key=lambda i:(-distance[i],records[i][0].identity())))
    return result

def population_leaf_diversity(members, max_pairs=1000):
    """Deterministic mean leaf-set Jaccard distance (bounded sample for runtime)."""
    from context_free_genome import validate_tree
    sets=[{(f,w,t,d) for f,w,t,d,_ in validate_tree(g.tree)} for g in members]
    pairs=list(combinations(range(len(sets)),2))
    if len(pairs)>max_pairs:
        step=len(pairs)/max_pairs
        pairs=[pairs[int(i*step)] for i in range(max_pairs)]
    return sum(1-len(sets[i]&sets[j])/len(sets[i]|sets[j]) for i,j in pairs)/len(pairs) if pairs else 0.0

def validate_metrics(metrics):
    return validate_discovery(metrics)

def diagnostic_evaluator(genome):
    """Deterministic infrastructure test only; NOT historical trading evidence."""
    genome.validate();leaves=len(genome.tree.get('children',[]))
    return {'net_ev':1/(1+abs(genome.hold_sessions-15)),
            'ev_per_session':1/(1+genome.hold_sessions),
            'reliability':1-genome.stop_loss,
            'training_consistency':1-genome.trailing_stop,
            'opportunity_coverage':leaves/8}

def evaluate_population(members,evaluator,workers=1):
    if workers==1:values=[evaluator(g) for g in members]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:values=list(pool.map(evaluator,members,chunksize=max(1,len(members)//(workers*4))))
    return [(g,validate_metrics(m)) for g,m in zip(members,values)]

def breed(records,population,rng,elite_fraction=.20):
    if population<4:raise ValueError('population must be >=4')
    order=rank_records(records);elite_count=max(2,int(population*elite_fraction))
    parents=[records[i][0] for i in order[:elite_count]]
    children=list(parents);identities={g.identity() for g in children}
    attempts=0
    while len(children)<population:
        attempts+=1
        if attempts>population*200:raise RuntimeError('novelty exhausted')
        roll=rng.random()
        if roll<.15:g=random_genome(rng)
        elif roll<.75:g=structural_mutation(tree_crossover(rng.choice(parents),rng.choice(parents),rng),rng)
        else:g=structural_mutation(rng.choice(parents),rng)
        identity=g.identity()
        if identity not in identities:children.append(g);identities.add(identity)
    return children

def encode_rng(rng):return base64.b64encode(pickle.dumps(rng.getstate())).decode()
def decode_rng(rng,s):rng.setstate(pickle.loads(base64.b64decode(s)))
def atomic_json(path,data):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,indent=2,sort_keys=True));os.replace(tmp,path)

def run(folder,population=100,generations=1000,seed=6106,workers=1,patience=100,evaluator=diagnostic_evaluator,evaluator_id='diagnostic_v1'):
    if population<4 or generations<1 or patience<1 or workers<1:raise ValueError('invalid budget')
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    checkpoint=folder/'checkpoint.json'
    config={'population':population,'seed':seed,'evaluator_id':evaluator_id,'objectives':OBJECTIVES}
    fingerprint=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
    rng=random.Random(seed)
    if checkpoint.exists():
        state=json.loads(checkpoint.read_text())
        if state['fingerprint']!=fingerprint:raise ValueError('resume fingerprint mismatch')
        decode_rng(rng,state['rng'])
        members=[Genome(**g) for g in state['members']]
        generation=state['generation'];archive=state['archive'];last_improvement=state['last_improvement']
    else:
        members=[];seen=set()
        while len(members)<population:
            g=random_genome(rng)
            if g.identity() not in seen:members.append(g);seen.add(g.identity())
        generation=0;archive=[];last_improvement=0
    while generation<generations and generation-last_improvement<patience:
        records=evaluate_population(members,evaluator,workers)
        order=rank_records(records)
        archive,improved=update_archive(archive,records)
        generation+=1
        if improved:last_improvement=generation
        summary={'generation':generation,'unique':len({g.identity() for g in members}),
                 'leaf_jaccard_diversity':population_leaf_diversity(members),
                 'pareto_front_size':len(nondominated(records)[0]),'archive_size':len(archive),'archive_improved':improved,
                 'stagnant_generations':generation-last_improvement,'leader':records[order[0]][0].identity(),
                 'mode':evaluator_id,'zero_trade_fraction':None,'mean_episodes':None,'mean_hold_sessions':None}
        atomic_json(folder/f'generation_{generation:04d}.json',summary)
        if generation<generations and generation-last_improvement<patience:members=breed(records,population,rng)
        atomic_json(checkpoint,{'fingerprint':fingerprint,'generation':generation,'members':[asdict(g) for g in members],
                               'rng':encode_rng(rng),'archive':archive,'last_improvement':last_improvement})
    result={'generation':generation,'stop_reason':'stagnation' if generation-last_improvement>=patience else 'generation_limit',
            'archive_size':len(archive),'mode':evaluator_id}
    atomic_json(folder/'result.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    p.add_argument('--population',type=int,default=100);p.add_argument('--generations',type=int,default=1000)
    p.add_argument('--workers',type=int,default=1);p.add_argument('--patience',type=int,default=100)
    a=p.parse_args()
    print(json.dumps(run(a.output,a.population,a.generations,workers=a.workers,patience=a.patience),indent=2))
