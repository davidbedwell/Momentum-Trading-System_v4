"""Strict, append-only bridge from independently evaluated shadow trades to learning ledger.

An entry decision must be identified explicitly from a time-t decision snapshot.
No symbol-only or hindsight chromosome matching is permitted.
"""
from math import isfinite

def publish_matured_trades(ledger, *, reconciled, entry_decisions, chromosome_id,
                           niche, as_of, run_id):
    """Persist completed shadow trades; never overwrite existing decisions/outcomes.

    entry_decisions maps (symbol, entry_decision_date) to a saved decision snapshot:
    decision_id, asof, evidence_cutoff, features, proposal, action, selected.
    This must be collected at decision time, not reconstructed retrospectively.
    """
    if not run_id or not chromosome_id or not niche:
        raise ValueError("missing run, chromosome or niche identity")
    as_of = str(as_of)[:10]
    inserted = 0
    deferred = 0
    for trade in reconciled["completed"]:
        if trade["exit_date"] >= as_of:
            deferred += 1
            continue
        key = (trade["symbol"], trade["entry_decision_date"])
        if key not in entry_decisions:
            raise ValueError(f"missing original time-t decision snapshot for {key}")
        decision = entry_decisions[key]
        if decision["asof"] != trade["entry_decision_date"]:
            raise ValueError("decision snapshot date mismatch")
        if decision["evidence_cutoff"] > decision["asof"]:
            raise ValueError("future evidence")
        if decision["action"] != "ENTER":
            raise ValueError("non-entry decision mapped to trade")
        if trade["holding_sessions"] < 1 or trade["holding_sessions"] > 40:
            raise ValueError("invalid holding period")
        if not isfinite(trade["net_return"]) or not isfinite(trade["realized_pnl"]):
            raise ValueError("nonfinite trade outcome")
        ledger.record_decision(
            decision_id=decision["decision_id"], asof=decision["asof"],
            symbol=trade["symbol"], niche=niche, chromosome=int(chromosome_id),
            action="ENTER", features=decision["features"],
            proposal=decision["proposal"], selected=decision["selected"],
            evidence_cutoff=decision["evidence_cutoff"])
        ledger.record_outcome(
            decision_id=decision["decision_id"], outcome_asof=trade["exit_date"],
            net_return=trade["net_return"], holding_sessions=trade["holding_sessions"],
            realized_pnl=trade["realized_pnl"],
            details={"run_id":run_id,"chromosome_id":str(chromosome_id),
                     "entry_date":trade["entry_date"],"exit_date":trade["exit_date"],
                     "gross_buy":trade["gross_buy"],"gross_sell":trade["gross_sell"],
                     "fees":trade["fees"],"fill_count":trade["fill_count"],
                     "scale_in_count":trade["scale_in_count"],
                     "scale_out_count":trade["scale_out_count"]})
        inserted += 1
    return {"inserted":inserted,"deferred":deferred,
            "status":"MATURED_SHADOW_LABELS_STORED_NOT_SELECTOR_CERTIFIED"}
