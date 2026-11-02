"""Owner-authenticated native risk reductions, independent of entry calibration.
An uncalibrated entry may not spend capital; a native risk exit must not be
silenced because its owner lacks matured performance observations.
"""
from engines.portfolio_replay.kernel import Signal
from .native_signal_contract import normalize_proposals


def mandatory_orders(native,as_of,holdings,owners):
    proposals=normalize_proposals(native,as_of)
    result={}
    for p in proposals:
        if p.action not in ('EXIT','REDUCE') or holdings.get(p.ticker,0)<=0:
            continue
        if owners.get(p.ticker)!=(p.family,p.chromosome_id):
            continue  # other chromosomes cannot liquidate an incumbent
        target=0. if p.action=='EXIT' else min(p.target_weight,holdings[p.ticker])
        old=result.get(p.ticker)
        if old is None or target<old.target_weight:
            result[p.ticker]=Signal(p.ticker,p.family,p.chromosome_id,target)
    return result
