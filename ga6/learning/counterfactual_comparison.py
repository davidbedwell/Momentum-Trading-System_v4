"""Match executed orders to verified time-t signal evidence.

Mandatory risk/defense fills can lack a discretionary EXIT signal. Those are
retained as execution-only events, never falsely attributed to a signal.
"""
from collections import defaultdict

def link_fills_to_signals(fills, decision_signals, *, run_id, chromosome_id):
    if not run_id or not chromosome_id:
        raise ValueError("missing run/chromosome identity")
    index={}
    for signal in decision_signals:
        key=(signal["decision_date"],signal["symbol"])
        if key in index:
            raise ValueError("duplicate signal identity")
        if signal["evidence_cutoff"]>signal["decision_date"]:
            raise ValueError("future signal evidence")
        index[key]=signal
    linked=[]
    for fill in fills:
        key=(str(fill["decision_date"])[:10],fill["security"])
        signal=index.get(key)
        if str(fill["execution_date"])[:10]<=key[0]:
            raise ValueError("nonchronological fill")
        if signal is None:
            status="EXECUTION_ONLY_NO_MATCHED_DISCRETIONARY_SIGNAL"
        elif (fill["side"]=="BUY" and signal["action"] in ("ENTER","SCALE_IN")) or (
            fill["side"]=="SELL" and signal["action"] in ("EXIT","SCALE_OUT","REPLACE_CANDIDATE")):
            status="SIGNAL_ACTION_MATCHED"
        else:
            status="EXECUTION_OVERRIDE_OR_RISK_EXIT"
        linked.append({**fill,
            "run_id":run_id,"chromosome_id":str(chromosome_id),
            "decision_id":f"{run_id}:{chromosome_id}:{key[0]}:{key[1]}",
            "signal":signal,"attribution_status":status})
    return linked

def compare_completed_shadow_trades(trades_by_chromosome, *, as_of):
    """Retrospective comparison only, not a live selection signal.

    Compares same symbol and original decision date; does not assert equal
    capital usage or identical exits, and cannot by itself prove regret.
    """
    grouped=defaultdict(list)
    for chromosome,trades in trades_by_chromosome.items():
        for trade in trades:
            if trade["exit_date"]>=as_of:
                continue
            key=(trade["symbol"],trade["entry_decision_date"])
            grouped[key].append(dict(chromosome=str(chromosome),
                                     net_return=trade["net_return"],
                                     realized_pnl=trade["realized_pnl"],
                                     holding_sessions=trade["holding_sessions"]))
    return [{"symbol":symbol,"decision_date":day,
             "candidates":sorted(rows,key=lambda x:x["net_return"],reverse=True),
             "comparison_status":"RETROSPECTIVE_SAME_OPPORTUNITY_NOT_CAPITAL_MATCHED"}
            for (symbol,day),rows in sorted(grouped.items()) if len(rows)>1]
