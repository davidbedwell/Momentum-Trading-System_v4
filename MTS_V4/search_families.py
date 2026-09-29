from __future__ import annotations

from typing import Callable

from .computational_search import Gene, SearchSpace
from .derived_feature_factory import standard_predictor_feature_set
from .earnings_event_features import earnings_event_feature_set


def _space(family_id: str, genes: tuple[Gene, ...], *, gaps: tuple[str, ...] = (), max_predicates: int = 4) -> SearchSpace:
    return SearchSpace(
        search_space_id=f"{family_id.lower().replace('_', '-')}-core",
        version="v1",
        family_id=family_id,
        genes=genes,
        maximum_active_predicates=max_predicates,
        attributes={
            "implemented_features_only": True,
            "known_feature_gaps": gaps,
            "scientific_status": "SEARCH_GRAMMAR_NOT_HYPOTHESIS",
        },
    )


def momentum_search_space_v1() -> SearchSpace:
    return _space("MOMENTUM", (
        Gene("momentum_feature", ("return_20__v1","return_63__v1","return_126__v1","return_252__v1","return_252_skip_20__v1","return_126_percentile__v1","return_252_percentile__v1","return_252_skip_20_percentile__v1")),
        Gene("direction", ("ABOVE","BELOW")),
        Gene("threshold_quantile", (0.50,0.60,0.70,0.80,0.90)),
        Gene("context_feature", ("NONE","breadth_above_sma_200__v1","breadth_positive_20__v1","sector_return_252_percentile__v1","natr_20_percentile__v1")),
        Gene("context_threshold", (0.40,0.50,0.60,0.70)),
        Gene("forward_horizon", (5,10,20,63)),
    ), gaps=("multi_horizon_momentum_agreement",), max_predicates=2)


def breakout_search_space_v1() -> SearchSpace:
    return _space("BREAKOUT", (
        Gene("range_feature", ("range_position_20__v1","range_position_50__v1","range_position_252__v1","prior_high_break_distance_20__v1","prior_high_break_distance_50__v1","range_width_ratio_20_63__v1","compression_duration__v1","failed_breakout_20__v1","breakout_reentry_20__v1")),
        Gene("range_threshold", (0.80,0.90,0.95,0.98)),
        Gene("participation_feature", ("NONE","relative_volume_20__v1","relative_volume_20_percentile__v1")),
        Gene("participation_threshold", (1.0,1.25,1.5,2.0)),
        Gene("volatility_feature", ("NONE","natr_20__v1","natr_20_percentile__v1","realized_vol_20__v1")),
        Gene("forward_horizon", (5,10,20,63)),
    ), gaps=(), max_predicates=3)


def trend_search_space_v1() -> SearchSpace:
    return _space("TREND", (
        Gene("trend_feature", ("close_to_sma_20__v1","close_to_sma_50__v1","close_to_sma_200__v1","sma20_slope_5__v1","sma50_slope_10__v1","sma200_slope_20__v1","trend_above_sma200_duration__v1","pullback_from_high_20__v1","adx_14__v1")),
        Gene("direction", ("ABOVE","BELOW")),
        Gene("threshold", (-0.10,-0.05,0.0,0.05,0.10)),
        Gene("confirmation_feature", ("NONE","return_63__v1","return_126__v1","range_position_50__v1")),
        Gene("forward_horizon", (5,10,20,63)),
    ), gaps=(), max_predicates=3)


def mean_reversion_search_space_v1() -> SearchSpace:
    return _space("MEAN_REVERSION", (
        Gene("displacement_feature", ("rsi_14__v1","close_to_sma_20__v1","close_to_sma_50__v1","return_5__v1","return_10__v1","return_20__v1","drawdown_252__v1","range_position_20__v1","price_zscore_20__v1","signed_return_streak__v1","exhaustion_score__v1")),
        Gene("tail", ("LOW","HIGH")),
        Gene("severity", (0.05,0.10,0.20,0.30)),
        Gene("context_feature", ("NONE","realized_vol_20__v1","natr_20_percentile__v1","breadth_positive_20__v1")),
        Gene("forward_horizon", (1,3,5,10,20)),
    ), gaps=("distance_from_vwap_requires_intraday_or_vwap_source",), max_predicates=3)


def volatility_search_space_v1() -> SearchSpace:
    return _space("VOLATILITY", (
        Gene("volatility_feature", ("natr_14__v1","natr_20__v1","natr_20_percentile__v1","realized_vol_20__v1","realized_vol_63__v1","candle_range_fraction__v1","volatility_ratio_20_63__v1","range_width_ratio_20_63__v1","volatility_contraction_duration__v1","volatility_expansion_transition__v1","realized_vol_20_percentile__v1")),
        Gene("state", ("LOW","HIGH")),
        Gene("threshold_quantile", (0.10,0.20,0.30,0.70,0.80,0.90)),
        Gene("price_context", ("NONE","return_20__v1","range_position_20__v1","close_to_sma_50__v1")),
        Gene("forward_horizon", (3,5,10,20,63)),
    ), gaps=(), max_predicates=3)


def volume_liquidity_search_space_v1() -> SearchSpace:
    return _space("VOLUME_LIQUIDITY", (
        Gene("participation_feature", ("relative_volume_20__v1","relative_volume_20_percentile__v1","turnover__v1","turnover_relative_20__v1","dollar_volume__v1","dollar_volume_relative_20__v1","amihud_illiquidity_20__v1","high_low_spread_proxy__v1","volume_slope_20__v1","up_down_volume_balance_20__v1")),
        Gene("state", ("LOW","HIGH")),
        Gene("threshold", (0.5,0.75,1.0,1.25,1.5,2.0)),
        Gene("price_feature", ("NONE","return_5__v1","return_20__v1","intraday_return__v1","close_location__v1")),
        Gene("forward_horizon", (1,3,5,10,20)),
    ), gaps=(), max_predicates=3)


def relative_strength_search_space_v1() -> SearchSpace:
    return _space("RELATIVE_CROSS_SECTIONAL", (
        Gene("relative_feature", ("return_126_percentile__v1","return_252_percentile__v1","return_252_skip_20_percentile__v1","sector_return_252_percentile__v1","relative_strength_change_20__v1","sector_vs_universe_return_63__v1")),
        Gene("tail", ("LEADER","LAGGARD")),
        Gene("threshold", (0.10,0.20,0.30,0.70,0.80,0.90)),
        Gene("market_context", ("NONE","breadth_above_sma_200__v1","breadth_positive_20__v1")),
        Gene("forward_horizon", (5,10,20,63)),
    ), gaps=("leadership_rotation_rate_available_in_analysis_rank_persistence_not_row_feature",), max_predicates=3)


def event_earnings_search_space_v1() -> SearchSpace:
    # Earnings-event rows exist elsewhere in MTS; this grammar uses only price
    # reactions currently available in the standard predictor panel until the
    # event evidence is joined through a governed Analysis contract.
    return _space("EVENT_EARNINGS", (
        Gene("reaction_feature", ("gap_return__v1","intraday_return__v1","relative_volume_20__v1","close_location__v1","earnings_surprise_pct__v1","days_since_earnings__v1","earnings_event_session__v1")),
        Gene("reaction_direction", ("POSITIVE","NEGATIVE")),
        Gene("reaction_threshold", (0.01,0.02,0.03,0.05,0.10)),
        Gene("momentum_context", ("NONE","return_63__v1","return_126_percentile__v1","return_252_skip_20_percentile__v1")),
        Gene("forward_horizon", (1,3,5,10,20,63)),
    ), gaps=(), max_predicates=3)


def market_regime_search_space_v1() -> SearchSpace:
    return _space("MARKET_REGIME_STRUCTURE", (
        Gene("breadth_feature", ("breadth_above_sma_200__v1","breadth_positive_20__v1","advance_decline_breadth__v1","new_high_low_breadth_252__v1","realized_vol_20_percentile__v1")),
        Gene("breadth_state", ("LOW","MID","HIGH")),
        Gene("breadth_threshold", (0.20,0.30,0.40,0.50,0.60,0.70,0.80)),
        Gene("security_context", ("NONE","return_20__v1","close_to_sma_200__v1","natr_20_percentile__v1")),
        Gene("forward_horizon", (5,10,20,63)),
    ), gaps=("correlation_regime_available_in_analysis_not_row_feature",), max_predicates=3)


def cross_family_search_space_v1() -> SearchSpace:
    return _space("CROSS_FAMILY_COMPOSITE", (
        Gene("family_a", ("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","EVENT_EARNINGS","MARKET_REGIME_STRUCTURE")),
        Gene("family_b", ("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","EVENT_EARNINGS","MARKET_REGIME_STRUCTURE")),
        Gene("composition", ("AND","CONTEXT_FILTER","CONFIRMATION")),
        Gene("forward_horizon", (5,10,20,63)),
    ), gaps=("candidate_reference_resolution_required",), max_predicates=2)


def experimental_search_space_v1() -> SearchSpace:
    """Placeholder grammar for RD/human-authored experiments.

    It intentionally contains no arbitrary market features. The RD must create a
    versioned experiment-specific SearchSpace rather than receiving unrestricted
    access to future outcomes or an unversioned feature soup.
    """
    return _space("EXPERIMENTAL", (
        Gene("experiment_slot", ("RD_DEFINED_SEARCH_SPACE_REQUIRED",)),
    ), gaps=("rd_defined_versioned_genes_required",), max_predicates=1)


FAMILY_FACTORIES: dict[str, Callable[[], SearchSpace]] = {
    "MOMENTUM": momentum_search_space_v1,
    "BREAKOUT": breakout_search_space_v1,
    "TREND": trend_search_space_v1,
    "MEAN_REVERSION": mean_reversion_search_space_v1,
    "VOLATILITY": volatility_search_space_v1,
    "VOLUME_LIQUIDITY": volume_liquidity_search_space_v1,
    "RELATIVE_CROSS_SECTIONAL": relative_strength_search_space_v1,
    "EVENT_EARNINGS": event_earnings_search_space_v1,
    "MARKET_REGIME_STRUCTURE": market_regime_search_space_v1,
    "CROSS_FAMILY_COMPOSITE": cross_family_search_space_v1,
    "EXPERIMENTAL": experimental_search_space_v1,
}


def all_search_spaces_v1() -> tuple[SearchSpace, ...]:
    return tuple(factory() for factory in FAMILY_FACTORIES.values())


def implemented_predictor_columns() -> frozenset[str]:
    return frozenset((*standard_predictor_feature_set().feature_columns, *earnings_event_feature_set().feature_columns))


def referenced_predictor_columns(space: SearchSpace) -> frozenset[str]:
    implemented = implemented_predictor_columns()
    refs: set[str] = set()
    for gene in space.genes:
        for value in gene.values:
            if isinstance(value, str) and value in implemented:
                refs.add(value)
    return frozenset(refs)
