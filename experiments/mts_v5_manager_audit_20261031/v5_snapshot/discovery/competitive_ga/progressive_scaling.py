"""Risk-gated progressive position scaling for research allocations."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class ScaleEvidence:
    matured_trades: int
    forward_folds: int
    positive_net_ev: bool
    historical_mdd: float
    current_signal_confirmed: bool
    position_profitable: bool
    independent_confirmation: bool

def allowed_target(current_weight,requested_weight,evidence,*,stop_distance,gap_risk,other_equity_risk=0.,max_equity_risk=.02):
    """Reject unsafe scaling; never manufacture a 30% initial entry."""
    if not isinstance(evidence,ScaleEvidence):raise TypeError("evidence required")
    vals=(current_weight,requested_weight,stop_distance,gap_risk,other_equity_risk,max_equity_risk,evidence.historical_mdd)
    if any(not isfinite(v) for v in vals) or any(v<0 for v in vals):raise ValueError("invalid risk inputs")
    if current_weight>0.30 or requested_weight>0.30 or max_equity_risk>.02 or evidence.historical_mdd>1:
        raise ValueError("risk bounds")
    initial=current_weight==0
    cap=.10
    exceptional=(evidence.matured_trades>=100 and evidence.forward_folds>=3
                 and evidence.positive_net_ev and evidence.historical_mdd<=.15
                 and evidence.independent_confirmation)
    if not initial and evidence.position_profitable and evidence.current_signal_confirmed:
        if exceptional:cap=.30
        elif evidence.matured_trades>=50 and evidence.forward_folds>=2 and evidence.positive_net_ev and evidence.historical_mdd<=.20:cap=.20
        elif evidence.matured_trades>=30 and evidence.positive_net_ev:cap=.15
    # Conservative risk exposure: include existing risk and possible overnight gap.
    per_dollar=max(stop_distance,gap_risk)
    remaining=max(0.,max_equity_risk-other_equity_risk)
    risk_cap=remaining/per_dollar if per_dollar>0 else 0.
    return min(requested_weight,cap,risk_cap)
