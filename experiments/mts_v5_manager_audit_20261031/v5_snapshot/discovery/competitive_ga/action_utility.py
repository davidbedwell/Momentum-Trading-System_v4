"""Paired held-state intervention utility, separately from entry returns.

Fixed next-open intervention versus HOLD; both marked at the same later close.
No future native decision or terminal exit is substituted for the intervention.
"""
from math import isfinite
from .causal_calibration import TradeOutcome


def paired(*, chromosome, family, action, decision, maturity, training_end,
           cash, shares, target, execution_open, terminal_close, fee=.001):
    if action not in ('ADD','REDUCE','EXIT') or not 0 <= decision < maturity <= training_end:
        raise ValueError('authorized chronological training intervention required')
    values=(cash,shares,target,execution_open,terminal_close,fee)
    if not all(isfinite(v) for v in values) or cash < 0 or shares <= 0 or min(execution_open,terminal_close)<=0 or not 0<=fee<1 or not 0<=target<=1:
        raise ValueError('invalid held counterfactual')
    equity=cash+shares*execution_open
    desired=target*equity/execution_open
    delta=desired-shares
    if action=='EXIT': delta=-shares
    if action=='ADD': delta=min(max(0.,delta),cash/(execution_open*(1+fee)))
    else: delta=min(0.,delta)
    action_cash=cash-delta*execution_open-abs(delta)*execution_open*fee
    baseline=cash+shares*terminal_close
    intervention=action_cash+(shares+delta)*terminal_close
    utility=(intervention-baseline)/equity
    return TradeOutcome(chromosome,(family+'_UTILITY',action),decision,maturity,utility,'shadow')
