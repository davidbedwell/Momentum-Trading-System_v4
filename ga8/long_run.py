"""Development-only, durable portfolio evolution. STOP file requests a clean stop."""
import argparse
import multiprocessing as mp
from functools import lru_cache
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import fcntl
import json
import os
from pathlib import Path
import random
import signal
import time
from .engine import FAMILIES, Gene, Manager, identity, load_panel, replay, rank, scores
from .run import RAW, seed_genes
from .phase_budget import phase_budget_due

PANEL = None
STOP = False

def atomic(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, allow_nan=False, indent=2) + '\n')
    tmp.replace(path)

def worker_init():
    global PANEL
    if PANEL is None:
        PANEL, _ = load_panel(RAW, end='2026-01-01')
    for value in vars(PANEL).values():
        for array in (value.values() if isinstance(value, dict) else [value]):
            if isinstance(array, np.ndarray):
                array.flags.writeable = False

@lru_cache(maxsize=16)
def cached_signal(gene):
    value=scores(PANEL,[gene])[0]
    value.flags.writeable=False
    return value

@lru_cache(maxsize=128)
def cached_replay(genes, manager, end):
    return replay(PANEL, genes, manager, '2022-01-01', end, signal=np.array([cached_signal(g) for g in genes]))

def evaluate(task):
    genes, manager, end = task
    genes = tuple(genes)
    result = cached_replay(genes, manager, end)
    audit=result['audit']
    if audit['max_identity_error']>1e-6 or audit['min_cash'] < -1e-6 or audit['max_total_risk'] > manager.risk_cap+1e-6:
        raise RuntimeError('Funded accounting or risk invariant failed')
    m = result['metrics']
    marginal = []
    for k in range(len(genes)):
        a = cached_replay(genes[:k]+genes[k+1:], manager, end)['metrics']
        marginal.append(dict(gene=k, delta_cagr=m['cagr']-a['cagr'],
                             delta_mdd=m['max_drawdown']-a['max_drawdown'],
                             incremental_nav=m['final_nav']-a['final_nav']))
    return dict(id=identity(genes, manager), genes=list(map(asdict, genes)), manager=asdict(manager),
                metrics=m, audit=result['audit'], marginal=marginal)

def decode(row):
    def tree(value):
        return tuple(tree(x) for x in value) if isinstance(value,list) else value
    return [Gene(**dict(g,entry_tree=tree(g.get('entry_tree',())))) for g in row['genes']], Manager(**row['manager'])

def dominates(a, b):
    # Feasible and infeasible archives are separate; all three funded objectives matter.
    av = (a['cagr'], -a['max_drawdown'], a['calmar'])
    bv = (b['cagr'], -b['max_drawdown'], b['calmar'])
    return all(x >= y for x,y in zip(av,bv)) and any(x > y for x,y in zip(av,bv))

def update_frontier(frontier, row, epsilon=1e-4):
    m = row['metrics']
    peers = [x for x in frontier if x['metrics']['feasible'] == m['feasible']]
    if any(x['id']==row['id'] or dominates(x['metrics'], m) or
           all(abs(x['metrics'][k]-m[k]) < epsilon for k in ('cagr','max_drawdown','calmar')) for x in peers):
        return frontier, False
    archive = [x for x in frontier if x not in peers or not dominates(m,x['metrics'])]+[row]
    # Keep objective extremes plus the best ranked representatives in each archive.
    bounded = []
    for feasible in (False, True):
        group = [x for x in archive if x['metrics']['feasible'] == feasible]
        extremes = [max(group, key=lambda x:x['metrics'][k]) for k in ('cagr','calmar')] if group else []
        if group:
            extremes.append(min(group,key=lambda x:x['metrics']['max_drawdown']))
        bounded.extend(list({x['id']:x for x in extremes+sorted(group,key=rank,reverse=True)}.values())[:128])
    return bounded, any(x['id']==row['id'] for x in bounded)

def material_pareto_improvement(frontier, reference):
    """Advance only on material feasible funded-Pareto progress, not archive churn.

    A new feasible solution must improve an existing reference point without
    materially worsening the other objectives. The reference is frozen at
    the last reset, so small cumulative improvements eventually count.
    """
    feasible=[r['metrics'] for r in frontier if r['metrics']['feasible']]
    if not feasible:
        return False
    if not reference:
        return True
    for m in feasible:
        for old in reference:
            if (m['cagr'] >= old['cagr']-0.001 and
                m['max_drawdown'] <= old['max_drawdown']+0.001 and
                m['calmar'] >= old['calmar']-0.05 and
                (m['cagr'] >= old['cagr']+0.005 or
                 m['max_drawdown'] <= old['max_drawdown']-0.005 or
                 m['calmar'] >= old['calmar']+0.25)):
                return True
    return False


def pareto_reference(frontier):
    return [dict(cagr=r['metrics']['cagr'],max_drawdown=r['metrics']['max_drawdown'],calmar=r['metrics']['calmar'])
            for r in frontier if r['metrics']['feasible']]

def offspring(rows, frontier, size, rng):
    ranked = sorted(rows, key=lambda x: rank(x), reverse=True)
    parents = list({x['id']:x for x in frontier + ranked[:max(4,size//4)]}.values())
    # Preserve frontier elites and representatives of each enabled family/niche.
    elites = ranked[:2]
    for predicate in ([lambda g,f=f:g.family==f for f in FAMILIES] +
                      [lambda g,n=n:g.niche==n for n in (-1,0,1,2)]):
        match = next((r for r in ranked if any(predicate(g) for g in decode(r)[0])), None)
        if match and match not in elites:
            elites.append(match)
    elites = list({identity(*decode(x)):x for x in elites}.values())
    result = [( *decode(x), [x['id']]) for x in elites[:size//2]]
    seen = {identity(g,m) for g,m,_ in result}
    while len(result)<size:
        a,b = rng.choice(parents),rng.choice(parents)
        genes, manager = decode(a)
        other,_ = decode(b)
        k = min(a['marginal'],key=lambda x:x['incremental_nav'])['gene'] if rng.random()<.7 else rng.randrange(len(genes))
        genes[k] = replace(other[k%len(other)], family=rng.choice(FAMILIES), second=rng.choice(FAMILIES),
            op=rng.choice(['single','and','or']), threshold=rng.uniform(-.2,.8), niche=rng.choice([-1,0,1,2]),
            hold_sessions=rng.choice([8,15,25,40,60]), weight=rng.choice([.04,.06,.08,.099]),
            trailing=rng.choice([.02,.03,.05,.08]), hold_family=rng.choice(FAMILIES), exit_family=rng.choice(FAMILIES),
            entry_tree=('and',rng.choice(FAMILIES),('or',rng.choice(FAMILIES),rng.choice(FAMILIES))) if rng.random()<.3 else ())
        manager=replace(manager,slots=rng.choice([5,7,10,15]),reserve=rng.choice([.1,.2,.35]),
                        correlation=rng.choice([.65,.8,.9]),replacement=rng.choice([.3,.7,1.]))
        if len(result)>=size* .9:  # independent immigrants, unrelated to selected parents
            genes=[Gene(rng.choice(FAMILIES),niche=rng.choice([-1,0,1,2]),threshold=rng.uniform(-.2,.8)) for _ in range(3)]
            manager=Manager()
        key=identity(genes,manager)
        if key not in seen:
            result.append((genes,manager,[a['id'],b['id']]))
            seen.add(key)
    return result

def next_phase_population(journal, forward_file, phase, size, rng):
    """Use only prior-year forward survivors as inherited parents."""
    from .forward_catalog import catalog
    records=[json.loads(line) for line in Path(forward_file).open()]
    qualified=[r for r in records if r['forward_feasible']]
    qualified.sort(key=lambda r:r['forward_metrics']['cagr'],reverse=True)
    source={r['id']:r for r in catalog(journal,phase)}
    qualified=[r for r in qualified if r['id'] in source]
    population=[]
    seen=set()
    def add(g,m,parents):
        key=identity(g,m)
        if key in seen:return
        seen.add(key)
        population.append(dict(genes=list(map(asdict,g)),manager=asdict(m),parents=parents))
    inherited=round(size*.2) if qualified else 0
    for r in qualified[:inherited]:
        g,m=decode(source[r['id']])
        add(g,m,[r['id']])
    attempts=0
    while len(population)<inherited:
        attempts+=1
        if attempts>size*100:raise RuntimeError('Unable to seed survivor descendants')
        r=qualified[(attempts-1)%len(qualified)]
        g,m=decode(source[r['id']])
        j=rng.randrange(len(g))
        g[j]=replace(g[j],threshold=max(-.2,min(.8,g[j].threshold+rng.uniform(-.2,.2))),
                     family=rng.choice(FAMILIES) if rng.random()<.25 else g[j].family,
                     niche=rng.choice([-1,0,1,2]) if rng.random()<.2 else g[j].niche)
        m=replace(m,reserve=rng.choice([.1,.2,.35]) if rng.random()<.3 else m.reserve)
        add(g,m,[r['id']])
    base=seed_genes()
    while len(population)<size:
        g=[replace(x,family=rng.choice(FAMILIES),niche=rng.choice([-1,0,1,2]),
                   threshold=rng.uniform(-.2,.8),hold_sessions=rng.choice([8,15,25,40,60]),
                   weight=rng.choice([.04,.06,.08,.099]),trailing=rng.choice([.02,.03,.05,.08])) for x in base]
        m=Manager(slots=rng.choice([5,7,10,15]),reserve=rng.choice([.1,.2,.35]),
                  correlation=rng.choice([.65,.8,.9]))
        add(g,m,[])
    return population

def population_size(initial, progress, stagnant, diversity):
    # Preserve full discovery diversity throughout the final chronological phase.
    if progress >= .439:
        return initial
    factor = 1. if progress < .2 else 1.-.4*min(1.,(progress-.2)/.4) if progress < .6 else .6-.25*min(1.,(progress-.6)/.4)
    if stagnant >= 20 or diversity < .8:
        factor=min(1.,factor+.1)
    return max(24,round(initial*factor))

def stop_signal(*_):
    global STOP
    STOP=True

def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--output',required=True)
    parser.add_argument('--generations',type=int,default=1000)
    parser.add_argument('--population',type=int,default=500)
    profile_path=Path(__file__).with_name('runtime_profile.json')
    profile=json.loads(profile_path.read_text()) if profile_path.exists() else {}
    parser.add_argument('--workers',type=int,default=profile.get('workers',4))
    parser.add_argument('--budget-hours',type=float,default=72)
    parser.add_argument('--seed',type=int,default=80079)
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    if not (3<=args.generations<=1000 and 24<=args.population<=500 and 1<=args.workers<=16 and 0<args.budget_hours<=168):
        parser.error('Require generations 3..1000, population 24..500, workers 1..16, budget 0..168 hours')
    out=Path(args.output)
    out.mkdir(parents=True,exist_ok=True)
    lock=(out/'run.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
    checkpoint=out/'checkpoint.json'
    if checkpoint.exists() and not args.resume:
        parser.error('Existing run requires --resume')
    signal.signal(signal.SIGTERM,stop_signal)
    signal.signal(signal.SIGINT,stop_signal)
    rng=random.Random(args.seed)
    source_hash=hashlib.sha256(RAW.read_bytes()).hexdigest()
    code_hash=hashlib.sha256(Path(__file__).read_bytes()+Path(__file__).with_name('engine.py').read_bytes()+Path(__file__).with_name('resources.py').read_bytes()).hexdigest()
    config=dict(code_sha256=code_hash,population=args.population,seed=args.seed,generations=args.generations,source_sha256=source_hash,
                generation_budget_scope='1000 maximum total across chronological phases',holdout_excluded='date < 2026-01-01 before features/audit; no final holdout replay',epsilon=1e-4)
    state=dict(config=config,phase=0,generation=0,total_generation=0,phase_cap=max(1,args.generations//3),stagnant=0,best_rank_seen=None,pareto_reference=[],frontier=[],rows=[],population=[],folds=[],evaluations=0,elapsed=0.)
    if args.resume:
        state=json.loads(checkpoint.read_text())
        if state['config']!=config:
            parser.error('Resume config/data mismatch')
        def tuples(x):
            return tuple(map(tuples,x)) if isinstance(x,list) else x
        rng.setstate(tuples(state['rng']))
    else:
        atomic(out/'config.json',dict(config,workers=args.workers,budget_hours=args.budget_hours))
    with (out/'runs.jsonl').open('a') as journal:
        journal.write(json.dumps(dict(started_utc=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),args=vars(args),config=config))+'\n')
    started=time.monotonic()
    prior_elapsed=state['elapsed']
    stopped=None
    phases=[('2023-01-01','2024-01-01'),('2024-01-01','2025-01-01'),('2025-01-01','2026-01-01')]
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
        os.environ[name] = '1'
    worker_init()
    from threadpoolctl import threadpool_limits
    threadpool_limits(1)
    from .resources import Monitor
    monitor = Monitor()
    state['rng']=rng.getstate()
    atomic(checkpoint,state)
    monitor.start()
    # Conservative startup cap until measured worker peaks are available.
    worker_bytes = max(profile.get('worker_peak_bytes',512*1024**2)*1.5, sum(a.nbytes for a in PANEL.features.values())*8)
    args.workers=min(args.workers,max(1,int((monitor.limit-monitor.snapshot()['peak_pss_bytes'])/worker_bytes)))
    with ProcessPoolExecutor(args.workers,initializer=worker_init,mp_context=mp.get_context('fork')) as pool:
        while state['phase']<len(phases):
            end,test_end=phases[state['phase']]
            if args.generations//3+(state['phase'] < args.generations%3)==0:
                break
            if not state['population']:
                base=seed_genes()
                initial=[]
                for i in range(args.population):
                    genes=list(base)
                    genes[i%3]=replace(genes[i%3],family=FAMILIES[i%len(FAMILIES)],niche=i%4-1,threshold=rng.uniform(-.1,.7))
                    initial.append(dict(genes=list(map(asdict,genes)),manager=asdict(Manager(slots=rng.choice([5,7,10]),reserve=rng.choice([.1,.2,.35]))),parents=[]))
                state['population']=initial
            if monitor.exceeded or STOP or (out/'STOP').exists() or prior_elapsed+time.monotonic()-started>=args.budget_hours*3600:
                stopped='memory_limit' if monitor.exceeded else 'explicit_stop' if STOP or (out/'STOP').exists() else 'wall_budget'
                break
            t=time.monotonic()
            tasks=[(*decode(r),end) for r in state['population']]
            rows=[]
            for offset in range(0,len(tasks),args.workers*4):
                if monitor.exceeded or STOP or (out/'STOP').exists():
                    break
                rows.extend(pool.map(evaluate,tasks[offset:offset+args.workers*4],chunksize=4))
            if len(rows)!=len(tasks):
                stopped='memory_limit' if monitor.exceeded else 'explicit_stop'
                state['rng']=rng.getstate()
                atomic(checkpoint,state)
                break
            improved=False
            for row,parent in zip(rows,state['population']):
                row.update(parents=parent['parents'],generation=state['generation']+1,phase=state['phase'])
                state['frontier'],change=update_frontier(state['frontier'],row)
                improved |= change
            # Material funded-Pareto progress across CAGR, MDD and Calmar.
            meaningful=material_pareto_improvement(state['frontier'],state.get('pareto_reference',[]))
            if meaningful:
                state['pareto_reference']=pareto_reference(state['frontier'])
                state['best_rank_seen']=max((m['cagr'] for m in state['pareto_reference']),default=None)
            # Stagnation tracks improvement of the leading funded feasible portfolio,
            # independently of diversity and secondary Pareto-frontier movement.
            feasible_now=[r for r in state['frontier'] if r['metrics']['feasible']]
            leader_now=max(feasible_now,key=rank) if feasible_now else None
            previous_leader=state.get('stagnation_leader')
            leader_improved=False
            if leader_now is not None:
                m=leader_now['metrics']
                if previous_leader is None:
                    leader_improved=True
                elif leader_now['id'] != previous_leader['id']:
                    old=previous_leader['metrics']
                    leader_improved=(m['cagr'] >= old['cagr']+0.005 and
                                     m['max_drawdown'] <= old['max_drawdown']+0.001 and
                                     m['calmar'] >= old['calmar']-0.05)
                if leader_improved:
                    state['stagnation_leader']={'id':leader_now['id'],'metrics':{
                        k:m[k] for k in ('cagr','max_drawdown','calmar')}}
            state['frontier_stagnant']=0 if meaningful else state.get('frontier_stagnant',0)+1
            state['stagnant']=0 if leader_improved else state['stagnant']+1
            state['generation']+=1
            state['total_generation']+=1
            state['evaluations']+=sum(1+len(r['genes']) for r in rows)
            state['rows']=rows
            state['elapsed']=prior_elapsed+time.monotonic()-started
            feasible=[r for r in state['frontier'] if r['metrics']['feasible']]
            best=max(feasible or state['frontier'],key=lambda r:rank(r))
            seconds=time.monotonic()-t
            remaining=max(0,args.generations-state['total_generation'])
            phase_remaining=max(0,state['phase_cap']-state['generation'])
            later=remaining-phase_remaining
            later_weights=sum(range(state['phase']+2,4))/max(1,2-state['phase'])
            eta=seconds/(state['phase']+1)*(phase_remaining*(state['phase']+1)+later*later_weights)
            status=dict(stage='RUNNING',pid=os.getpid(),updated_utc=datetime.now(timezone.utc).isoformat(),
                phase=state['phase'],train_end=end,generation=state['total_generation'],fold_generation=state['generation'],fold_generation_cap=state['phase_cap'],generations_since_meaningful_portfolio_improvement=state['stagnant'],generations_since_frontier_improvement=state.get('frontier_stagnant',0),
                best_feasible_portfolio=max(feasible,key=lambda r:rank(r)) if feasible else None,
                workers=args.workers,disk_bytes=sum(p.stat().st_size for p in out.iterdir() if p.is_file()),resources=monitor.snapshot(),frontier=state['frontier'],population=len(rows),unique_genomes=len({r['id'] for r in rows}),
                family_coverage=sorted({g['family'] for r in rows for g in r['genes']}),
                niche_coverage=sorted({g['niche'] for r in rows for g in r['genes']}),
                seconds_per_generation=seconds,throughput_evaluations_per_second=sum(1+len(r['genes']) for r in rows)/seconds,
                eta_seconds=eta,eta_basis='measured generation time scaled by training years across remaining global budget; stagnation may stop earlier',
                elapsed_seconds=state['elapsed'],folds=state['folds'],holdout_accessed=False)
            with (out/'generations.jsonl').open('a') as log:
                log.write(json.dumps(dict(status,rows=rows))+'\n')
            # Persist every evaluated chromosome, not just Pareto survivors.
            from .chromosome_catalog import connect, record
            with connect(out/'chromosome_library.sqlite') as catalog_db:
                record(catalog_db,rows,state['phase'],state['generation'])
            progress=(sum(f['generations'] for f in state['folds'])+state['generation'])/args.generations
            target=population_size(args.population,progress,state['stagnant'],len({r['id'] for r in rows})/len(rows))
            next_pop=offspring(rows,state['frontier'],target,rng)
            state['rows']=[]
            state['population']=[dict(genes=list(map(asdict,g)),manager=asdict(m),parents=p) for g,m,p in next_pop]
            state['rng']=rng.getstate()
            atomic(checkpoint,state)
            atomic(out/'status.json',status)
            if state['total_generation']==500:
                atomic(out/f'checkpoint_phase{state["phase"]}_generation500.json',state)
            print(json.dumps({k:status[k] for k in ('phase','generation','seconds_per_generation','eta_seconds','generations_since_frontier_improvement')}),flush=True)
            if state['generation']>=state['phase_cap'] or state['stagnant']>=100 or phase_budget_due(state['phase'],state['elapsed'],args.budget_hours*3600,state['generation']):
                # Frozen winner evaluated on the next development year only; no feedback to search.
                g,m=decode(best)
                result=replay(PANEL,g,m,end,test_end,True)
                atomic(out/f'fold_{end[:4]}.json',dict(model=best,result=result))
                # Independent forward evidence for every distinct qualifying chromosome.
                # Read-only observational catalog: never fed into evolution.
                from .forward_catalog import forward_all
                forward_summary=forward_all(PANEL,out/'generations.jsonl',state['phase'],end,test_end,out/f'forward_{end[:4]}.jsonl')
                state['folds'].append(dict(train_end=end,test_end=test_end,metrics=result['metrics'],model_id=best['id'],
                    forward_eligible=forward_summary['eligible'],forward_tested=forward_summary['tested'],generations=state['generation'],stop_reason='portfolio_stagnation' if state['stagnant']>=100 else 'generation_cap' if state['generation']>=state['phase_cap'] else 'reserved_wall_budget'))
                next_population=next_phase_population(out/'generations.jsonl',out/f'forward_{end[:4]}.jsonl',state['phase'],args.population,rng)
                atomic(out/f'phase{state["phase"]+1}_parent_selection.json',dict(
                    forward_year=end[:4],forward_survivors=forward_summary['forward_qualifying'],
                    inherited=sum(bool(x['parents']) for x in next_population),
                    independent=sum(not x['parents'] for x in next_population),
                    parent_ids=sorted({i for x in next_population for i in x['parents']})))
                state.update(phase=state['phase']+1,generation=0,stagnant=0,frontier_stagnant=0,stagnation_leader=None,best_rank_seen=None,pareto_reference=[],frontier=[],rows=[],population=next_population)
                state['rng']=rng.getstate()
                state['phase_cap']=max(1,(args.generations-state['total_generation'])//max(1,3-state['phase']))
                atomic(checkpoint,state)
                if state['total_generation']>=args.generations:
                    break
        status=json.loads((out/'status.json').read_text()) if (out/'status.json').exists() else {}
        status.update(stage='STOPPED' if stopped else 'COMPLETE',stop_reason=stopped or 'all_development_folds_complete',folds=state['folds'],eta_seconds=None if stopped else 0)
        atomic(out/'status.json',status)
    monitor.closed=True

if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        import sys
        if '--output' in sys.argv:
            output=Path(sys.argv[sys.argv.index('--output')+1])
            if output.exists():
                atomic(output/'failure.json',dict(stage='FAILED',error=repr(exc),pid=os.getpid(),updated_utc=datetime.now(timezone.utc).isoformat()))
        raise
