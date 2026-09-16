from __future__ import annotations

from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.context_enriched_revisit import build_context_enriched_revisit_evidence
from MTS_V4.contracts import SubjectMetadata
from MTS_V4.derived_market_store import (
    DerivedFeatureDefinition,
    DerivedFeatureSetDefinition,
    InMemoryDerivedMarketStore,
    UniverseDefinition,
)


def _store() -> InMemoryDerivedMarketStore:
    store = InMemoryDerivedMarketStore()
    store.register_universe(UniverseDefinition(
        universe_id="current",
        description="current members",
        membership_source="fixture",
        point_in_time_membership_required=True,
    ))
    store.register_feature_set(DerivedFeatureSetDefinition(
        feature_set_id="predictors", version="v1", description="predictors",
        features=(
            DerivedFeatureDefinition("momentum", "v1", "momentum", classification="PREDICTOR"),
            DerivedFeatureDefinition("breadth", "v1", "breadth", classification="CONTEXT"),
        ),
    ))
    store.register_feature_set(DerivedFeatureSetDefinition(
        feature_set_id="earnings", version="v1", description="earnings",
        features=(DerivedFeatureDefinition(
            "surprise", "v1", "surprise", classification="PREDICTOR",
        ),),
    ))
    store.register_feature_set(DerivedFeatureSetDefinition(
        feature_set_id="outcomes", version="v1", description="outcomes",
        features=(DerivedFeatureDefinition(
            "forward", "v1", "forward", classification="OUTCOME",
            knowledge_timing="FUTURE_INFORMATION_HISTORICAL_ONLY",
        ),),
    ))
    predictors = []
    outcomes = []
    for date, aapl, msft, xom in (
        ("2026-01-02", 1.0, 2.0, 4.0),
        ("2026-01-05", 2.0, 4.0, 8.0),
    ):
        for security, value in (("AAPL", aapl), ("MSFT", msft), ("XOM", xom)):
            predictors.append({
                "security_id": security, "effective_date": date, "eligible": True,
                "momentum__v1": value, "breadth__v1": 2 / 3,
            })
            outcomes.append({
                "security_id": security, "effective_date": date, "eligible": True,
                "forward__v1": value / 100,
            })
    store.append_update(
        universe_id="current", feature_set_id="predictors", feature_set_version="v1",
        update_id="p", rows=predictors,
    )
    store.append_update(
        universe_id="current", feature_set_id="outcomes", feature_set_version="v1",
        update_id="o", rows=outcomes,
    )
    store.append_update(
        universe_id="current", feature_set_id="earnings", feature_set_version="v1",
        update_id="e", rows=({
            "security_id": "AAPL", "effective_date": "2026-01-05", "eligible": True,
            "surprise__v1": 4.2,
        },),
    )
    return store


def test_builds_uniform_time_aligned_subject_market_and_sector_context() -> None:
    cache = TemporaryResearchCache()
    evidence = build_context_enriched_revisit_evidence(
        store=_store(), cache=cache,
        subject=SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL"),
        universe_id="current", security_id="AAPL", sector_id="TECH",
        security_sector_ids={"AAPL": "TECH", "MSFT": "TECH", "XOM": "ENERGY"},
        predictor_feature_set_id="predictors", predictor_feature_set_version="v1",
        outcome_feature_set_id="outcomes", outcome_feature_set_version="v1",
        earnings_feature_set_id="earnings", earnings_feature_set_version="v1",
    )
    context, outcomes, earnings = evidence
    rows = cache.get(context.cache_key)
    assert len(rows) == 2
    assert rows[0]["subject__momentum__v1"] == 1.0
    assert rows[0]["market_median__momentum__v1"] == 2.0
    assert rows[0]["current_sector_median__momentum__v1"] == 1.5
    assert context.provenance["historical_membership_classification"] == "CURRENT_MEMBER_CONDITIONED"
    assert context.provenance["historical_outcomes_present"] is False
    assert context.provenance["source_high_water_mark"] == "2026-01-05"
    assert outcomes.provenance["contains_future_outcomes"] is True
    assert outcomes.provenance["source_high_water_mark"] == "2026-01-05"
    assert {row["security_id"] for row in cache.get(outcomes.cache_key)} == {"AAPL"}
    assert cache.get(earnings.cache_key)[0]["surprise__v1"] == 4.2
    assert earnings.provenance["unknown_timing_conservatively_delayed"] is True
