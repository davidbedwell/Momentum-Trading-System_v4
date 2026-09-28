from __future__ import annotations

from .computational_search import Gene, SearchSpace


def momentum_search_space_v1() -> SearchSpace:
    """Initial search grammar using predictor columns already present in the v1 derived feature factory.

    Threshold grids are intentionally coarse in the baseline. Fine precision
    should be earned by later neighborhood search, not granted to the first pass.
    """
    return SearchSpace(
        search_space_id="momentum-core",
        version="v1",
        family_id="MOMENTUM",
        genes=(
            Gene("momentum_feature", (
                "return_20__v1", "return_63__v1", "return_126__v1",
                "return_252__v1", "return_252_skip_20__v1",
                "return_126_percentile__v1", "return_252_percentile__v1",
                "return_252_skip_20_percentile__v1",
            ), meaning="Implemented absolute or cross-sectional momentum measurement"),
            Gene("direction", ("ABOVE", "BELOW")),
            Gene("threshold_quantile", (0.50, 0.60, 0.70, 0.80, 0.90)),
            Gene("context_feature", (
                "NONE", "breadth_above_sma_200__v1", "breadth_positive_20__v1",
                "sector_return_252_percentile__v1", "natr_20_percentile__v1",
            )),
            Gene("context_threshold", (0.40, 0.50, 0.60, 0.70)),
            Gene("forward_horizon", (5, 10, 20, 63)),
        ),
        maximum_active_predicates=2,
        attributes={
            "implemented_features_only": True,
            "scientific_status": "SEARCH_GRAMMAR_NOT_HYPOTHESIS",
        },
    )


def breakout_search_space_v1() -> SearchSpace:
    """Baseline breakout grammar limited to features already implemented.

    This intentionally exposes that richer breakout concepts (true prior-high
    breakout distance, compression duration, failed-breakout state) require new
    deterministic features rather than silently pretending current genes cover them.
    """
    return SearchSpace(
        search_space_id="breakout-core",
        version="v1",
        family_id="BREAKOUT",
        genes=(
            Gene("range_feature", ("range_position_20__v1", "range_position_50__v1", "range_position_252__v1")),
            Gene("range_threshold", (0.80, 0.90, 0.95, 0.98)),
            Gene("participation_feature", ("NONE", "relative_volume_20__v1", "relative_volume_20_percentile__v1")),
            Gene("participation_threshold", (1.0, 1.25, 1.5, 2.0)),
            Gene("volatility_feature", ("NONE", "natr_20__v1", "natr_20_percentile__v1", "realized_vol_20__v1")),
            Gene("forward_horizon", (5, 10, 20, 63)),
        ),
        maximum_active_predicates=3,
        attributes={
            "implemented_features_only": True,
            "known_feature_gaps": (
                "prior_high_break_distance", "compression_duration",
                "failed_breakout_state", "breakout_reentry_state",
            ),
            "scientific_status": "SEARCH_GRAMMAR_NOT_HYPOTHESIS",
        },
    )
