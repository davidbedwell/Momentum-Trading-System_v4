"""Discovery-only measured trade fitness; not certified production fitness.
Explicit fold panels and verified earnings inputs are required by the caller.
"""
import math
from historical_bridge import evaluate_chromosome
from discovery_fitness import validate

def measured_discovery_fitness(genome, folds, schedules, verified_tickers, *, minimum_completed=1, initial_cash=100000):
    if len(folds)<2:raise ValueError('at least two chronological discovery folds required')
    if minimum_completed<1:raise ValueError('minimum completed trades must be positive')
    spans=[];results=[]
    for fold in folds:
        bars=fold['bars'];start=str(bars.date.min())[:10];end=str(bars.date.max())[:10]
        if start>=end:raise ValueError('invalid fold span')
        spans.append((start,end))
        results.append(evaluate_chromosome(genome,bars,schedules,verified_tickers,end,initial_cash=initial_cash))
    if any(spans[i][1]>=spans[i+1][0] for i in range(len(spans)-1)):
        raise ValueError('overlapping or unordered discovery folds')
    counts=[len(r['completed_trades']) for r in results]
    if sum(counts)<minimum_completed:raise ValueError('insufficient completed trades; no EV')
    pnl=[t['net_pnl'] for r in results for t in r['completed_trades']]
    # Net EV is mean fractional net return on actual committed trade capital.
    returns=[t['net_return'] for r in results for t in r['completed_trades']]
    fold_ev=[sum(t['net_return'] for t in r['completed_trades'])/len(r['completed_trades']) if r['completed_trades'] else 0.0 for r in results]
    # Calendar-session opportunity coverage is measured by days with filled entries.
    coverage=sum(len(set(r['trades'].loc[r['trades'].side=='buy','date'])) for r in results if not r['trades'].empty)/sum(len(f['bars'].date.unique()) for f in folds)
    out={'net_ev':sum(returns)/len(returns),
         'ev_per_session':sum(pnl)/(initial_cash*sum(len(f['bars'].date.unique()) for f in folds)),
         'reliability':sum(x>0 for x in fold_ev)/len(fold_ev),
         'training_consistency':1/(1+(max(fold_ev)-min(fold_ev))),
         'opportunity_coverage':min(1.0,coverage)}
    return validate(out)
