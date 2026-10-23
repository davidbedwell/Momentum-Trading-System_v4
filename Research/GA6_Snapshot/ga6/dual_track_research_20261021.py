"""GA6 independent dual-track research ranking, never production fitness.
Trade-first; niche specialists require within-niche evidence. No CAGR target.
"""
from math import isfinite,log1p
from statistics import mean
from collections import defaultdict

def safe(x):
    return x is not None and isfinite(float(x))

def trade_quality(m, uncertainty=None, min_count=50, min_months=10):
    n=int(m.get('count') or 0)
    months=int((uncertainty or {}).get('independent_months') or m.get('episodes') or 0)
    ev=m.get('net_ev')
    lg=m.get('geometric_log_ev',m.get('log_ev'))
    tail=m.get('worst_5pct_mean',m.get('tail_5pct'))
    if n<min_count or months<min_months:
        return {'eligible':False,'reason':'INSUFFICIENT_TRADES_OR_EPISODES','count':n,'months':months}
    if not all(safe(v) for v in (ev,lg,tail)):
        return {'eligible':False,'reason':'MISSING_METRICS','count':n,'months':months}
    if ev<=0 or lg<=0:
        return {'eligible':False,'reason':'NONPOSITIVE_EV','count':n,'months':months}
    # No hard winner threshold: protect rare large winners, but penalize severe tails.
    # Log EV captures multiplicative loss asymmetry; no portfolio CAGR/MDD optimization.
    # Saturate arithmetic EV to prevent single giant winners overwhelming the ranking.
    score=100*(min(ev,.25)+2*min(lg,.25)+.5*max(tail,-1))
    if uncertainty and uncertainty.get('eligible'):
        if not uncertainty.get('robust_positive',False):
            return {'eligible':False,'reason':'BOOTSTRAP_NOT_ROBUST','count':n,'months':months,'score':score}
    return {'eligible':True,'score':score,'count':n,'months':months,
            'net_ev':ev,'log_ev':lg,'tail_5pct':tail,'win_rate':m.get('win_rate'),
            'ev_per_session':m.get('ev_per_session') if safe(m.get('ev_per_session')) else 0.,
            'payoff_ratio':m.get('payoff_ratio') if safe(m.get('payoff_ratio')) else 0.}

def rank_tracks(rows,niches):
    global_rank=[]
    specialists={n:[] for n in niches}
    for x in rows:
        cid=x['chromosome_id']
        result=x['result']
        global_quality=trade_quality(result['ga6_trade_metrics'],result.get('ga6_episode_uncertainty'))
        if global_quality['eligible']:
            global_rank.append({'id':cid,'origin':x['origin_niche'],'metrics':global_quality})
        for n in niches:
            m=result['ga6_niche_evidence'][n]
            # Specialization is only credited for chromosome's assigned niche.
            if n!=x['origin_niche']:continue
            specialist=trade_quality(m,min_count=50,min_months=10)
            if specialist['eligible']:
                specialists[n].append({'id':cid,'origin':n,'metrics':specialist})
    global_rank.sort(key=lambda x:(-x['metrics']['score'],x['id']))
    for n in niches:specialists[n].sort(key=lambda x:(-x['metrics']['score'],x['id']))
    return {'generalist':global_rank,'specialists':specialists,
            'principle':'Independent tracks: no outside-niche gains credited to specialist ranking'}
