"""Native GA6 action -> manager proposal bridge. Fail closed without
out-of-time calibrated evidence; no fabricated expected returns.
"""
from manager_policy_v2 import Proposal
from manager_policy_v3 import decide

NATIVE_TO_MANAGER={"ENTER":"ENTER","ADD":"INCREASE","SCALE_IN":"INCREASE",
                   "HOLD":"HOLD","REDUCE":"REDUCE","SCALE_OUT":"REDUCE",
                   "EXIT":"EXIT","REPLACE_CANDIDATE":"PASS"}

def proposal_from_native(ticker,chromosome_id,family,native_action,weight,
                         calibration=None,held_weight=0.):
    """Native SCALE_IN is an ADDITIONAL weight; SCALE_OUT is a fractional trim.
    Convert both to absolute portfolio target weights before manager scoring.
    """
    from math import isfinite
    weight=float(weight)
    held_weight=float(held_weight)
    if not isfinite(weight) or not isfinite(held_weight) or weight<0 or not 0<=held_weight<=1:
        raise ValueError('invalid native weight or holding')
    if native_action=='SCALE_IN':
        weight=held_weight+weight
    elif native_action=='SCALE_OUT':
        if weight>1:raise ValueError('invalid SCALE_OUT fraction')
        weight=held_weight*(1-weight)
    action=NATIVE_TO_MANAGER.get(native_action)
    if action is None:return None
    if calibration is None:
        return Proposal(ticker,chromosome_id,family,action,0.,0.,0.,
                        max(0.,float(weight)),False,0)
    required=("edge","downside","confidence","matured_samples","asof_session")
    if any(k not in calibration for k in required):raise ValueError("incomplete calibration")
    if calibration["matured_samples"]<=0:raise ValueError("no matured observations")
    return Proposal(ticker,chromosome_id,family,action,
                    float(calibration["edge"]),float(calibration["downside"]),
                    float(calibration["confidence"]),max(0.,float(weight)),
                    True,int(calibration["matured_samples"]))

def orders_from_native(native_rows,holdings,settled_cash,genes,defense=False):
    """Each native row: ticker,id,family,action,weight,calibration.
    Calibration must be computed from outcomes matured before decision time.
    """
    proposals=[]
    for t,c,f,a,w,cal in native_rows:
        p=proposal_from_native(t,c,f,a,w,cal,holdings.get(t,0.))
        if p is not None:proposals.append(p)
    if genes.max_total>0.10 or genes.max_initial>0.10:
        raise ValueError('learning-phase per-symbol cap must be <= 10%')
    return decide(proposals,holdings,settled_cash,genes,defense)
