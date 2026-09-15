import pytest

from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.derived_feature_factory import standard_outcome_feature_set
from MTS_V4.derived_market_evidence import derived_market_evidence_descriptor, universe_subject
from MTS_V4.derived_market_store import DerivedMarketQuery, InMemoryDerivedMarketStore, UniverseDefinition


def test_outcome_materialization_requires_explicit_historical_authorization():
    store = InMemoryDerivedMarketStore()
    store.register_universe(UniverseDefinition("u", "u", "fixture"))
    feature_set = standard_outcome_feature_set()
    store.register_feature_set(feature_set)
    row = {"security_id": "A", "effective_date": "2025-01-01", "eligible": True}
    row.update({column: 0.01 for column in feature_set.feature_columns})
    store.append_update(universe_id="u", feature_set_id=feature_set.feature_set_id, feature_set_version=feature_set.version, update_id="o1", rows=[row])
    query = DerivedMarketQuery("u", feature_set.feature_set_id, feature_set.version)
    subject = universe_subject(universe_id="u")
    with pytest.raises(ValueError, match="future/outcome"):
        derived_market_evidence_descriptor(store=store, cache=TemporaryResearchCache(), subject=subject, query=query)
    descriptor = derived_market_evidence_descriptor(
        store=store,
        cache=TemporaryResearchCache(),
        subject=subject,
        query=query,
        allow_future_outcomes=True,
    )
    assert descriptor.provenance["contains_future_outcomes"] is True
