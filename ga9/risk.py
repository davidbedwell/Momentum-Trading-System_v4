"""Defined stop loss-at-risk; gaps can exceed this planned loss."""
import math
MAX_DRAWDOWN = 1.0  # research validity boundary, not a discovery drawdown gate
DRAWDOWN_REFERENCE = .08
PORTFOLIO_RISK_CAP = .02

def risk_feasible(max_drawdown):
    return bool(math.isfinite(max_drawdown) and 0 <= max_drawdown <= MAX_DRAWDOWN)

def stop_risk(value, price, stop):
    if not all(math.isfinite(x) for x in (value, price, stop)) or value < 0 or price <= 0 or stop < 0:
        raise ValueError('Invalid risk mark')
    return value * max(0., 1-stop/price)

def risk_budget(nav, cap, existing_risk, stop_distance):
    if not 0 <= cap <= PORTFOLIO_RISK_CAP or not 0 < stop_distance <= 1:
        raise ValueError('Risk cap must remain within 2%; positive stop distance required')
    return max(0., cap*nav-existing_risk)/stop_distance
