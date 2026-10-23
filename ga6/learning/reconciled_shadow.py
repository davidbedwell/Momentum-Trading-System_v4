"""Verify captured reference execution and produce auditable matured trade outcomes.

No learning labels are exposed until the actual closing fill date.
"""
from ga6.learning.position_lifecycle import reconstruct_positions

def reconcile_shadow(capture, session_dates, *, max_sessions=40):
    metrics = capture["metrics"]
    fills = capture["fills"]
    actions = capture["corporate_actions"]
    session_index = {str(day)[:10]:i for i,day in enumerate(session_dates)}
    if len(session_index) != len(session_dates):
        raise ValueError("duplicate sessions")
    if list(session_index) != sorted(session_index):
        raise ValueError("nonchronological sessions")
    result = reconstruct_positions(fills,session_index=session_index,
                                   corporate_actions=actions,max_sessions=max_sessions)
    if len(fills) != metrics["fills"] or len(actions) != metrics["corporate_actions"]:
        raise ValueError("reference event count mismatch")
    if abs(result["dividend_cash"]-metrics["reconciliation"]["dividend_cash"])>1e-6:
        raise ValueError("dividend ledger mismatch")
    if abs(sum(x["fee"] for x in fills)-metrics["reconciliation"]["fees"])>1e-6:
        raise ValueError("fee ledger mismatch")
    if len(result["completed"]) != metrics["ga6_completed_position_metrics"]["completed_trades"]:
        raise ValueError("completed position count mismatch")
    return result

def matured_outcomes(reconciled, *, as_of):
    """Only positions whose closing execution has occurred are visible."""
    as_of = str(as_of)[:10]
    return [dict(t, label_available_date=t["exit_date"])
            for t in reconciled["completed"] if t["exit_date"] < as_of]
