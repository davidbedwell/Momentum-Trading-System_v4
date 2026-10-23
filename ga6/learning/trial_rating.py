"""Research-only capital-aware counterfactual rating and coverage audit.

Not a causal estimate: each genome has independently funded fills. Missing
execution is NOT evidence that a genome chose to abstain.
"""
from collections import defaultdict
from statistics import mean

def rate_trial(bank_result, *, start, end, as_of):
    groups=defaultdict(dict)
    coverage=defaultdict(dict)
    for chromosome,result in bank_result["chromosomes"].items():
        for signal in result["decisions"]:
            day=signal["decision_date"]
            if start<=day<end and signal["action"]=="ENTER":
                coverage[(day,signal["symbol"])][chromosome]="SIGNALLED_ENTRY"
        for trade in result["positions"]["completed"]:
            day=trade["entry_decision_date"]
            if start<=day<end and trade["exit_date"]<as_of:
                groups[(day,trade["symbol"])][chromosome]=trade
                coverage[(day,trade["symbol"])][chromosome]="COMPLETED_EXECUTION"
    names=list(bank_result["chromosomes"])
    records=[]
    for (day,symbol),trades in sorted(groups.items()):
        if len(trades)<2:continue
        # Normalize realized P&L to gross capital purchased. This captures
        # scaling expenditure but not holding-period or mark-to-market risk.
        measures={name:dict(net_return=float(t["net_return"]),
            pnl_per_gross_buy=float(t["realized_pnl"])/float(t["gross_buy"]),
            realized_pnl=float(t["realized_pnl"]),
            gross_buy=float(t["gross_buy"]),
            scale_ins=int(t["scale_in_count"]),
            scale_outs=int(t["scale_out_count"]),
            holding_sessions=int(t["holding_sessions"]))
            for name,t in trades.items() if t["gross_buy"]>0}
        if len(measures)<2:continue
        best_return=max(v["net_return"] for v in measures.values())
        best_efficiency=max(v["pnl_per_gross_buy"] for v in measures.values())
        records.append(dict(decision_date=day,symbol=symbol,
            candidates=measures,best_return=best_return,
            best_efficiency=best_efficiency))
    summary={}
    for name in names:
        eligible=[r for r in records if name in r["candidates"]]
        if eligible:
            summary[name]=dict(matched_trades=len(eligible),
                avg_net_return=mean(r["candidates"][name]["net_return"] for r in eligible),
                avg_pnl_per_gross_buy=mean(r["candidates"][name]["pnl_per_gross_buy"] for r in eligible),
                mean_return_regret=mean(r["best_return"]-r["candidates"][name]["net_return"] for r in eligible),
                mean_efficiency_regret=mean(r["best_efficiency"]-r["candidates"][name]["pnl_per_gross_buy"] for r in eligible),
                return_wins=sum(abs(r["best_return"]-r["candidates"][name]["net_return"])<1e-10 for r in eligible))
        else:summary[name]=dict(matched_trades=0)
    incomplete=defaultdict(int)
    for key,statuses in coverage.items():
        for name in names:
            if name not in statuses:incomplete["NO_ENTER_SIGNAL_OR_NO_COMPLETED_TRADE_"+name]+=1
            elif statuses[name]=="SIGNALLED_ENTRY":incomplete["SIGNAL_WITHOUT_MATURE_COMPLETED_EXECUTION_"+name]+=1
    return dict(summary=summary,matched_opportunities=len(records),
        signalled_or_completed_opportunities=len(coverage),
        incomplete_coverage=dict(incomplete),
        status="RESEARCH_ONLY_INDEPENDENT_CAPITAL_NO_CAUSAL_OR_SELECTOR_PROMOTION")
