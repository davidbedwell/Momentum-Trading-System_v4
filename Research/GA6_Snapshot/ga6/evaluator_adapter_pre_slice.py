"""GA6-only adapter. Never changes GA5 evaluator outputs or cache semantics."""
from math import isfinite,log1p
from statistics import mean
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent / "ga5_redesign"))
from ga6.guarded_evaluator_ga6 import evaluate as ga6_raw_evaluate

def enrich(result, trades, niche_labels=None):
    r=dict(result)
    n=len(trades)
    if n != int(r['shadow']['closed_trades']):
        raise ValueError('Shadow trade count mismatch')
    vals=[float(t['net_return']) for t in trades]
    if any(not isfinite(x) or x<=-1 for x in vals):
        raise ValueError('Invalid trade returns')
    gains=[x for x in vals if x>0];losses=[-x for x in vals if x<0]
    sessions=[int(t['sessions']) for t in trades]
    if any(s<1 for s in sessions):raise ValueError('Invalid holding sessions')
    ga6={'count':n,'net_ev':mean(vals) if n else None,
         'geometric_log_ev':mean(log1p(x) for x in vals) if n else None,
         'profit_factor':sum(gains)/sum(losses) if losses else (float('inf') if gains else None),
         'payoff_ratio':mean(gains)/mean(losses) if gains and losses else None,
         'ev_per_session':sum(vals)/sum(sessions) if sessions else None,
         'win_rate':len(gains)/n if n else None,
         'worst_5pct_mean':mean(sorted(vals)[:max(1,(n+19)//20)]) if n else None}
    if n:
        if abs(ga6['net_ev']-float(r['shadow']['mean_net_return']))>1e-10:
            raise ValueError('Shadow EV mismatch')
        if abs(ga6['win_rate']-float(r['shadow']['win_rate']))>1e-10:
            raise ValueError('Shadow win rate mismatch')
    from ga6.episode_uncertainty import assess
    r['ga6_episode_uncertainty']=assess(trades)
    r['ga6_trade_metrics']=ga6
    if niche_labels is not None:
        from ga6.niche_evidence import summarize
        from optimizer_v3 import NICHES
        r['ga6_niche_evidence']=summarize(trades,niche_labels,NICHES)
    return r

_INDEX_CACHE={}
def evaluate(*args, **kwargs):
    labels=kwargs.pop("evidence_labels",None)
    if labels is None:labels=kwargs.get("niche_labels")
    raw=ga6_raw_evaluate(*args, **kwargs)
    trades=raw["shadow"].pop("trades")
    result=enrich(raw,trades,labels)
    if args and trades:
        from ga6.path_replay import price_index,replay
        prepared=args[0]
        key=id(prepared)
        if key not in _INDEX_CACHE:
            _INDEX_CACHE.clear()
            _INDEX_CACHE[key]=price_index(prepared)
        result["ga6_exit_reentry_research"]=replay(trades,_INDEX_CACHE[key],fee=kwargs.get("fee",.001),cash_daily=(1+kwargs["annual_cash_yield"])**(1/252)-1)
    if args and trades:
        from ga6.prospective_replay import simulate
        from ga6.prospective_policy import Policy
        from ga6.chronological_validation import split
        paths=[]
        for tr in trades:
            rows=_INDEX_CACHE[key].get(tr['ticker'],[])
            begin=str(tr['entry_date'])[:10];end=str(tr['exit_date'])[:10]
            path=[row for row in rows if begin<=row[0]<=end]
            if len(path)>=3:paths.append(path)
        if paths:
            ordered=sorted(str(p[0][0])[:10] for p in paths)
            cutoff=ordered[(len(ordered)*7)//10]
            train,valid,excluded=split(paths,cutoff)
            daily=(1+kwargs['annual_cash_yield'])**(1/252)-1
            def summarize(group):
                reports=[simulate(path,Policy(),fee=kwargs.get('fee',.001),cash_daily=daily) for path in group]
                return {'count':len(reports),'mean_incremental':sum(x['incremental_net'] for x in reports)/len(reports) if reports else None}
            if len(train)>=50 and len(valid)>=50:
                from ga6.policy_evolution_oos import train_validate
                import random
                result['ga6_policy_oos']=train_validate(paths,random.Random(6106),cutoff,population=32,generations=5,fee=kwargs.get('fee',.001),cash_daily=daily)
            else:
                result['ga6_policy_oos']={'eligible':False,'train_count':len(train),'validation_count':len(valid)}
            result['ga6_prospective_baseline']={'cutoff':cutoff,'train':summarize(train),'validation':summarize(valid),'excluded':excluded,'policy':'fixed_baseline_not_evolved'}
    return result
