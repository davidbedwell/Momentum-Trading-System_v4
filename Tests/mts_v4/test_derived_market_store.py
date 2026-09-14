from __future__ import annotations

import pytest

from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.derived_market_evidence import derived_market_evidence_descriptor
from MTS_V4.derived_market_store import (
    DerivedFeatureDefinition,
    DerivedFeatureSetDefinition,
    DerivedMarketQuery,
    DerivedMarketStoreError,
    InMemoryDerivedMarketStore,
    ParquetDerivedMarketStore,
    UniverseDefinition,
    acquisition_start_for_plan,
    plan_incremental_update,
)
from MTS_V4.research_scope import universe_scope


def _definitions(store):
    store.register_universe(
        UniverseDefinition(
            universe_id="sp500_pit",
            description="Point-in-time S&P 500 research universe",
            membership_source="TEST_FIXTURE",
            point_in_time_membership_required=True,
        )
    )
    store.register_feature_set(
        DerivedFeatureSetDefinition(
            feature_set_id="core_daily",
            version="v1",
            description="Small fixture feature set",
            features=(
                DerivedFeatureDefinition(
                    feature_id="ret_252",
                    version="v1",
                    description="Trailing 252-session return",
                    dependencies=("close",),
                    required_lookback_sessions=252,
                    classification="PREDICTOR",
                ),
                DerivedFeatureDefinition(
                    feature_id="fwd_ret_20",
                    version="v1",
                    description="Forward 20-session return",
                    dependencies=("close",),
                    required_lookback_sessions=0,
                    classification="OUTCOME",
                    knowledge_timing="FUTURE_INFORMATION_HISTORICAL_ONLY",
                ),
            ),
        )
    )


def _rows(day: str, aapl: float, msft: float):
    return (
        {
            "security_id": "sec:AAPL",
            "effective_date": day,
            "eligible": True,
            "ret_252__v1": aapl,
            "fwd_ret_20__v1": 0.02,
        },
        {
            "security_id": "sec:MSFT",
            "effective_date": day,
            "eligible": True,
            "ret_252__v1": msft,
            "fwd_ret_20__v1": -0.01,
        },
    )


def test_in_memory_store_appends_and_queries_incrementally():
    store = InMemoryDerivedMarketStore()
    _definitions(store)
    first = store.append_update(
        universe_id="sp500_pit",
        feature_set_id="core_daily",
        feature_set_version="v1",
        update_id="u1",
        rows=_rows("2026-09-11", 0.20, 0.15),
        source_lineage={"fixture": True},
    )
    second = store.append_update(
        universe_id="sp500_pit",
        feature_set_id="core_daily",
        feature_set_version="v1",
        update_id="u2",
        rows=_rows("2026-09-14", 0.21, 0.16),
    )
    assert first.row_count == 2
    assert second.first_effective_date == "2026-09-14"
    state = store.state("sp500_pit", "core_daily", "v1")
    assert state.high_water_mark == "2026-09-14"

    rows = store.query(
        DerivedMarketQuery(
            universe_id="sp500_pit",
            feature_set_id="core_daily",
            feature_set_version="v1",
            start_date="2026-09-14",
            end_date="2026-09-14",
            security_ids=("sec:AAPL",),
            feature_columns=("ret_252__v1",),
        )
    )
    assert rows == (
        {
            "security_id": "sec:AAPL",
            "effective_date": "2026-09-14",
            "eligible": True,
            "ret_252__v1": 0.21,
        },
    )


def test_normal_update_cannot_overlap_high_water_mark():
    store = InMemoryDerivedMarketStore()
    _definitions(store)
    store.append_update(
        universe_id="sp500_pit",
        feature_set_id="core_daily",
        feature_set_version="v1",
        update_id="u1",
        rows=_rows("2026-09-11", 0.20, 0.15),
    )
    with pytest.raises(DerivedMarketStoreError, match="append-only"):
        store.append_update(
            universe_id="sp500_pit",
            feature_set_id="core_daily",
            feature_set_version="v1",
            update_id="u2",
            rows=_rows("2026-09-11", 0.25, 0.22),
        )


def test_parquet_store_persists_manifest_and_rows(tmp_path):
    root = tmp_path / "derived"
    store = ParquetDerivedMarketStore(root)
    _definitions(store)
    store.append_update(
        universe_id="sp500_pit",
        feature_set_id="core_daily",
        feature_set_version="v1",
        update_id="u1",
        rows=_rows("2026-09-11", 0.20, 0.15),
    )

    reopened = ParquetDerivedMarketStore(root)
    assert reopened.state("sp500_pit", "core_daily", "v1").high_water_mark == "2026-09-11"
    rows = reopened.query(
        DerivedMarketQuery(
            universe_id="sp500_pit",
            feature_set_id="core_daily",
            feature_set_version="v1",
            security_ids=("sec:MSFT",),
        )
    )
    assert len(rows) == 1
    assert rows[0]["security_id"] == "sec:MSFT"
    assert rows[0]["ret_252__v1"] == pytest.approx(0.15)


def test_incremental_planner_uses_feature_lookback_not_full_history():
    store = InMemoryDerivedMarketStore()
    _definitions(store)
    plan = plan_incremental_update(
        store=store,
        universe_id="sp500_pit",
        feature_set_id="core_daily",
        feature_set_version="v1",
        first_new_effective_date="2026-09-14",
        last_new_effective_date="2026-09-18",
    )
    assert plan.maximum_lookback_sessions == 252
    assert acquisition_start_for_plan(plan) < "2026-01-01"


def test_universe_scope_materializes_multi_security_evidence_without_ai_row_payload():
    store = InMemoryDerivedMarketStore()
    _definitions(store)
    store.append_update(
        universe_id="sp500_pit",
        feature_set_id="core_daily",
        feature_set_version="v1",
        update_id="u1",
        rows=_rows("2026-09-11", 0.20, 0.15),
    )
    cache = TemporaryResearchCache()
    subject = universe_scope("sp500_pit").to_subject_metadata(display_ticker="SP500")
    query = DerivedMarketQuery(
        universe_id="sp500_pit",
        feature_set_id="core_daily",
        feature_set_version="v1",
        feature_columns=("ret_252__v1",),
    )
    descriptor = derived_market_evidence_descriptor(
        store=store,
        cache=cache,
        subject=subject,
        query=query,
    )
    assert descriptor.subject_id == "universe:sp500_pit"
    assert descriptor.row_count == 2
    assert descriptor.evidence_type == "DERIVED_MARKET_PANEL"
    assert len(cache.get(descriptor.cache_key)) == 2
    assert "ret_252__v1" in descriptor.schema
