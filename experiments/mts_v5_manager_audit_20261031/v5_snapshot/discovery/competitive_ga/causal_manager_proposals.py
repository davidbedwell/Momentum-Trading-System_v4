"""Convert native decisions to comparable manager proposals only after
strictly earlier matured chromosome outcomes exist. No native-score mixing.
"""
from .causal_calibration import Calibrator
from .manager_policy_v2 import Proposal
from .native_signal_contract import normalize_proposals

ACTIONS={'ENTER':'ENTER','ADD':'INCREASE','HOLD':'HOLD',
         'REDUCE':'REDUCE','EXIT':'EXIT'}


def calibrated_proposals(native,as_of,session,calibrator,context=None):
    if not isinstance(calibrator,Calibrator):
        raise TypeError('causal calibrator required')
    result=[]
    for p in normalize_proposals(native,as_of):
        family_context=tuple(context) if context is not None else ((p.family+'_ENTRY',) if p.action in ('ENTER','HOLD') else (p.family+'_UTILITY',p.action))
        estimate=calibrator.estimate(p.chromosome_id,family_context,session)
        if estimate is None:
            continue  # shadow-only; never allocate capital on missing evidence
        result.append(Proposal(p.ticker,p.chromosome_id,p.family,
            ACTIONS[p.action],estimate['edge'],estimate['downside'],
            estimate['confidence'],p.target_weight,True,
            estimate['matured_samples']))
    return result
