"""Controlling GA9 portfolio acceptance constraint; not a per-position stop."""
MAX_DRAWDOWN = 0.08


def risk_feasible(max_drawdown):
    return bool(0 <= max_drawdown <= MAX_DRAWDOWN)
