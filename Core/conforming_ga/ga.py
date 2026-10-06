"""Deterministic nine-island staged evolutionary runner.

No scientific guard thresholds beyond frozen DD-band constraints. Numeric guards
proposed by Claude remain disabled unless separately user-approved.
"""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib
import numpy as np
from .schema import *
from .engine import AllocationMode
from .evolution import *

DD_BANDS=(.10,.15,.20,.25,.30,.35,.40)
ISLANDS=tuple([f"band_{int(x*100)}" for x in DD_BANDS]+["global","novelty"])
POPULATION_SIZE=250
BASE_GENERATIONS=500
MIGRATION_INTERVAL=25
CHECKPOINT_INTERVAL=10

def _rng(master,fold,island,generation):
    return np.random.Generator(np.random.PCG64(deterministic_seed(master,fold,island,generation)))

def _mutate_term(term,rng,scale=.20):
    return replace(term,weight=float(term.weight+rng.normal(0,scale)))

def mutate(g:Genome,rng:np.random.Generator,stage:str)->Genome:
    """Stage emphasis changes operator probabilities; no gene type is disabled."""
    ow=operator_weights(stage); keys=list(ow); probs=np.array([ow[k] for k in keys],float);probs/=probs.sum()
    op=str(rng.choice(keys,p=probs))
    if op in ("context","sector","applicability","structure","family"):
        mcs=tuple(_mutate_term(x,rng) for x in g.market_contexts)
        scs=tuple(_mutate_term(x,rng) for x in g.sector_contexts)
        mods=[]
        for m in g.modules:
            mods.append(replace(m,
              stock_terms=tuple(_mutate_term(x,rng) for x in m.stock_terms),
              market_terms=tuple(_mutate_term(x,rng) for x in m.market_terms),
              sector_terms=tuple(_mutate_term(x,rng) for x in m.sector_terms),
              applicability_market=tuple(_mutate_term(x,rng) for x in m.applicability_market),
              applicability_sector=tuple(_mutate_term(x,rng) for x in m.applicability_sector)))
        return replace(g,market_contexts=mcs,sector_contexts=scs,modules=tuple(mods))
    if op=="lifecycle":
        return replace(g,lifecycle=replace(g.lifecycle,kappa=max(0.,g.lifecycle.kappa+rng.normal(0,.25)),
                                           lambda_u=max(0.,g.lifecycle.lambda_u+rng.normal(0,.02))))
    if op=="allocation":
        modes=list(AllocationMode)
        return replace(g,allocation=replace(g.allocation,
          mode=modes[int(rng.integers(0,4))] if rng.random()<.2 else g.allocation.mode,
          tau=float(np.clip(g.allocation.tau+rng.normal(0,.08),0,1)),
          q=float(g.allocation.q+rng.normal(0,.01)),
          gamma=max(.05,float(g.allocation.gamma+rng.normal(0,.15))),
          eta=max(0.,float(g.allocation.eta+rng.normal(0,.05)))))
    if op=="short":
        return replace(g,short_policy=replace(g.short_policy,
          enabled=(not g.short_policy.enabled) if rng.random()<.15 else g.short_policy.enabled,
          extra_hurdle=max(0.,g.short_policy.extra_hurdle+rng.normal(0,.003))))
    if op=="robustness":
        return replace(g,opportunity_map=replace(g.opportunity_map,
          intercept=float(g.opportunity_map.intercept+rng.normal(0,.003)),
          scale=max(.01,float(g.opportunity_map.scale+rng.normal(0,.05)))))
    return g

def crossover(a:Genome,b:Genome,rng)->Genome:
    pick=lambda x,y:x if rng.random()<.5 else y
    return Genome(pick(a.market_contexts,b.market_contexts),pick(a.sector_contexts,b.sector_contexts),
                  pick(a.stock_states,b.stock_states),pick(a.modules,b.modules),
                  pick(a.opportunity_map,b.opportunity_map),pick(a.allocation,b.allocation),
                  pick(a.lifecycle,b.lifecycle),pick(a.short_policy,b.short_policy))

def dominates(ma,mb):
    return (ma["cagr"]>=mb["cagr"] and abs(ma["mdd"])<=abs(mb["mdd"])
            and (ma["cagr"]>mb["cagr"] or abs(ma["mdd"])<abs(mb["mdd"])))

def pareto_front(scored):
    out=[]
    for x in scored:
        if not any(dominates(y[1],x[1]) for y in scored if y is not x):out.append(x)
    return out

def _behavior(m):
    return np.array([m.get(k,0.) for k in MAP_DESCRIPTOR_NAMES],float)

def select(scored,island_name,n=POPULATION_SIZE):
    # deterministic tie ordering by canonical genome hash.
    def gh(g):return hashlib.sha256(canonical_genome(g).encode()).hexdigest()
    if island_name.startswith("band_"):
        band=int(island_name.split("_")[1])/100
        feasible=[x for x in scored if abs(x[1]["mdd"])<=band+1e-12]
        pool=feasible if feasible else scored
        pool=sorted(pool,key=lambda x:(-x[1]["cagr"],abs(x[1]["mdd"]),gh(x[0])))
        return pool[:n]
    if island_name=="global":
        front=pareto_front(scored)
        rest=[x for x in scored if x not in front]
        front=sorted(front,key=lambda x:(-x[1]["cagr"],abs(x[1]["mdd"]),gh(x[0])))
        rest=sorted(rest,key=lambda x:(-x[1]["cagr"],abs(x[1]["mdd"]),gh(x[0])))
        return (front+rest)[:n]
    # novelty island: behavioral nearest-neighbor novelty + feasibility.
    B=np.array([_behavior(m) for _,m in scored])
    nov=[]
    for i,x in enumerate(scored):
        if len(scored)==1:nv=0.
        else:
            d=np.sqrt(np.mean((B-B[i])**2,axis=1));d=np.delete(d,i);nv=float(np.mean(np.sort(d)[:min(10,len(d))]))
        nov.append((nv,x))
    nov.sort(key=lambda z:(-z[0],-z[1][1]["cagr"],abs(z[1][1]["mdd"]),gh(z[1][0])))
    return [x for _,x in nov[:n]]

def evolve(*,evaluator,master_seed:str,fold:int,generations:int=BASE_GENERATIONS,
           population_size:int=POPULATION_SIZE,checkpoint_dir:Path|None=None,resume_path:Path|None=None,
           workers:int=1,genome_factory=None):
    """Run frozen nine-island mechanics. evaluator(genome)->metrics dict."""
    if resume_path is not None:
        state=json.loads(Path(resume_path).read_text())
        if state["master_seed"]!=master_seed or int(state["fold"])!=fold:
            raise ValueError("checkpoint identity mismatch")
        start_gen=int(state["generation"])
        pops={k:[genome_from_canonical(x) for x in v] for k,v in state["populations"].items()}
        archives={k:[(genome_from_canonical(x["genome"]),x["metrics"]) for x in v] for k,v in state["archives"].items()}
        history={k:[float(x) for x in v] for k,v in state["history"].items()}
        plateaus={k:int(v) for k,v in state["plateaus"].items()}
        population_size=len(next(iter(pops.values())))
    else:
        start_gen=0
        pops={}
        factory=genome_factory or random_genome
        for ii,name in enumerate(ISLANDS):
            pops[name]=[factory(deterministic_seed(master_seed,fold,ii,-1)+j) for j in range(population_size)]
        archives={k:[] for k in ISLANDS}; history={k:[] for k in ISLANDS};plateaus={k:0 for k in ISLANDS}
    for gen in range(start_gen,generations):
        stage=stage_for_generation(gen)
        scored={}
        for ii,name in enumerate(ISLANDS):
            # deterministic evaluation and reduction order independent of worker count.
            genomes=list(pops[name])
            if workers<=1:
                metrics=[evaluator(g) for g in genomes]
            else:
                with ThreadPoolExecutor(max_workers=workers) as ex:
                    metrics=list(ex.map(evaluator,genomes))
            pairs=list(zip(genomes,metrics))
            pairs.sort(key=lambda x:hashlib.sha256(canonical_genome(x[0]).encode()).hexdigest())
            scored[name]=pairs
            archives[name]=pareto_front(archives[name]+pairs)
            hv=max((m["cagr"] for _,m in archives[name]),default=-np.inf)
            history[name].append(float(hv))
            if len(history[name])>=41:
                old=history[name][-41];new=history[name][-1]
                gain=(new-old)/max(abs(old),1e-12) if np.isfinite(old) else np.inf
                if gain<.005:plateaus[name]+=1
                else:plateaus[name]=0
        # ring migration top 5% each 25 generations; migrants re-evaluated next generation.
        migrants={k:[] for k in ISLANDS}
        if (gen+1)%MIGRATION_INTERVAL==0:
            count=max(1,int(np.ceil(population_size*.05)))
            for ii,name in enumerate(ISLANDS):
                top=select(scored[name],name,count)
                migrants[ISLANDS[ring_destination(ii,len(ISLANDS))]].extend([g for g,_ in top])
        nxt={}
        for ii,name in enumerate(ISLANDS):
            rng=_rng(master_seed,fold,ii,gen)
            base=select(scored[name],name,population_size)
            parents=[g for g,_ in base]
            action=plateau_action(plateaus[name])
            if action=="FREEZE_REALLOCATE":
                nxt[name]=parents[:population_size];continue
            children=[]
            immigrant_fraction=.20 if action=="IMMIGRANTS_20_STRUCTURAL_UPWEIGHT" else 0.
            imm_n=int(round(population_size*immigrant_fraction))
            factory=genome_factory or random_genome
            children.extend(factory(int(rng.integers(0,2**63-1))) for _ in range(imm_n))
            children.extend(migrants[name])
            while len(children)<population_size:
                a=parents[int(rng.integers(0,len(parents)))];b=parents[int(rng.integers(0,len(parents)))]
                child=crossover(a,b,rng)
                child=mutate(child,rng,stage)
                children.append(child)
            nxt[name]=children[:population_size]
        pops=nxt
        if checkpoint_dir and (gen+1)%CHECKPOINT_INTERVAL==0:
            checkpoint_dir.mkdir(parents=True,exist_ok=True)
            payload={"master_seed":master_seed,"fold":fold,"generation":gen+1,
                     "populations":{k:[canonical_genome(g) for g in v] for k,v in pops.items()},
                     "archives":{k:[{"genome":canonical_genome(g),"metrics":m} for g,m in archives[k]] for k in ISLANDS},
                     "history":history,"plateaus":plateaus}
            raw=json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
            (checkpoint_dir/f"fold{fold}_gen{gen+1:04d}.json").write_bytes(raw)
    return {"populations":pops,"archives":archives,"history":history}
