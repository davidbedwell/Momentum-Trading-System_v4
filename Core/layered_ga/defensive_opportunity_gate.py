"""Fail-closed Defensive opportunity policy, separate from market-state detector.

This pure policy module does not place orders, determine R-1, or infer a holding cutoff.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Decision:
    permitted: bool
    reason: str


def crash_transition_actions(crash_detected):
    """Ordered intentions; broker must confirm execution, never assume fills."""
    return ('cancel_conflicting_entries', 'liquidate_equity_to_cash') if crash_detected else ()


def evaluate_entry(*, defensive, direction, planned_horizon, max_defensive_horizon,
                   validated_defensive_strategy, independent_signal_pass,
                   risk_pass, borrow_available=None, quoted_borrow_rate=None):
    if direction not in ('LONG', 'SHORT'):
        return Decision(False, 'invalid_direction')
    if not isinstance(planned_horizon, int) or isinstance(planned_horizon, bool) or planned_horizon < 1:
        return Decision(False, 'invalid_horizon')
    if defensive:
        if max_defensive_horizon is None or not isinstance(max_defensive_horizon, int) or isinstance(max_defensive_horizon, bool) or max_defensive_horizon < 1:
            return Decision(False, 'unfrozen_defensive_horizon')
        if planned_horizon > max_defensive_horizon:
            return Decision(False, 'defensive_horizon_exceeded')
        if not validated_defensive_strategy:
            return Decision(False, 'defensive_strategy_not_validated')
    if not independent_signal_pass or not risk_pass:
        return Decision(False, 'signal_or_risk_failed')
    if direction == 'SHORT':
        if not borrow_available or quoted_borrow_rate is None or not 0 <= quoted_borrow_rate <= 0.06:
            return Decision(False, 'borrow_not_eligible')
    return Decision(True, 'eligible_for_order_checks')
