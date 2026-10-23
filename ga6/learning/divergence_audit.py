"""Counterfactual divergence attribution without hindsight-driven promotion."""
from collections import defaultdict

def audit_divergences(bank_result, *, start, end, as_of):
    results=bank_result["chromosomes"]
    trades={}
    for chromosome,result in results.items():
        for trade in result["positions"]["completed"]:
            day=trade["entry_decision_date"]
            if start<=day<end and trade["exit_date"]<as_of:
                trades[(day,trade["symbol"],chromosome)]=trade
    groups=defaultdict(dict)
    for (day,symbol,chromosome),trade in trades.items():
        groups[(day,symbol)][chromosome]=trade
    audit=[]
    for (day,symbol),group in sorted(groups.items()):
        if len(group)<2: continue
        candidates=[]
        for chromosome,trade in sorted(group.items()):
            result=results[chromosome]
            relevant=[f for f in result["fills"]
                      if f["security"]==symbol
                      and trade["entry_date"]<=f["execution_date"]<=trade["exit_date"]]
            candidates.append(dict(chromosome=chromosome,
                entry_date=trade["entry_date"],exit_date=trade["exit_date"],
                net_return=trade["net_return"],realized_pnl=trade["realized_pnl"],
                gross_buy=trade["gross_buy"],fees=trade["fees"],
                holding_sessions=trade["holding_sessions"],
                scale_in_count=trade["scale_in_count"],
                scale_out_count=trade["scale_out_count"],
                fill_actions=[(f["execution_date"],f["side"],f["quantity"],
                               f["attribution_status"]) for f in relevant]))
        first=candidates[0]
        categories=[]
        if len({c["gross_buy"] for c in candidates})>1:categories.append("CAPITAL_SIZING")
        if len({c["entry_date"] for c in candidates})>1:categories.append("ENTRY_TIMING")
        if len({c["exit_date"] for c in candidates})>1:categories.append("EXIT_TIMING")
        if len({c["scale_in_count"] for c in candidates})>1:categories.append("SCALE_IN")
        if len({c["scale_out_count"] for c in candidates})>1:categories.append("SCALE_OUT")
        if len({tuple(c["fill_actions"]) for c in candidates})>1:categories.append("FILL_PATH")
        if len({round(c["net_return"],10) for c in candidates})>1:categories.append("NET_RETURN")
        audit.append(dict(decision_date=day,symbol=symbol,categories=categories,
                          candidates=candidates,
                          status="DESCRIPTIVE_NOT_CAUSAL_NOT_SELECTOR_TRAINING"))
    return audit
