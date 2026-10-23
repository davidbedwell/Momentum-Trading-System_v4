"""Trade-first GA6 evaluation from actual shadow trade records, independent of production."""
from math import log1p,isfinite
from statistics import mean,median
from collections import defaultdict

def assess_trades(trades,labels,assigned_niche,min_trades=50,min_months=10):
    groups={'global':[],'assigned':[],'other_identified':[],'unclassified':[]}
    for t in trades:
        v=float(t['net_return']);days=int(t['sessions'])
        if not isfinite(v) or v<=-1 or days<1:raise ValueError('Invalid trade')
        niche=labels.get((str(t['entry_date'])[:10],t['ticker']))
        groups['global'].append(t)
        groups['assigned' if niche==assigned_niche else 'other_identified' if niche is not None else 'unclassified'].append(t)
    def summarize(ts):
        n=len(ts);returns=[float(t['net_return']) for t in ts]
        months=len({str(t['entry_date'])[:7] for t in ts})
        quick=[t for t in ts if 2<=int(t['sessions'])<=20]
        winners=[t for t in quick if float(t['net_return'])>=.05]
        losers=[t for t in quick if float(t['net_return'])<=-.05]
        positive=[v for v in returns if v>0]
        negative=[v for v in returns if v<0]
        ev=mean(returns) if n else None
        logev=mean(log1p(v) for v in returns) if n else None
        tail=mean(sorted(returns)[:max(1,(n+19)//20)]) if n else None
        return {'count':n,'independent_months':months,'eligible':n>=min_trades and months>=min_months and ev>0 and logev>0,
                'net_ev':ev,'geometric_log_ev':logev,'worst_5pct_mean':tail,
                'win_rate':len(positive)/n if n else None,
                'median_return':median(returns) if n else None,
                'avg_sessions':mean(int(t['sessions']) for t in ts) if n else None,
                'ev_per_session':sum(returns)/sum(int(t['sessions']) for t in ts) if n else None,
                'quick_2_20_count':len(quick),'quick_5pct_winners':len(winners),
                'quick_5pct_losers':len(losers),
                'quick_5pct_win_frequency':len(winners)/len(quick) if quick else None,
                'quick_5pct_loss_frequency':len(losers)/len(quick) if quick else None,
                'mean_winner':mean(positive) if positive else None,
                'mean_loser':mean(negative) if negative else None}
    result={name:summarize(ts) for name,ts in groups.items()}
    assert sum(result[k]['count'] for k in ('assigned','other_identified','unclassified'))==result['global']['count']
    return result
