"""Research adapter from calibrated V3 manager decisions to replay orders.
Only decisions already backed by matured calibration may reach this adapter.
Replacement sale proceeds remain unavailable to same-open buys in Replay.
"""
from math import isfinite
from engines.portfolio_replay.kernel import Signal
from .manager_policy_v3 import decide
from .progressive_scaling import ScaleEvidence


def orders(proposals,holdings,settled_cash,genes,defense=False,scaling=None):
    decisions=decide(proposals,holdings,settled_cash,genes,defense=defense)
    result=[]
    for ticker,(action,target,owner) in decisions.items():
        if not isinstance(target,(int,float)) or not isfinite(target) or not 0<=target<=1:
            raise ValueError('invalid target')
        if action not in ('ENTER','INCREASE','REDUCE','EXIT'):
            raise ValueError('unsupported manager action')
        scale=None
        if action in ('ENTER','INCREASE') and target>0.10:
            if action!='INCREASE' or holdings.get(ticker,0)<=0:
                raise ValueError('unverified scaling above learning cap')
            scale=(scaling or {}).get((ticker,owner))
            if not isinstance(scale,dict) or not isinstance(scale.get('evidence'),ScaleEvidence):
                raise ValueError('unverified scaling above learning cap')
            if scale.get('stop_distance') is None or scale.get('gap_risk') is None:
                raise ValueError('scaling risk inputs required')
        if action in ('EXIT','REDUCE') and ticker not in holdings:
            raise ValueError('cannot reduce an absent position')
        result.append(Signal(ticker,'MANAGER',owner,target,
            scaling_evidence=scale['evidence'] if scale else None,
            stop_distance=scale['stop_distance'] if scale else None,
            gap_risk=scale['gap_risk'] if scale else None,
            other_equity_risk=scale.get('other_equity_risk',0.) if scale else 0.))
    return result
