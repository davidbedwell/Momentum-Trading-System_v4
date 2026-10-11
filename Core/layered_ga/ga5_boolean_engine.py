"""Resumable isolated incremental grammar GA with explicit evaluation budget."""
import hashlib,json,os,pickle,random
from pathlib import Path
from .ga5_boolean_grammar import propose,mutate,combine,identity
from .stage2_nsga2_engine_v3 import Individual,environmental_selection

def atomic(path,obj):
    tmp=path.with_suffix('.tmp')
    with tmp.open('wb') as f:pickle.dump(obj,f,protocol=5);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def run(spaces,evaluate,*,arm,seed,population_size,generations,checkpoint_dir,run_identity,persist):
    if not run_identity or population_size<2 or generations<1:raise ValueError('Frozen budget required')
    directory=Path(checkpoint_dir);directory.mkdir(parents=True,exist_ok=True)
    config={'arm':arm,'seed':seed,'population_size':population_size,'generations':generations,'run_identity':run_identity,'engine':'GA5_BOOLEAN_ENGINE_V1'}
    h=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();cp=directory/'ga5_generation_state.pkl'
    if cp.exists():
        state=pickle.loads(cp.read_bytes())
        if state['config_hash']!=h:raise ValueError('Checkpoint identity mismatch')
        rng=random.Random();rng.setstate(state['rng_state']);population=state['population'];cache=state['cache'];ledger=state['ledger'];counter=state['counter'];start=state['next_generation']
    else:
        rng=random.Random(seed);population=[];cache={};ledger=[];counter=0;start=0
    def new(tree,parents,born):
        nonlocal counter
        counter+=1
        return {'id':f'c{counter:07d}','tree':tree,'parents':parents,'born':born}
    if not population:
        used=set()
        for _ in range(population_size):
            for attempt in range(4096):
                tree=propose(spaces,arm,rng);key=identity(tree,arm)
                if key not in used:break
            else:raise RuntimeError('Initialization novelty exhausted')
            used.add(key);population.append(new(tree,[],0))
    for generation in range(start,generations):
        missing={identity(p['tree'],arm):p['tree'] for p in population if identity(p['tree'],arm) not in cache}
        for key,tree in missing.items():
            curve,record=evaluate(tree)
            persist(record)
            cache[key]=curve
        if not any(any(__import__('math').isfinite(float(pt.get('ev_net',float('nan')))) for pt in curve.points) for curve in cache.values()):
            raise RuntimeError('Preflight failure: no valid finite fitness observations; refusing blind evolution')
        selected,_=environmental_selection([Individual({'expression':p['tree']},cache[identity(p['tree'],arm)],p['id']) for p in population],population_size)
        by_id={p['id']:p for p in population};survivors=[by_id[x.candidate_id] for x in selected]
        ledger.append({'generation':generation,'new_evaluations':len(missing),'unique_evaluations':len(cache),'selected':[x['id'] for x in survivors],'lineage':[{'child':p['id'],'parents':p['parents']} for p in population if p['born']==generation]})
        children=[]
        if generation<generations-1:
            seen={identity(p['tree'],arm) for p in population}
            for _ in range(population_size):
                a,b=rng.sample(survivors,2)
                for attempt in range(256):
                    tree=combine(a['tree'],b['tree'],spaces,arm,rng)
                    tree=mutate(tree,spaces,arm,rng)
                    key=identity(tree,arm)
                    if key not in seen and key not in cache:break
                else:raise RuntimeError('Offspring novelty exhausted')
                seen.add(key);children.append(new(tree,[a['id'],b['id']],generation+1))
        population=survivors+children
        atomic(cp,{'config_hash':h,'next_generation':generation+1,'population':population,'cache':cache,'ledger':ledger,'counter':counter,'rng_state':rng.getstate()})
    return {'generations_completed':len(ledger),'unique_evaluations':len(cache),'checkpoint':str(cp),'certified':False}
