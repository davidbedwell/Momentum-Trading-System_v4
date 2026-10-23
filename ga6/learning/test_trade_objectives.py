"""Trade learning remains primary; portfolio results are separately certified."""
from ga6.learning.chronological_shadow_learning import chronological_shadow_scores
from ga6.learning.trial_rating import rate_trial

def test_cash_opportunity_cost_changes_trade_score():
    def row(name, ret, sessions):
        return {name: {"decisions": [
            {"decision_date":"2025-01-02","symbol":"AAA","evidence_cutoff":"2025-01-02",
             "action":"ENTER","features":{}}],
            "positions":{"completed":[{"entry_decision_date":"2025-01-02",
                "symbol":"AAA","exit_date":"2025-02-01",
                "holding_sessions":sessions,"net_return":ret}]}}}
    bank={**row("fast", .02, 2), **row("slow", .02, 35)}
    # Include a later decision to expose matured scores.
    bank["fast"]["decisions"].append({"decision_date":"2025-02-03","symbol":"BBB",
        "evidence_cutoff":"2025-02-03","action":"ENTER","features":{}})
    # The score snapshots are based on executed trade entry dates only.
    # Add a completed later trade whose outcome must remain unavailable.
    bank["fast"]["positions"]["completed"].append({"entry_decision_date":"2025-02-03",
        "symbol":"BBB","exit_date":"2025-02-10","holding_sessions":5,"net_return":.01})
    snapshots=chronological_shadow_scores(bank,niche="N",decision_start="2025-01-01",
        decision_end="2025-03-01",min_samples=1,annual_cash_yield=.05)
    assert snapshots[1]["leader"]=="fast"
    assert snapshots[1]["available_matured_labels"]==2
    assert "NOT_SHARED_PORTFOLIO" in snapshots[1]["status"]

def test_rating_does_not_mislabel_scaling_as_independent_fitness():
    def result(net, sessions):
        return {"decisions":[{"decision_date":"2025-01-02","symbol":"AAA","action":"ENTER"}],
            "positions":{"completed":[{"entry_decision_date":"2025-01-02","symbol":"AAA",
            "exit_date":"2025-02-01","net_return":net,"holding_sessions":sessions,
            "realized_pnl":net*1000,"gross_buy":1000,"scale_in_count":0,
            "scale_out_count":0}]}}
    output=rate_trial({"chromosomes":{"A":result(.02,2),"B":result(.02,35)}},
        start="2025-01-01",end="2025-03-01",as_of="2025-03-10",
        annual_cash_yield=.05)
    assert output["summary"]["A"]["avg_excess_return_over_cash"] > output["summary"]["B"]["avg_excess_return_over_cash"]
    assert "avg_pnl_per_gross_buy" not in output["summary"]["A"]
    assert "NO_CAUSAL_OR_SELECTOR_PROMOTION" in output["status"]
