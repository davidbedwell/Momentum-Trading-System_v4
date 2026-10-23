from ga6.learning.chronological_shadow_learning import chronological_shadow_scores

def candidate(chromosome,decision_date,exit_date,ret):
    return {str(chromosome):{"decisions":[dict(decision_date=decision_date,symbol="AAA",
        evidence_cutoff=decision_date,action="ENTER",features={"x":1})],
        "positions":{"completed":[dict(entry_decision_date=decision_date,symbol="AAA",
        exit_date=exit_date,net_return=ret,holding_sessions=5)]}}}

def test_same_day_outcome_excluded():
    bank=candidate(1,"2025-01-02","2025-01-10",.1)
    bank.update(candidate(2,"2025-01-10","2025-01-15",.2))
    rows=chronological_shadow_scores(bank,niche="N",decision_start="2025-01-01",
        decision_end="2025-02-01",min_samples=1)
    assert rows[1]["decision_date"]=="2025-01-10"
    assert rows[1]["available_matured_labels"]==0
    assert rows[1]["leader"] is None

def test_matured_label_affects_later_ranking():
    bank=candidate(1,"2025-01-02","2025-01-10",.1)
    bank.update(candidate(2,"2025-01-11","2025-01-15",.2))
    rows=chronological_shadow_scores(bank,niche="N",decision_start="2025-01-01",
        decision_end="2025-02-01",min_samples=1)
    assert rows[1]["available_matured_labels"]==1
    assert rows[1]["leader"]=="1"
