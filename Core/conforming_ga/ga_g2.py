"""Deterministic nine-island production GA controller for MTS-GA-G2."""
from __future__ import annotations
from pathlib import Path
from multiprocessing import get_context
import hashlib,os,pickle
import numpy as np
from .g2schema import genome_hash,canonical
from .g2evolution import initial_population_g2,mutate_g2,crossover_g2,assign_species
from .ga import DD_BANDS,ISLANDS,POPULATION_SIZE,BASE_GENERATIONS,MIGRATION_INTERVAL,CHECKPOINT_INTERVAL
from .evolution import MAP_DESCRIPTOR_NAMES,deterministic_seed,stage_for_generation

_EVAL=None
def _worker(x):
    island,idx,g=x
    m=dict(_EVAL(g));m["_worker_pid"]=os.getpid()
    return island,idx,g,m

def dominates(a,b):
    return a["cagr"]>=b["cagr"] and a["mdd"]>=b["mdd"] and (a["cagr"]>b["cagr"] or a["mdd"]>b["mdd"])

def pareto(scored):
    return [x for x in scored if not any(dominates(y[1],x[1]) for y in scored if y is not x)]

def hypervolume(scored,ref=(-1.0,-1.0)):
    """Exact 2D dominated area for maximize(CAGR,signed-MDD)."""
    pts=sorted({(max(ref[0],float(m["cagr"])),max(ref[1],float(m["mdd"]))) for _,m in pareto(scored)})
    hv=0.0;best_y=ref[1]
    for x,y in pts:
        if y>best_y:hv+=(x-ref[0])*(y-best_y);best_y=y
    return float(max(hv,0.0))

def _behavior(m):return np.array([float(m.get(k,0.0)) for k in MAP_DESCRIPTOR_NAMES])
def _base_select(scored,name,n):
    key=lambda x:(-x[1]["cagr"],-x[1]["mdd"],genome_hash(x[0]))
    if name.startswith("band_"):
        lim=int(name.split("_")[1])/100.0;ok=[x for x in scored if x[1]["mdd"]>=-lim-1e-12]
        return sorted(ok if ok else scored,key=key)[:n]
    if name=="global":
        f=sorted(pareto(scored),key=key);rest=sorted([x for x in scored if x not in f],key=key);return (f+rest)[:n]
    B=np.array([_behavior(m) for _,m in scored]);z=[]
    for i,x in enumerate(scored):
        if len(scored)==1:nv=0.0
        else:
            d=np.sqrt(np.mean((B-B[i])**2,axis=1));d=np.delete(d,i);nv=float(np.mean(np.sort(d)[:min(10,len(d))]))
        z.append((nv,x))
    z.sort(key=lambda q:(-q[0],-q[1][1]["cagr"],-q[1][1]["mdd"],genome_hash(q[1][0])))
    return [x for _,x in z[:n]]

def select(scored,name,n):
    """Species protection: retain one selected representative per compatibility species, then fill by island rule."""
    ordered=_base_select(scored,name,len(scored));groups=assign_species([g for g,_ in ordered])
    keep=[];seen=set()
    for grp in groups:
        ids={genome_hash(g) for g in grp}
        x=next((q for q in ordered if genome_hash(q[0]) in ids),None)
        if x and genome_hash(x[0]) not in seen:keep.append(x);seen.add(genome_hash(x[0]))
    for x in _base_select(scored,name,len(scored)):
        h=genome_hash(x[0])
        if h not in seen:keep.append(x);seen.add(h)
        if len(keep)>=n:break
    return keep[:n]

def _checkpoint(path,state):
    raw=pickle.dumps(state,protocol=5);path.write_bytes(raw)
    path.with_suffix(path.suffix+".sha256").write_text(hashlib.sha256(raw).hexdigest()+"\n")

def island_feasible(name,m):
    if name.startswith("band_"):
        lim=int(name.split("_")[1])/100.0
        return float(m["mdd"])>=-lim-1e-12
    return True

def update_archive(archive,scored,name):
    """Archive admission is under receiving-island semantics."""
    eligible=[x for x in scored if island_feasible(name,x[1])]
    return pareto(archive+eligible)

def canonical_raw_metric_cache(scored_by_island):
    """Canonical genome -> island-independent deterministic raw metrics only."""
    cache={}
    for pairs in scored_by_island.values():
        for g,m in pairs:cache.setdefault(genome_hash(g),dict(m))
    return cache

def receiving_migrants(receiver,receiver_scored,migrant_scored,count):
    """Process migrants anew under the receiver's complete island semantics.

    ``migrant_scored`` contains only genome + deterministic island-independent raw
    simulation metrics.  No source feasibility/rank/archive state is accepted by
    this API.  Receiver feasibility and ranking are recomputed here; archive
    admission is independently recomputed by ``update_archive`` when evaluated in
    the receiving population.
    """
    eligible=[(g,dict(m)) for g,m in migrant_scored if island_feasible(receiver,m)]
    if not eligible:return []
    combined=list(receiver_scored)+eligible
    chosen=select(combined,receiver,len(receiver_scored))
    mh={genome_hash(g) for g,_ in eligible}
    return [g for g,_ in chosen if genome_hash(g) in mh][:count]

def evaluation_jobs(pops,plateau_state):
    """Shared-pool work queue: frozen islands contribute exactly zero jobs.

    Workers are not owned by islands.  Removing a frozen island's jobs therefore
    makes the same worker/evaluation capacity available to every remaining active
    island without changing any population or generation budget.
    """
    return [(name,j,g) for name in ISLANDS if not plateau_state[name]["frozen"]
            for j,g in enumerate(pops[name])]

def extension_decision(aggregate_hv_history,current_budget,completed_generation,base=500,step=100,max_generations=800,window=50,threshold=.01):
    """Frozen H.2 training-only budget extension rule."""
    if completed_generation!=current_budget or current_budget<base or current_budget>=max_generations:return current_budget
    if len(aggregate_hv_history)<window+1:return current_budget
    old=float(aggregate_hv_history[-(window+1)]);new=float(aggregate_hv_history[-1])
    gain=(new-old)/max(abs(old),1e-12)
    return min(max_generations,current_budget+step) if gain>threshold+1e-12 else current_budget

def evolve_g2(*,evaluator,master_seed,fold,generations=BASE_GENERATIONS,population_size=POPULATION_SIZE,
              workers=6,checkpoint_dir:Path|None=None,resume_path:Path|None=None,population_factory=None,generation_stop=None,
              mechanics:dict|None=None):
    cfg={"plateau_window":40,"plateau_gain_threshold":.005,"migration_interval":MIGRATION_INTERVAL,
         "checkpoint_interval":CHECKPOINT_INTERVAL,"extension_base":500,"extension_step":100,
         "extension_max":800,"extension_window":50,"extension_threshold":.01}
    if mechanics:cfg.update(mechanics)
    if resume_path:
        raw=Path(resume_path).read_bytes();state=pickle.loads(raw)
        if state["master_seed"]!=master_seed or state["fold"]!=fold:raise ValueError("checkpoint identity")
        pops=state["pops"];archives=state["archives"];history=state["history"];plateaus=state["plateaus"];start=state["generation"]
        plateau_state=state.get("plateau_state",{k:{"phase":"BASE","window_start":0,"structural_until":None,"frozen":False} for k in ISLANDS})
        aggregate_hv_history=list(state.get("aggregate_hv_history",[]));current_budget=int(state.get("current_budget",generations));events=dict(state.get("events",{"extensions":0,"migration_events":0,"migrants_accepted":0,"freeze_events":0,"frozen_island_generation_skips":0}))
    else:
        makepop=population_factory or initial_population_g2
        pops={name:makepop(master_seed,fold,i,population_size) for i,name in enumerate(ISLANDS)}
        archives={k:[] for k in ISLANDS};history={k:[] for k in ISLANDS};plateaus={k:0 for k in ISLANDS};start=0
        plateau_state={k:{"phase":"BASE","window_start":0,"structural_until":None,"frozen":False} for k in ISLANDS}
        aggregate_hv_history=[];current_budget=int(generations);events={"extensions":0,"migration_events":0,"migrants_accepted":0,"freeze_events":0,"frozen_island_generation_skips":0}
    global _EVAL;_EVAL=evaluator
    ctx=get_context("fork")
    with ctx.Pool(processes=max(1,min(int(workers),os.cpu_count() or 1))) as pool:
      gen=start
      while gen<current_budget:
        active=[name for name in ISLANDS if not plateau_state[name]["frozen"]]
        events["frozen_island_generation_skips"]+=len(ISLANDS)-len(active)
        jobs=evaluation_jobs(pops,plateau_state)
        got=pool.map(_worker,jobs,chunksize=max(1,len(jobs)//(max(1,workers)*8))) if jobs else []
        scored={k:[] for k in ISLANDS}
        for name,j,g,m in got:scored[name].append((g,m))
        for name in active:
            scored[name].sort(key=lambda x:genome_hash(x[0]))
            archives[name]=update_archive(archives[name],scored[name],name)
            hv=hypervolume(archives[name]);history[name].append(hv)
            ps=plateau_state[name]
            # Plateau decisions are event/window based. The first qualifying
            # 40-generation window activates the frozen intervention for the
            # following 40 generations. Only after that complete window may a
            # second consecutive plateau freeze the island archive.
            elapsed=(gen+1)-int(ps["window_start"])
            if not ps["frozen"] and elapsed>=int(cfg["plateau_window"]):
                old_idx=max(0,len(history[name])-(int(cfg["plateau_window"])+1))
                old=history[name][old_idx];gain=(hv-old)/max(abs(old),1e-12)
                if gain<float(cfg["plateau_gain_threshold"]):
                    if ps["phase"]=="BASE":
                        plateaus[name]=1;ps["phase"]="INTERVENTION";ps["window_start"]=gen+1;ps["structural_until"]=(gen+1)+int(cfg["plateau_window"])
                    else:
                        plateaus[name]=2;ps["phase"]="FROZEN";ps["frozen"]=True;ps["structural_until"]=None;events["freeze_events"]+=1
                else:
                    plateaus[name]=0;ps["phase"]="BASE";ps["window_start"]=gen+1;ps["structural_until"]=None
        aggregate_hv_history.append(sum(hypervolume(archives[k]) for k in ISLANDS))
        if gen+1==current_budget:
            old_budget=current_budget
            current_budget=extension_decision(aggregate_hv_history,current_budget,gen+1,
              base=int(cfg["extension_base"]),step=int(cfg["extension_step"]),max_generations=int(cfg["extension_max"]),
              window=int(cfg["extension_window"]),threshold=float(cfg["extension_threshold"]))
            events["extensions"]+=int(current_budget>old_budget)
        migrants={k:[] for k in ISLANDS}
        raw_metric_cache=canonical_raw_metric_cache(scored)
        if (gen+1)%int(cfg["migration_interval"])==0:
            events["migration_events"]+=1
            count=max(1,int(np.ceil(population_size*.05)))
            for i,name in enumerate(ISLANDS):
                if plateau_state[name]["frozen"]:continue
                receiver=ISLANDS[(i+1)%len(ISLANDS)]
                if plateau_state[receiver]["frozen"]:continue
                outgoing=select(scored[name],name,count)
                # Rehydrate only deterministic raw metrics from the canonical cache.
                # Source feasibility/rank/archive state has no representation here.
                migrant_raw=[(g,raw_metric_cache[genome_hash(g)]) for g,_ in outgoing]
                accepted=receiving_migrants(receiver,scored[receiver],migrant_raw,count)
                migrants[receiver].extend(accepted);events["migrants_accepted"]+=len(accepted)
        nxt={}
        for i,name in enumerate(ISLANDS):
            if plateau_state[name]["frozen"]:
                nxt[name]=list(pops[name]);continue
            rng=np.random.Generator(np.random.PCG64(deterministic_seed(master_seed,fold,i,gen)))
            base=select(scored[name],name,population_size);parents=[g for g,_ in base]
            ps=plateau_state[name]
            if ps["frozen"]:nxt[name]=parents[:population_size];continue
            children=list(migrants[name]);# Immigrants are injected once, at entry to the intervention window.
            imm=int(round(population_size*.20)) if plateaus[name]==1 and ps["window_start"]==gen+1 else 0
            if imm:children.extend(initial_population_g2(f"{master_seed}|imm|{gen}|{name}",fold,i,imm))
            species=assign_species(parents)
            while len(children)<population_size:
                grp=species[int(rng.integers(0,len(species)))]
                a=grp[int(rng.integers(0,len(grp)))];b=grp[int(rng.integers(0,len(grp)))]
                structural_mult=2.0 if ps["phase"]=="INTERVENTION" and (gen+1)<int(ps["structural_until"]) else 1.0
                children.append(mutate_g2(crossover_g2(a,b,rng),rng,stage_for_generation(gen),structural_multiplier=structural_mult))
            nxt[name]=children[:population_size]
        pops=nxt
        # Observation-only early-stop hook: evaluated after the generation archive is
        # complete. It may terminate a calibration run but cannot change GA state.
        stop_now=bool(generation_stop and generation_stop(gen+1,archives,history))
        if checkpoint_dir and (gen+1)%int(cfg["checkpoint_interval"])==0:
            checkpoint_dir.mkdir(parents=True,exist_ok=True)
            _checkpoint(checkpoint_dir/f"g2_fold{fold}_gen{gen+1:04d}.pkl",
              {"master_seed":master_seed,"fold":fold,"generation":gen+1,"pops":pops,"archives":archives,"history":history,"plateaus":plateaus,"plateau_state":plateau_state,
               "aggregate_hv_history":aggregate_hv_history,"current_budget":current_budget,"mechanics":cfg,"events":events})
        if stop_now:break
        gen+=1
    _EVAL=None
    return {"populations":pops,"archives":archives,"history":history,"plateau_state":plateau_state,"completed_generations":gen+1 if stop_now else gen,"final_budget":current_budget,"aggregate_hv_history":aggregate_hv_history,"events":events}
