"""Frozen H.7 null provenance policy.

Numerical inequality is evidence, not the definition of conformance.
Only explicitly registered chronological exogenous/PIT stock context may be
carried unchanged. Stock-path and dynamic-peer fields must be rebuilt from
the completed synthetic path through production builders.
"""
CHRONOLOGICAL_EXOGENOUS_PIT_STOCK_CONTEXT=frozenset({
 "eligible",
 "earnings_surprise_pct__v1",
 "earnings_reported_eps__v1",
 "earnings_estimate_eps__v1",
 "earnings_event_count__v1",
 "earnings_timing_known__v1",
 "days_since_earnings__v1",
 "earnings_event_session__v1",
})

def classify_stock_feature(name:str)->str:
    if name in CHRONOLOGICAL_EXOGENOUS_PIT_STOCK_CONTEXT:
        return "chronological_exogenous_pit"
    return "synthetic_stock_path_rebuild_required"

def assert_stock_bank_provenance(stock_keys):
    keys=set(stock_keys)
    unknown_registered=CHRONOLOGICAL_EXOGENOUS_PIT_STOCK_CONTEXT-keys
    if unknown_registered:
        raise RuntimeError(f"NULL_PIT_REGISTRY_FIELD_MISSING:{sorted(unknown_registered)}")
    return True
