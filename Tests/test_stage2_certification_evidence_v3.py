from Core.layered_ga.stage2_certification_evidence_v3 import audit_evolutionary_ledger,audit_catastrophic_policy

def test_no_self_certification():
    assert audit_evolutionary_ledger({'method':'NSGA_II_TWO_OBJECTIVE_V3','independent_selection_audit':True})
    assert audit_catastrophic_policy({'independently_verified':True,'frozen_before_search':True})

def test_late_policy_fails():
    assert any('not frozen' in x for x in audit_catastrophic_policy({'frozen_at':'2026-10-09','search_started_at':'2026-10-08','policy_hash':'x','metrics':[1],'thresholds':[1],'provenance':'x','independent_recalculation':True}))
