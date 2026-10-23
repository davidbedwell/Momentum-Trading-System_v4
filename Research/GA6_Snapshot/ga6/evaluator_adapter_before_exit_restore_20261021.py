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
    return result
