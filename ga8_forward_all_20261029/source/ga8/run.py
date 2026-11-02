"""Bounded A-F driver. Run from repository root: python -m ga8.run."""
import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import resource
import time
from .engine import *

RAW = Path('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet')
STARTED = time.monotonic()
OUT = Path('/opt/mts/ga8')

def write(name, data):
    target = OUT / name
    temp = target.with_suffix(target.suffix+'.tmp')
    temp.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')
    temp.replace(target)

def status(stage, checks, next_action, eta=None, **kw):
    write('status.json', dict(system='GA8', stage=stage, updated_utc=datetime.now(timezone.utc).isoformat(),
          completed_checks=checks, blockers=kw.pop('blockers', []), current_command='python -m ga8.run', pid=os.getpid(),
          elapsed_seconds=time.monotonic()-STARTED, eta_seconds=eta, next_action=next_action, **kw))


def seed_genes():
    return [Gene('trend', threshold=.4, niche=2), Gene('relative_strength', 'momentum', 'and', .2, -1, -.2, 30),
            Gene('volatility', 'recursive', 'and', .1, 1, -.4, 12)]


def search(p, end, tag, rng, args):
    begin = time.monotonic()
    base = seed_genes()
    population = [(base, Manager(), [])]
    # Cover every enabled family and preserve independent niche specialists.
    for family in FAMILIES:
        population.append(([Gene(family, rng.choice(FAMILIES), rng.choice(['single','and','or']),
                                 rng.choice([.1,.3,.5]), rng.choice([-1,0,1,2])),
                            base[1], base[2]], Manager(slots=rng.choice([6,8,10]), reserve=rng.choice([.1,.2,.3])), []))
    cache, ledger, generation_rows = {}, [], []
    evaluated = []
    best = None
    stagnant = 0
    for generation in range(args.generations):
        rows = []
        for genes, manager, parents in population:
            if time.monotonic()-begin > args.budget:
                break
            key = identity(genes, manager)
            if key not in cache:
                result = replay(p, genes, manager, '2022-01-01', end)
                cache[key] = result
            result = cache[key]
            # Marginal contribution under exactly the same manager / market path.
            ablations = []
            for k in range(len(genes)):
                reduced = genes[:k] + genes[k+1:]
                aid = identity(reduced, manager)
                if aid not in cache:
                    cache[aid] = replay(p, reduced, manager, '2022-01-01', end)
                a = cache[aid]['metrics']
                b = result['metrics']
                ablations.append(dict(gene=k, delta_cagr=b['cagr']-a['cagr'], delta_mdd=b['max_drawdown']-a['max_drawdown'],
                                      delta_cost=b['costs']-a['costs'], delta_turnover=b['turnover']-a['turnover'],
                                      incremental_nav=b['final_nav']-a['final_nav']))
            row = dict(generation=generation, id=key, parents=parents, genes=list(map(asdict,genes)), manager=asdict(manager),
                       metrics=result['metrics'], audit=result['audit'], marginal=ablations,
                       niche_coverage=sorted(set(g.niche for g in genes)), families=sorted(set(g.family for g in genes)))
            ledger.append(row)
            rows.append((genes,manager,key,result,ablations))
            evaluated.append((genes,manager,key,result,ablations))
            elapsed=time.monotonic()-begin
            write(f'{tag}_lineage.json',ledger)
            status('D' if tag=='pilot' else 'E', ['A','B','C'], f'{tag}: generation {generation+1}/{args.generations}',
                   eta=max(0., args.generations*len(population)*4-len(cache))*elapsed/max(len(cache),1),
                   evaluations=len(cache), throughput_evaluations_per_second=len(cache)/elapsed)
        if not rows:
            break
        # Funded feasibility and contribution; elite incumbent cannot be lost.
        rows.sort(key=lambda x: (rank(x[3]), sum(m['incremental_nav'] for m in x[4])), reverse=True)
        current=rows[0]
        if best is None or rank(current[3]) > rank(best[3]):
            best=current
            stagnant=0
        else:
            stagnant+=1
        generation_rows.append(dict(generation=generation, best_id=best[2], metrics=best[3]['metrics'],
                                    unique_genomes=len(set(x[2] for x in rows)),
                                    family_coverage=sorted(set(g.family for x in rows for g in x[0])),
                                    manager_variants=len(set(json.dumps(asdict(x[1]),sort_keys=True) for x in rows))))
        if stagnant >= 100 or time.monotonic()-begin > args.budget:
            break
        # Retain best plus one representative per specialist niche before filling.
        parents=rows[:3]
        for niche in range(3):
            specialists=[x for x in rows if any(g.niche==niche for g in x[0])]
            if specialists and specialists[0] not in parents:
                parents.append(specialists[0])
        population=[(best[0],best[1],[best[2]])]
        while len(population)<8:
            a,b=rng.sample(parents,2) if len(parents)>1 else (parents[0],parents[0])
            child=list(a[0])
            # Prefer replacing the least useful funded contributor, retain novelty.
            k=min(a[4],key=lambda x:x['incremental_nav'])['gene'] if rng.random()<.7 else rng.randrange(len(child))
            child[k]=b[0][k % len(b[0])]
            child[k]=replace(child[k], family=rng.choice(FAMILIES), second=rng.choice(FAMILIES),
                             op=rng.choice(['single','and','or']), threshold=rng.uniform(-.1,.7),
                             niche=rng.choice([-1,0,1,2]), hold_sessions=rng.choice([8,15,25,40]),
                             weight=rng.choice([.04,.06,.08]), trailing=rng.choice([.03,.05,.08]),
                             hold_family=rng.choice(FAMILIES),exit_family=rng.choice(FAMILIES),
                             entry_tree=('and',rng.choice(FAMILIES),('or',rng.choice(FAMILIES),rng.choice(FAMILIES))) if rng.random()<.3 else ())
            m=replace(a[1],slots=rng.choice([5,7,10]),reserve=rng.choice([.1,.2,.35]),
                      correlation=rng.choice([.65,.8,.9]),replacement=rng.choice([.3,.7,1.]))
            population.append((child,m,[a[2],b[2]]))
        # Independent novelty challenger in every generation.
        population[-1]=([Gene(rng.choice(FAMILIES),rng.choice(FAMILIES),'or',.3,rng.choice([0,1,2])),base[0]],Manager(),[])
    elapsed=time.monotonic()-begin
    # Preserve Pareto frontier of funded CAGR and MDD, regardless of feasibility.
    unique={x[2]:x for x in evaluated}
    frontier=[x for x in unique.values() if not any(
        y[3]['metrics']['cagr']>=x[3]['metrics']['cagr'] and y[3]['metrics']['max_drawdown']<=x[3]['metrics']['max_drawdown']
        and (y[3]['metrics']['cagr']>x[3]['metrics']['cagr'] or y[3]['metrics']['max_drawdown']<x[3]['metrics']['max_drawdown'])
        for y in unique.values())]
    feasible=[x for x in unique.values() if x[3]['metrics']['feasible']]
    summary=dict(evaluations=len(cache), runtime_seconds=elapsed, evaluations_per_second=len(cache)/elapsed,
                 resources=dict(workers=1,available_cpus=os.cpu_count(),cpu_seconds_process=time.process_time(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
                 generations=generation_rows, best_id=best[2], best_metrics=best[3]['metrics'],
                 feasible_ids=[x[2] for x in feasible], frontier_ids=[x[2] for x in frontier],
                 stop_reason='bounded_generation_limit' if len(generation_rows)==args.generations else 'wall_budget',
                 survivor=None if not feasible else max(feasible,key=lambda x:rank(x[3]))[2])
    write(f'{tag}_search.json',summary)
    return best,summary


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='/opt/mts/ga8')
    parser.add_argument('--generations',type=int,default=3)
    parser.add_argument('--budget',type=float,default=240)
    parser.add_argument('--seed',type=int,default=80079)
    parser.add_argument('--smoke-only',action='store_true')
    args=parser.parse_args()
    if not 1<=args.generations<=10 or not 1<=args.budget<=900:
        raise ValueError('Bounded run requires 1–10 generations and 1–900 seconds/fold')
    global OUT
    OUT=Path(args.output)
    OUT.mkdir(parents=True,exist_ok=True)
    status('A',[], 'load real DEV79 data',60)
    p,audit=load_panel(RAW)
    source_hash=hashlib.sha256(RAW.read_bytes()).hexdigest()
    write('inventory.json',dict(prices=audit, source=str(RAW),sha256=source_hash,
          active_families=FAMILIES, disabled=dict(sector='No dated PIT history',earnings='No verified knowledge-time events',
          crash_AB_B1_C_R1='No verified causal input tape',SGOV='No verified SGOV bars',SPY='Not in source'),
          corporate_actions='Vendor split-normalized OHLC and per-share dividends; reject discontinuous split bars',
          universe='Fixed DEV79 research cohort; survivorship and retrospective membership limitations',
          grammar='Independent entry AND/OR, niche, hold/exit, loss/time/trailing, add/reduce, manager replacement'))
    genes=seed_genes()
    status('C',['A','B'],'real-data funded smoke',60)
    t=time.monotonic()
    smoke=replay(p,genes,Manager(),'2022-01-01','2023-01-01',True)
    write('smoke.json',smoke)
    write('shadow.json',dict(note='Independent native accounts, $100k each; never summed into funded equity',
          accounts=[replay(p,[g],Manager(),'2022-01-01','2023-01-01',True) for g in genes]))
    elapsed=time.monotonic()-t
    status('C_COMPLETE',['A','B','C'],'bounded evolutionary pilot',args.generations*8*4*elapsed/4,
           smoke_runtime_seconds=elapsed, funded_metrics=smoke['metrics'])
    print(json.dumps(dict(stage='C',runtime=elapsed,metrics=smoke['metrics']),allow_nan=False),flush=True)
    if args.smoke_only:
        return
    rng=random.Random(args.seed)
    pilot,summary=search(p,'2023-01-01','pilot',rng,args)
    print(json.dumps(dict(stage='D',summary=summary)),flush=True)
    # Sequential expanding training. Frozen selected genomes evaluated once on next year.
    folds=[]
    models=[]
    for train_end,test_end,model,search_summary in [ ('2023-01-01','2024-01-01',pilot,summary) ]:
        result=replay(p,model[0],model[1],train_end,test_end,True)
        write('fold_2023.json',result)
        folds.append(dict(train_end=train_end,end=test_end,id=model[2],metrics=result['metrics']))
    for train_end,test_end,tag in [('2024-01-01','2025-01-01','train_2023'),('2025-01-01','2026-01-01','train_2024')]:
        model,search_summary=search(p,train_end,tag,rng,args)
        result=replay(p,model[0],model[1],train_end,test_end,True)
        write(f'fold_{train_end[:4]}.json',result)
        folds.append(dict(train_end=train_end,end=test_end,id=model[2],metrics=result['metrics']))
    # Freeze before opening 2026 outcomes. No search touches 2025 or 2026 returns.
    freeze=dict(genes=list(map(asdict,model[0])),manager=asdict(model[1]),id=model[2],
                train_end='2025-01-01',selection_uses='2022–2024 training only',seed=args.seed)
    write('frozen_model.json',freeze)
    frozen_hash=hashlib.sha256((OUT/'frozen_model.json').read_bytes()).hexdigest()
    holdout=replay(p,model[0],model[1],'2026-01-01','2027-01-01',True)
    write('final_holdout.json',holdout)
    write('final_shadow.json',dict(accounts=[replay(p,[g],model[1],'2026-01-01','2027-01-01',True) for g in model[0]],
                                   note='Separate funded accounts; diagnostic only, never portfolio substitute'))
    benchmarks=dict(cash=dict(cagr=0.,max_drawdown=0.,calmar=0.,annual_yield=0.),SPY=None,
                    note='Cash zero yield; SPY unavailable; no invented benchmark prices')
    write('results.json',dict(folds=folds,holdout=holdout['metrics'],benchmarks=benchmarks,frozen_sha256=frozen_hash,
          survivor=model[2] if all(x['metrics']['feasible'] for x in folds) and holdout['metrics']['feasible'] else None,
          edge_claim=False,config=vars(args),runtime_seconds=time.monotonic()-STARTED))
    report=['# GA8 engineering and bounded research report','',
            'Real-data funded replay and bounded evolutionary search completed. No validated edge claim.',
            '','| Replay | CAGR | MDD | Calmar | Closed trades | Exposure | Costs |',
            '|---|---:|---:|---:|---:|---:|---:|']
    for label,m in [('2022 smoke',smoke['metrics'])]+[(x['train_end'][:4]+' walk-forward',x['metrics']) for x in folds]+[('2026 final holdout',holdout['metrics'])]:
        report.append(f"| {label} | {m['cagr']:.2%} | {m['max_drawdown']:.2%} | {m['calmar']:.3f} | {m['closed_trades']} | {m['exposure']:.2%} | ${m['costs']:.2f} |")
    report += ['', 'No survivor is promoted unless all chronological tests satisfy MDD <20% and Calmar >1.5. '
               'The best infeasible frontiers remain in each search ledger.', '',
               'Each fold resets to $100,000, purges positions at its boundary, and uses only backward warmup. '
               '2026 is opened after freezing the 2022–2024 model; 2025 results did not tune it. See holdout_access.json for any accounting-correction re-evaluations. '
               'Earlier MTS studies have seen these years, so this is GA8 isolation, not global blindness.', '',
               'Next-open stops trigger at close; gaps can exceed the -2% loss policy. Conservative T+2 settlement, '
               '5bp slippage and 1bp fee each side. 10% entry cap (9.9% buffer), 2% portfolio stop-risk cap, '
               'no leverage; cash yields zero. Per-symbol weights can drift over 10% intraday and trigger next-open exit. '
               'Position sizing limits implied stop risk below the 1–2% per-trade ceiling; it does not force that much risk.', '',
               'Sector, earnings, named crash A/B/B1/C and R-1, SGOV and SPY are disabled for missing verified causal inputs. '
               'Price correlation provides diversification. Corporate actions rely on vendor split normalization with '
               'dividends credited as nonspendable receivables to overnight holders; no independent vendor authenticity certification. '
               'Static DEV79 membership has survivorship/PIT limitations. No GA4 archive strategies were used.', '',
               'Search is a small engineering pilot, not exhaustive discovery. Grammar supports nested AND/OR trees, '
               'independent hold/exit families and conditional scaling; all seven enabled families are initialized. '
               'No long exploration is authorized by this result. See lineage, marginal ablations, funded fills and equity in JSON.', '',
               f'Measured first search: {summary["evaluations"]} native evaluations in {summary["runtime_seconds"]:.2f}s '
               f'({summary["evaluations_per_second"]:.2f}/s). Total elapsed {time.monotonic()-STARTED:.2f}s.']
    (OUT/'pilot_report.md').write_text('\n'.join(report)+'\n')
    status('F_PACKAGED',['A','B','C','D','E'],'verify and commit isolated GA8 source',0,
           funded_metrics=holdout['metrics'],throughput_evaluations_per_second=summary['evaluations_per_second'],
           completed_run=True)
    print(json.dumps(dict(stage='E',folds=folds,holdout=holdout['metrics'])),flush=True)

if __name__=='__main__':
    try:
        import sys
        if '--long-search' in sys.argv:
            sys.argv.remove('--long-search')
            from .long_run import main as long_main
            long_main()
        else:
            main()
    except Exception as exc:
        if '--long-search' not in __import__('sys').orig_argv:
            status('FAILED',[],str(exc),None,blockers=[str(exc)])
        raise
