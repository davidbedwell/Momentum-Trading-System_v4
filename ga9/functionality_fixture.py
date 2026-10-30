"""SYNTHETIC engineering fixture. No historical performance or fitted models."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .execution import Panel, Gene, Manager, FAMILIES, replay
from .alpaca_repair import reuse_benchmark


def fixture():
    dates = pd.bdate_range('2030-01-07', periods=8)
    close = np.array([[100,100],[100,100],[99,101],[99,101],[99,101],[99,101],[99,101],[99,101]],float)
    opens = np.vstack([close[0],close[:-1]])
    features = {k: np.zeros((8,2)) for k in FAMILIES}
    # Decision inputs fixed in advance, available at each synthetic close only.
    features['momentum'][:2] = [[1, .8],[1,.8]]
    features['momentum'][2] = .1
    features['volume'][:] = 2  # higher-scoring generalist must lose to specialists
    features['trend'][3:] = -1
    niche = np.tile([0,1],(8,1))
    returns = np.vstack([np.zeros(2), close[1:]/close[:-1]-1])
    p = Panel(dates,['SYN_A','SYN_B'],opens,close,np.zeros((8,2)),returns,
              features,niche,np.zeros(8),eligible=np.ones((8,2),bool),
              screen_mask=np.ones((8,2),bool),screen_score=np.ones((8,2)))
    genes = [Gene('momentum',niche=i,weight=.06,add=1,reduce=-.005) for i in (0,1)]
    genes.append(Gene('volume',weight=.06,add=1))
    return p, genes, Manager(slots=2,reserve=.91)


def execute(p=None, genes=None, manager=None, **kwargs):
    base = fixture()
    p,genes,manager = p or base[0], genes or base[1], manager or base[2]
    return replay(p,genes,manager,p.dates[0],p.dates[-1]+pd.Timedelta(days=1),
                  detail=True,edge_mode=True,niche_first=True,enforce_drawdown=True,**kwargs)


def run(output):
    p,genes,manager = fixture()
    result = execute(p,genes,manager)
    assert {f['gene'] for f in result['fills'] if f['action']=='ENTRY'} >= {0,1}
    assert any(f['action'] in ('REDUCE','EXIT') for f in result['fills'])
    assert any(e['decision']=='NO_TRADE' for e in result['events'])
    assert result['metrics']['feasible'] and result['audit']['min_cash'] >= 0
    # Predeclared synthetic benchmark buys at the same first executable open,
    # charges the same entry slippage/fee, and marks residual shares daily.
    benchmark_close = 100 * 1.001**np.arange(8)
    q = 100000/(100*1.0005*1.0001)
    benchmark = [100000.] + (q*benchmark_close[1:]).tolist()
    for row,b in zip(result['equity'],benchmark):
        row['synthetic_benchmark_nav']=b
        row['excess_nav']=row['nav']-b
    counter = execute(p,[genes[2]],manager)
    raw = reuse_benchmark(Path(__file__).parent/'artifacts/alpaca_repair_live_batch_20261029')
    sources = raw['sources']
    bars = [b for s in sources for b in json.loads(Path(s['source_file']).read_text()).get('bars',{}).get('QQQ',[])]
    raw.update(first_timestamp=min(b['t'] for b in bars),last_timestamp=max(b['t'] for b in bars),
               diagnosis='first_replay.run hard-coded absence; ingest handles requested stock gaps only and never discovers benchmark cache',
               blocker='Raw SIP OHLCV exists; explicit distributions, splits, normalization and availability reconciliation still required')
    output=Path(output); output.mkdir(parents=True,exist_ok=False)
    daily=[]
    for row in result['equity']:
        daily.append(dict(label='SYNTHETIC',**row,decision=next((e for e in result['events'] if e['date']==row['date']),dict(decision='TERMINAL_MARK_NO_NEW_ORDERS')),
                          fills=[f for f in result['fills'] if f['date']==row['date']]))
    report=dict(label='SYNTHETIC_NOT_HISTORICAL_PERFORMANCE',status='FUNCTIONAL_FIXTURE_EXECUTED',
                metrics=result['metrics'],audit=result['audit'],genes=list(map(asdict,genes)),manager=asdict(manager),
                counterfactual=dict(policy='generalist_only_same_account_and_gates',metrics=counter['metrics'],fills=counter['fills']),
                benchmark=dict(label='SYNTHETIC_FIXED_0.1_PERCENT_PER_SESSION',final_nav=benchmark[-1],excess_nav=result['metrics']['final_nav']-benchmark[-1]),
                drawdown_policy='8% hard acceptance ceiling; breach raises, never clips NAV. Next-open gap-proof prevention unavailable.',
                blockers=['No guarantee of 8% realized loss ceiling across arbitrary price gaps','Synthetic hand-authored signals do not prove feature estimation, model fitting or historical PIT eligibility'],long_generations=0)
    for name,value in [('report',report),('ledger',daily),('replay',result),('counterfactual',counter),('qqq_raw_audit',raw)]:
        (output/f'{name}.json').write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__); parser.add_argument('--output',required=True)
    print(json.dumps(run(parser.parse_args().output),indent=2))
