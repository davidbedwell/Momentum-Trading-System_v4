"""Research-only Horizons native long-side transitions to manager proposals.
Consumes actual decisions from horizons_signed_decisions.decide; never
fabricates rankings or permits unsupported shorts/reversals.
"""
from .native_signal_contract import NativeProposal

ACTION={'ENTER_LONG':'ENTER','ADD_LONG':'ADD','REDUCE_LONG':'REDUCE',
        'EXIT_LONG':'EXIT','HOLD':'HOLD'}


def from_horizons(decisions,*,decision_date,chromosome_id,trained_through,
                  source_hash,snapshot_hash,native_score_by_ticker):
    result=[]
    for ticker,transition in sorted(decisions.items()):
        action=transition['action']
        if action not in ACTION:
            raise ValueError('unsupported Horizons short/reversal action')
        target=float(transition['target_weight'])
        previous=float(transition['previous_weight'])
        if target<0 or previous<0:
            raise ValueError('short exposure unsupported')
        if target>.30:
            raise ValueError('target above native contract limit')
        if ticker not in native_score_by_ticker:
            raise ValueError('missing native score; no proxy permitted')
        result.append(NativeProposal(decision_date,ticker,'HORIZONS',chromosome_id,
            ACTION[action],target,float(native_score_by_ticker[ticker]),
            'native_horizon_score',source_hash,snapshot_hash,trained_through))
    return result
