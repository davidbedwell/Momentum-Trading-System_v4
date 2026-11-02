"""V5 manager capital-risk and profit-giveback accounting (research).

Stop risk is loss of invested capital relative to weighted cost basis, NOT
loss of unrealized gains. Portfolio drawdown is a separate equity-peak metric.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class AllocationPolicy:
    favorable_exposure_target: float = .70
    preferred_initial_min: float = .07
    preferred_initial_max: float = .10
    max_position_capital_loss: float = .02
    max_portfolio_drawdown: float = .20
    max_gross_exposure: float = 1.0

    def __post_init__(self):
        values=(self.favorable_exposure_target,self.preferred_initial_min,
                self.preferred_initial_max,self.max_position_capital_loss,
                self.max_portfolio_drawdown,self.max_gross_exposure)
        if not all(isfinite(x) and 0<=x<=1 for x in values):
            raise ValueError('invalid allocation policy')
        if self.preferred_initial_min>self.preferred_initial_max:
            raise ValueError('initial position bounds')


def position_risk(*,shares,average_cost,current_price,protective_exit,portfolio_equity,peak_price=None,gap_exit=None):
    """Separate principal-at-risk, mark-to-stop loss, and profit giveback.

    Stop/gap estimates are not guaranteed fills. Includes open profit only in
    mark-to-stop and giveback, not in loss of original position capital.
    """
    values=(shares,average_cost,current_price,protective_exit,portfolio_equity)
    if gap_exit is not None: values+= (gap_exit,)
    if peak_price is not None: values+=(peak_price,)
    if not all(isfinite(x) and x>=0 for x in values) or portfolio_equity<=0:
        raise ValueError('invalid position values')
    effective_exit=min(protective_exit,gap_exit) if gap_exit is not None else protective_exit
    principal_loss=max(0.,shares*(average_cost-effective_exit))/portfolio_equity
    mark_loss=max(0.,shares*(current_price-effective_exit))/portfolio_equity
    giveback=max(0.,shares*((peak_price if peak_price is not None else current_price)-effective_exit))/portfolio_equity
    return {'capital_loss_fraction':principal_loss,'mark_to_exit_fraction':mark_loss,
            'profit_giveback_fraction':giveback,
            'within_two_percent':principal_loss<=.02+1e-12}


def allowable_additional_shares(*,existing_shares,average_cost,add_price,protective_exit,portfolio_equity,max_loss_fraction=.02):
    """Risk-budget add sizing; assumes an unchanged protective exit and no fees.

    Caller must account for fees, gap stress, correlation and total cash separately.
    """
    v=(existing_shares,average_cost,add_price,protective_exit,portfolio_equity,max_loss_fraction)
    if not all(isfinite(x) and x>=0 for x in v) or portfolio_equity<=0 or max_loss_fraction>1:
        raise ValueError('invalid sizing inputs')
    remaining=portfolio_equity*max_loss_fraction-existing_shares*max(0.,average_cost-protective_exit)
    per_share=max(0.,add_price-protective_exit)
    if remaining<=0:return 0.
    if per_share==0:return float('inf')
    return remaining/per_share
