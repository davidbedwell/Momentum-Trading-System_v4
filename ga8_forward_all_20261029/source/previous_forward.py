"""Run from repository root: /opt/mts/.venv/bin/python ga8_forward_stop75_20261029/run_forward.py"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hashlib
import json
from datetime import datetime, timezone
from types import SimpleNamespace
import numpy as np
from ga8.engine import load_panel, replay, identity, metrics
from ga8.long_run import decode
from ga8.run import RAW
from ga9.benchmarks import load_primary, BenchmarkPolicy
from ga9.objective import benchmark

OUT = Path(__file__).resolve().parent
SNAP = Path('/opt/mts/ga8/production_500_20261029/manual_stop_75_20261029')
SPY = Path('/opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet')
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
def passive(p, dates):
    ix=p.dates.get_indexer(dates)
    assert (ix>=0).all()
    # Reuse existing funded passive engine; no GA9 runs or artifacts are opened.
    v=SimpleNamespace(dates=dates, symbols=p.symbols, open=p.open[ix], close=p.close[ix],
                      dividends=p.dividends[ix], eligible=None)
    r=benchmark(v, '2024-01-01', '2025-01-01')
    # Use GA8 metric convention for every comparison.
    r['metrics']=metrics([x['nav'] for x in r['equity']], r['fills'],
                         [x['exposure'] for x in r['equity']], len(dates))
    r['metrics']['open_positions']=len(r['fills'])
    return r
def main():
    before={str(p):sha(p) for p in SNAP.iterdir() if p.is_file()}
    status=json.loads((SNAP/'status.json').read_text())
    row=status['best_feasible_portfolio']; genes, manager=decode(row)
    assert status['phase']==1 and status['train_end']=='2024-01-01'
    assert row['metrics']['feasible'] and identity(genes,manager)==row['id']
    write('frozen_portfolio.json',row)
    p,audit=load_panel(RAW,end='2025-01-01')
    # Small replay first, then verify prefix results don't depend on future bars.
    short,_=load_panel(RAW,end='2024-02-01')
    smoke=replay(short,genes,manager,'2024-01-01','2024-02-01',True)
    prefix=replay(p,genes,manager,'2024-01-01','2024-02-01',True)
    assert smoke==prefix, 'Future data changed prefix replay'
    write('smoke.json',dict(passed=True,sessions=smoke['metrics']['sessions'],prefix_causality=True))
    print('Small replay and prefix causality passed',flush=True)
    training=replay(p,genes,manager,'2022-01-01','2024-01-01')
    assert training['metrics']==row['metrics'], 'Frozen training parity failed'
    result=replay(p,genes,manager,'2024-01-01','2025-01-01',True)
    dates=p.dates[(p.dates>='2024-01-01')&(p.dates<'2025-01-01')]
    spy,spy_audit=load_primary(SPY,BenchmarkPolicy('broad_us'),'2025-01-01',dates)
    results={'GA8':result,'SPY':passive(spy,dates),'equal_weight_DEV79':passive(p,dates)}
    summary={}
    for name,r in results.items():
        assert [x['date'] for x in r['equity']]==dates.strftime('%Y-%m-%d').tolist()
        m=r['metrics']; m['net_return']=m['final_nav']/100000-1
        exp=[x['holdings']/x['nav'] for x in r['equity']]
        m['min_exposure']=min(exp); m['max_exposure']=max(exp);m['terminal_exposure']=exp[-1]
        m['entry_fills']=sum(f['action']=='ENTRY' for f in r['fills'])
        summary[name]=m
        write(name+'.json',r)
    comparisons={name:dict(net_return_difference_pp=100*(summary['GA8']['net_return']-m['net_return']),
                           cagr_difference_pp=100*(summary['GA8']['cagr']-m['cagr']),
                           mdd_difference_pp=100*(summary['GA8']['max_drawdown']-m['max_drawdown']),
                           final_nav_difference=summary['GA8']['final_nav']-m['final_nav'])
                 for name,m in summary.items() if name!='GA8'}
    assert before=={str(p):sha(p) for p in SNAP.iterdir() if p.is_file()}
    write('summary.json',dict(results=summary,comparisons=comparisons))
    write('metadata.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=1,
        portfolio_id=row['id'],snapshot_hashes=before,source=str(RAW),source_sha256=sha(RAW),
        spy_source=str(SPY),spy_sha256=sha(SPY),
        code_hashes={f:sha(f) for f in ['ga8/engine.py','ga8/long_run.py','ga9/benchmarks.py','ga9/objective.py','ga9/execution.py',__file__]},
        start=str(dates[0].date()),last=str(dates[-1].date()),end_exclusive='2025-01-01',sessions=len(dates),initial_nav=100000,
        training_parity_passed=True,prefix_causality_passed=True,production_snapshot_unchanged=True,
        raw_audit=audit,spy_audit=spy_audit,
        QQQ='Unavailable: absent from DEV79; no real QQQ parquet found under /opt/mts. No synthetic substitute.',
        conventions=['Fresh cash account; first decision Jan 2 close, earliest entry Jan 3 open for all.',
        '5 bps adverse slippage plus 1 bp commission each fill; fractional shares.',
        'Dividends in NAV as nonspendable receivables; no reinvestment; terminal holdings marked, no liquidation.',
        'CAGR uses 252/sessions. GA8 T+2 settlement; no cash interest.',
        'No refit, evolution, parameter selection, or 2026 holdout replay.'],
        limitations=['Retrospectively selected DEV79 sample; historical full-market PIT membership/delisted coverage unproven. Applies to strategy and equal-weight diagnostic.',
        'Equal weight assigns 79 fixed sleeves; GEV cash until regular-way listing Apr 2 2024. No filtering on forward performance.',
        'Prefix check validates data causality, not historical universe selection. This is chronological out-of-training replay, not a prospectively sealed experiment.',
        'Vendor split-normalized prices and dividend ex-date receivables; dividend payment dates unavailable.']))
    print(json.dumps(dict(results=summary,comparisons=comparisons),indent=2),flush=True)
if __name__=='__main__':
    main()
