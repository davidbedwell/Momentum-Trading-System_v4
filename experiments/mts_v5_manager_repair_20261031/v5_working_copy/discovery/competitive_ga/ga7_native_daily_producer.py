"""GA7 close decisions using executed held state and optional native callbacks.

Decision thresholds follow ga7/request_replay.py. Authenticated proposals still
require actual training lineage; raw decisions can be audited independently.
"""
from math import isfinite
from .native_signal_contract import NativeProposal


def decision(genome, bar, position=None, *, defensive=False, niche_group='NON_NICHE',
             signal_evaluator=None, strength_evaluator=None):
    if genome.operator not in ('AND','OR'):raise ValueError('unsupported GA7 operator')
    if not 0<genome.entry_pct<=.10:raise ValueError('invalid native entry fraction')
    if not isinstance(niche_group,str) or not niche_group:raise ValueError('explicit GA7 niche group required')
    if position is None and (defensive or not bar.get('eligible',False)):return None
    features=bar.get('features',{})
    if genome.feature_a not in features or genome.feature_b not in features:
        raise ValueError('missing native GA7 features')
    a=float(features[genome.feature_a]);b=float(features[genome.feature_b])
    if not isfinite(a) or not isfinite(b):
        if position is None:return None
        raise ValueError('nonfinite held-position feature')
    signal=((a>=(genome.threshold_a+1)/2) and (b>=(genome.threshold_b+1)/2)) if genome.operator=='AND' else ((a>=(genome.threshold_a+1)/2) or (b>=(genome.threshold_b+1)/2))
    if signal_evaluator is not None:signal=bool(signal_evaluator(genome,bar))
    if niche_group!='NON_NICHE':
        if 'controlling_niche' not in bar:raise ValueError('missing GA7 controlling niche')
        signal=signal and bar['controlling_niche']==niche_group
    strength=(a+b)/2 if strength_evaluator is None else float(strength_evaluator(genome,bar))
    if not isfinite(strength):raise ValueError('invalid native GA7 strength')
    if position is None:
        return ('ENTER',float(genome.entry_pct)) if signal else None
    entry=float(position['entry']);stop=float(position.get('initial_stop',genome.stop_pct))
    close=float(bar['close']);weight=float(position['weight'])
    if not all(isfinite(v) for v in (entry,stop,close,weight)) or entry<=0 or close<=0 or not 0<stop<=.02 or not 0<weight<=1.:
        raise ValueError('invalid held-position state')
    pnl=close/entry-1
    exit_now=(defensive or pnl<=-stop or
        (genome.exit_rule=='signal_decay' and not signal) or
        (genome.exit_rule=='reversal' and pnl<-.005) or
        (genome.exit_rule=='volatility' and abs(pnl)>.04))
    if exit_now:return 'EXIT',0.
    if strength>.75 and pnl>.03 and weight<.30:return 'ADD',min(.30,weight+.03)
    if pnl<-.01 or strength<.45:return 'REDUCE',weight/2
    return 'HOLD',weight


def produce(genome,bars,*,decision_date,trained_through,source_hash,
            snapshot_hash,chromosome_id=None,defensive=False,held=None,niche_group='NON_NICHE',
            signal_evaluator=None,strength_evaluator=None):
    cid=chromosome_id or genome.identity()
    if not cid or not source_hash or not snapshot_hash:raise ValueError('missing GA7 provenance')
    # Validate genome even when the dated universe is empty.
    if genome.operator not in ('AND','OR'):raise ValueError('unsupported GA7 operator')
    if not 0<genome.entry_pct<=.10:raise ValueError('invalid native entry fraction')
    if not isinstance(niche_group,str) or not niche_group:raise ValueError('explicit GA7 niche group required')
    held=held or {}
    if set(held)-set(bars):raise ValueError('held ticker missing session bar')
    result=[]
    for ticker,bar in sorted(bars.items()):
        value=decision(genome,bar,held.get(ticker),defensive=defensive,niche_group=niche_group,
            signal_evaluator=signal_evaluator,strength_evaluator=strength_evaluator)
        if value is None:continue
        action,target=value
        result.append(NativeProposal(decision_date,ticker,'GA7',cid,action,
            target,0.,'net_return_fraction',source_hash,snapshot_hash,trained_through))
    return result
