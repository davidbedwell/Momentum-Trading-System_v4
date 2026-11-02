"""Bounded GA9 pilot: python -m ga9.run. Writes exclusively to GA9 or /tmp."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import signal
import sys
import time
import traceback
import numpy as np
import pandas as pd
from .execution import Gene, Manager, load_panel, replay
from .evolution import search, funded
from .objective import benchmark, objective, discrimination
from .risk import MAX_DRAWDOWN
from .benchmarks import BenchmarkPolicy, DEFAULT_SPY, SECONDARY, attach_primary, load_universe, selection_benchmark

RAW=Path('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet')
PACKAGE=Path(__file__).resolve().parent


def write(path,value):
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    temp.replace(path)


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def save_replay(root,name,result,passive,secondary=None):
    objective(result,passive)
    if secondary is not None:
        result['metrics']['secondary_benchmark_cagr']=secondary['metrics']['cagr']
        result['metrics']['secondary_excess_pp']=100*(result['metrics']['cagr']-secondary['metrics']['cagr'])
        result['metrics']['secondary_incremental_nav']=result['metrics']['final_nav']-secondary['metrics']['final_nav']
    write(root/f'{name}.json',result)
    frame=pd.DataFrame(result['equity'])
    if 'holdings_detail' in frame:
        frame['holdings_detail']=frame.holdings_detail.map(json.dumps)
    frame['benchmark_nav']=[r['nav'] for r in passive['equity']]
    if list(frame.date)!=[r['date'] for r in passive['equity']]:
        raise AssertionError('Benchmark and strategy calendars differ')
    frame['primary_benchmark_nav']=frame.benchmark_nav
    if secondary is not None:
        if list(frame.date)!=[r['date'] for r in secondary['equity']]:
            raise AssertionError('Secondary universe calendar differs from strategy')
        frame['secondary_full_universe_nav']=[r['nav'] for r in secondary['equity']]
    frame['incremental_nav']=frame.nav-frame.benchmark_nav
    frame.to_csv(root/f'{name}_daily.csv',index=False)
    return result['metrics']


def report(manifest,folds,elapsed):
    lines=['# GA9 bounded pilot', '',
           f"Command: `{manifest['command']}`",'',
           f"Primary benchmark: {manifest['benchmark']} buy-and-hold for declared {manifest['benchmark_policy']['universe_profile']} universe, frozen before training/test.",
           f"Secondary diagnostic: equal-weight buy-and-hold of the complete {len(manifest['universe'])}-stock PIT research universe; never the selected subset.",
           'PIT eligibility, $100,000 initial capital, 5bp slippage and 1bp commission per side.',
           'Secondary sleeves remain cash until listing; GEV regular-way listing is 2024-04-02.',
           'Portfolio hard acceptance gate: absolute daily close MDD <=8.00%, including initial capital.',
           'Success additionally requires positive net excess CAGR. No Calmar admission gate.', '',
           f"Configured horizon sessions: {manifest['horizons']}; explicit swing cap: {manifest['swing_max_sessions']}.",
           'Each new position samples its planned expiry from the frozen evolved mixture using a deterministic',
           'date/symbol/genome hash. Native stops and opportunity-cost exits can close it sooner.', '',
           f"Sample: {len(manifest['sample'])} fixed research stocks: {', '.join(manifest['sample'])}.", '',
           '| Year | Phase/control | CAGR % | Primary % | Excess pp | Full EW % | EW excess pp | MDD % | Calmar | Turnover | Exposure % | Closed trades / fills | Max stock % | Max sector % | Pass |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|']
    for fold in folds:
        for name,m in fold['metrics'].items():
            lines.append(f"| {fold['year']} | {name} | {100*m['cagr']:.2f} | {100*m['benchmark_cagr']:.2f} | {m['excess_pp']:.2f} | {100*m['secondary_benchmark_cagr']:.2f} | {m['secondary_excess_pp']:.2f} | {100*m['max_drawdown']:.2f} | {m['calmar']:.2f} | {m['turnover']:.2f} | {100*m['exposure']:.1f} | {m['closed_trades']} / {m['fills']} | {100*m.get('max_symbol_weight',0):.1f} | {100*m.get('max_sector_weight',0):.1f} | {'yes' if m['success'] else 'no'} |")
    success=len(folds)==3 and all(f['accepted'] for f in folds)
    lines += ['',f"All three GA9 forward folds pass: {success}. Elapsed: {elapsed:.1f}s.", '',
              'Selection uses an internal chronological half-year validation segment within each training period.',
              'Benchmark profile, symbol, source hash and complete-universe membership are predeclared in the manifest.',
              'The selected genome is then refit through December and frozen before the next year is loaded.',
              'Training-refit metrics are in-sample diagnostics; internal validation is selection-used.',
              'Forward results never feed model, horizon, or manager selection. Each fold starts a new account;',
              'residual positions are marked, with no fictitious terminal liquidation. No continuous stitched-return claim.', '',
              'GA8 seed control replays the three source seed genes and manager; it is not the running GA8 champion',
              'or an equal-budget search comparison. Momentum control uses native momentum entry/lifecycle.',
              'Per-gene funded ablations compare full and removed-gene accounts under identical cash/cost constraints.',
              'Predictive discrimination is a separate post-freeze label diagnostic, never a live feature.', '',
              'Unknown sectors share one conservative sector bucket capped at entry; market drift/gaps can exceed',
              'allocation caps. Verified historical sector classifications and SGOV execution bars are unavailable.',
              'Cash/NO_TRADE is implemented; SGOV remains disabled rather than receiving invented returns.',
              'Dividend receivables are not spendable without payment dates. Data is vendor split-normalized.',
              'Fixed DEV79 membership is not evidence of a historically survivorship-free universe.',
              'GA9 forward folds are protected from GA9 selection, but were previously accessed in GA8 research.',
              f"Prior GA9 engineering forward runs disclosed in manifest: {manifest['prior_ga9_forward_access']}.",
              'An observed risk breach is rejected, never clipped; next-open gaps prevent any guarantee of an 8% live cap.', '',
              'Artifacts: manifest.json, fold_YYYY/frozen.json, selection.json, rejected_risk.json,',
              'training_rejected_risk.json, forward_rejected_risk.json, primary benchmark.json and secondary_full_universe.json,',
              'training_refit/forward_frozen/control JSON and daily CSV ledgers, contribution.json,',
              'discrimination.json, results.json and status.json. Stop via this output directory’s STOP file.',
              'Budget checks occur between candidates; a candidate/refit/reporting task finishes atomically.',
              'No GA8 process, source, output or checkpoint is written by this runner.']
    return '\n'.join(lines)+'\n'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=RAW)
    parser.add_argument('--universe-profile',choices=['broad_us','nasdaq'],default='broad_us')
    parser.add_argument('--benchmark-data',type=Path,help='primary ETF parquet: SPY for broad_us, QQQ for nasdaq')
    parser.add_argument('--universe-data',type=Path,help='complete research universe parquet, independent of --symbols; defaults to --data')
    parser.add_argument('--output',type=Path,default=PACKAGE/'artifacts'/datetime.now(timezone.utc).strftime('pilot_%Y%m%d_%H%M%S'))
    parser.add_argument('--generations',type=int,choices=range(1,4),default=2)
    parser.add_argument('--population',type=int,choices=range(4,9),default=4)
    parser.add_argument('--budget',type=float,default=30.,help='seconds per fold search, checked between candidates')
    parser.add_argument('--seed',type=int,default=90079)
    parser.add_argument('--symbols',help='comma-separated exact sample; applied BEFORE cross-sectional features')
    parser.add_argument('--horizons',default='5,20,60,120')
    parser.add_argument('--swing-max-sessions',type=int,default=None,help='explicit constrained experiment; horizons must respect it')
    parser.add_argument('--membership',type=Path,help='dated historical membership CSV')
    parser.add_argument('--screen-top-k',type=int,default=20)
    parser.add_argument('--broad-discovery',action='store_true',help='research: rank all observed momentum patterns, including mixed/negative horizons')
    args=parser.parse_args(argv)
    from .screening import ScreenPolicy
    screen_policy=ScreenPolicy(top_k=args.screen_top_k,require_all_positive=not args.broad_discovery)
    horizons=tuple(int(x) for x in args.horizons.split(','))
    if not horizons or min(horizons)<1 or len(set(horizons))!=len(horizons):
        parser.error('horizons must be unique positive session counts')
    if not 1<=args.budget<=120:
        parser.error('pilot budget must be 1..120 seconds per fold')
    if args.swing_max_sessions is not None and max(horizons)>args.swing_max_sessions:
        parser.error('explicit swing experiment requires every horizon <= swing-max-sessions')
    output=args.output.resolve()
    if not (output.is_relative_to(PACKAGE) or output.is_relative_to(Path('/tmp'))):
        parser.error('output must be within GA9 package or /tmp; other runtime directories are protected')
    output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    requested_stop=False
    def stop_handler(*_):
        nonlocal requested_stop
        requested_stop=True
    signal.signal(signal.SIGTERM,stop_handler)
    signal.signal(signal.SIGINT,stop_handler)
    stop=lambda: requested_stop or (output/'STOP').exists()
    policy=BenchmarkPolicy(args.universe_profile)
    primary_path=args.benchmark_data or (DEFAULT_SPY if policy.primary=='SPY' else None)
    universe_path=args.universe_data or args.data
    universe=sorted(pd.read_parquet(universe_path,columns=['ticker']).ticker.unique())
    data_universe=sorted(pd.read_parquet(args.data,columns=['ticker']).ticker.unique())
    sample=sorted(set(args.symbols.split(','))) if args.symbols else data_universe
    command=shlex.join([sys.executable,'-m','ga9.run',*(sys.argv[1:] if argv is None else argv)])
    manifest=dict(screen_policy=screen_policy.record(),membership=str(args.membership) if args.membership else None,
                  membership_sha256=sha(args.membership) if args.membership else None,system='GA9',command=command,pid=os.getpid(),created_utc=datetime.now(timezone.utc).isoformat(),
                  data=str(args.data),data_sha256=sha(args.data),sample=sample,initial_capital=100000,
                  benchmark=policy.primary,benchmark_policy=policy.record(),risk_limit=MAX_DRAWDOWN,
                  benchmark_data=str(primary_path) if primary_path else None,
                  benchmark_data_sha256=sha(primary_path) if primary_path and primary_path.is_file() else None,
                  universe=universe,data_universe=data_universe,universe_data=str(universe_path),universe_data_sha256=sha(universe_path),
                  horizons=horizons,swing_max_sessions=args.swing_max_sessions,seed=args.seed,
                  generations=args.generations,population=args.population,budget_seconds_per_fold=args.budget,
                  source_sha256={p.name:sha(p) for p in PACKAGE.glob('*.py')},
                  missing_evidence=['verified historical sector metadata; all stocks conservatively UNKNOWN',
                                    'verified SGOV bars; cash fallback','dividend payment dates'],
                  forward_access='Previously used in GA8; protected from GA9 selection only',
                  prior_ga9_forward_access=[str(p) for p in (PACKAGE/'artifacts').glob('*')
                                            if any(p.glob('fold_*/forward_frozen.json')) and p!=output])
    write(output/'manifest.json',manifest)
    def status(stage,**kwargs):
        write(output/'status.json',dict(stage=stage,pid=os.getpid(),risk_limit=MAX_DRAWDOWN,
              elapsed_seconds=time.monotonic()-started,updated_utc=datetime.now(timezone.utc).isoformat(),**kwargs))
    folds=[]
    try:
        if not set(data_universe).issubset(universe):
            raise ValueError('Secondary must contain the complete stock-data universe, not a selected subset')
        if not set(sample).issubset(universe):
            raise ValueError('Evaluated sample must be contained in the complete diagnostic universe')
        if set(sample) != set(universe) or set(data_universe) != set(universe):
            raise ValueError('Daily screening requires the complete universe; subset --symbols is unsupported')
        for year in [2023,2024,2025]:
            if stop(): break
            root=output/f'fold_{year}';root.mkdir()
            end=f'{year}-01-01'; forward_end=f'{year+1}-01-01'
            status('training',year=year,eta_seconds=None,next_action='calibration and internal validation')
            p,audit=load_panel(args.data,end=end,sample=sample,membership=args.membership,screen_policy=screen_policy)
            p,primary_audit=attach_primary(p,primary_path,policy,end)
            write(root/'training_primary_audit.json',primary_audit)
            write(root/'training_input_audit.json',audit)
            def progress(row):
                status('selection',year=year,generation=row['generation'],candidate_id=row['id'],
                       eta_seconds=max(0,args.budget-row['elapsed_seconds']),
                       next_action='finish bounded search, refit selected genome, then freeze')
            candidate,models,selection=search(p,year,args.generations,args.population,args.budget,args.seed,horizons,stop,progress)
            write(root/'selection.json',selection)
            write(root/'rejected_risk.json',selection['rejected_risk'])
            frozen=dict(screen_policy=manifest['screen_policy'],membership_sha256=manifest['membership_sha256'],candidate=candidate.record(),models=models,selected_id=candidate.id,
                        trained_before=end,forward_start=end,forward_end=forward_end,
                        risk_limit=MAX_DRAWDOWN,sample=sample,benchmark=manifest['benchmark'],
                        benchmark_policy=manifest['benchmark_policy'],benchmark_data_sha256=manifest['benchmark_data_sha256'],
                        universe=universe,universe_data_sha256=manifest['universe_data_sha256'])
            write(root/'frozen.json',frozen)
            frozen_hash=sha(root/'frozen.json')
            if stop(): break
            status('training_refit_diagnostic',year=year,eta_seconds=None)
            train_passive=selection_benchmark(p,'2022-01-01',end)
            train_universe,_=load_universe(universe_path,universe,end,p.dates,membership=args.membership)
            train_secondary=benchmark(train_universe,'2022-01-01',end)
            training=funded(p,candidate,models,'2022-01-01',end)
            metrics={'training_refit_in_sample':save_replay(root,'training_refit',training,train_passive,train_secondary)}
            write(root/'training_rejected_risk.json',[] if training['metrics']['feasible'] else
                  [dict(phase='training_refit_in_sample',selected_id=candidate.id,metrics=training['metrics'],
                        reason='absolute_MDD_above_8pct')])
            # First load of this fold's external forward rows occurs AFTER the freeze.
            status('forward_frozen',year=year,frozen_sha256=frozen_hash,eta_seconds=None)
            if args.membership and sha(args.membership)!=manifest['membership_sha256']:
                raise ValueError('Frozen membership source changed')
            if sha(args.data)!=manifest['data_sha256']:
                raise ValueError('Frozen stock source changed')
            if sha(primary_path)!=manifest['benchmark_data_sha256'] or sha(universe_path)!=manifest['universe_data_sha256']:
                raise ValueError('Frozen benchmark source changed before forward evaluation')
            forward,forward_audit=load_panel(args.data,end=forward_end,sample=sample,membership=args.membership,screen_policy=screen_policy)
            write(root/'forward_input_audit.json',forward_audit)
            forward,primary_audit=attach_primary(forward,primary_path,policy,forward_end)
            write(root/'forward_primary_audit.json',primary_audit)
            complete,universe_audit=load_universe(universe_path,universe,forward_end,forward.dates,membership=args.membership)
            write(root/'forward_universe_audit.json',universe_audit)
            passive=selection_benchmark(forward,end,forward_end)
            secondary=benchmark(complete,end,forward_end)
            result=funded(forward,candidate,models,end,forward_end)
            metrics['forward_frozen']=save_replay(root,'forward_frozen',result,passive,secondary)
            write(root/'forward_rejected_risk.json',
                  [] if result['metrics']['feasible'] else [dict(phase='forward_frozen',
                       selected_id=candidate.id,metrics=result['metrics'],reason='absolute_MDD_above_8pct')])
            save_replay(root,'benchmark',passive,passive,secondary)
            save_replay(root,'secondary_full_universe',secondary,passive,secondary)
            ga8_genes=[Gene('trend',threshold=.4,niche=2),Gene('relative_strength','momentum','and',.2,-1,-.2,30),
                       Gene('volatility','recursive','and',.1,1,-.4,12)]
            for name,genes in [('ga8_seed_control',ga8_genes),('momentum_control',[Gene('momentum')])]:
                baseline=replay(forward,genes,Manager(),end,forward_end,detail=True)
                metrics[name]=save_replay(root,name,baseline,passive,secondary)
            contribution=[]
            for k in range(len(candidate.genes)):
                removed=funded(forward,candidate,models,end,forward_end,omit=k)
                rm=save_replay(root,f'without_gene_{k}',removed,passive,secondary)
                fm=metrics['forward_frozen']
                contribution.append(dict(gene=k,incremental_nav=fm['final_nav']-rm['final_nav'],
                                         delta_excess_pp=fm['excess_pp']-rm['excess_pp'],
                                         delta_mdd=fm['max_drawdown']-rm['max_drawdown'],
                                         delta_costs=fm['costs']-rm['costs'],
                                         phase='post_freeze_diagnostic_never_used_for_selection'))
            write(root/'contribution.json',contribution)
            write(root/'discrimination.json',discrimination(forward,candidate.genes,models,candidate.mix,end,forward_end))
            if sha(root/'frozen.json')!=frozen_hash:
                raise AssertionError('Frozen model changed during forward evaluation')
            folds.append(dict(year=year,selected_id=candidate.id,metrics=metrics,contribution=contribution,
                              frozen_sha256=frozen_hash,rejected_candidates=len(selection['rejected_risk']),
                              selection_stop_reason=selection['stop_reason'],
                              accepted=bool(metrics['training_refit_in_sample']['feasible'] and
                                            metrics['forward_frozen']['success'])))
            write(output/'results.json',dict(folds=folds,risk_limit=MAX_DRAWDOWN,
                  all_forward_pass=len(folds)==3 and all(f['accepted'] for f in folds)))
            (output/'report.md').write_text(report(manifest,folds,time.monotonic()-started))
        status('stopped' if stop() else 'complete',completed_folds=len(folds),eta_seconds=0,
               all_forward_pass=len(folds)==3 and all(f['accepted'] for f in folds))
    except Exception as exc:
        write(output/'failure.json',dict(error=repr(exc),traceback=traceback.format_exc()))
        status('failed',blocker=repr(exc))
        raise
    print(str(output))
    return output

if __name__=='__main__': main()
