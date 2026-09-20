from __future__ import annotations

from typing import Mapping

KNOWN_PREDICTIVE_THEORY_CONTEXT_VERSION = "2026-09-20-v1"

KNOWN_PREDICTIVE_THEORIES: tuple[Mapping[str, object], ...] = (
    {
        "theory_id": "CROSS_SECTIONAL_MOMENTUM",
        "name": "Cross-sectional momentum",
        "canonical_claim": "Stronger intermediate-horizon prior performers may continue to outperform weaker peers over subsequent horizons.",
        "factor_families": ("past_return", "relative_strength", "cross_sectional_rank"),
        "canonical_direction": "continuation",
        "references": ("Jegadeesh & Titman (1993)",),
        "caveats": ("crash/reversal regimes", "costs", "formation/holding-horizon dependence"),
    },
    {
        "theory_id": "TIME_SERIES_MOMENTUM",
        "name": "Time-series momentum / trend persistence",
        "canonical_claim": "An asset's own prior directional trend may contain information about subsequent directional continuation.",
        "factor_families": ("trend_slope", "moving_average_position", "past_return"),
        "canonical_direction": "continuation",
        "references": ("Moskowitz, Ooi & Pedersen (2012)",),
        "caveats": ("whipsaw", "regime dependence", "parameter sensitivity"),
    },
    {
        "theory_id": "SHORT_HORIZON_REVERSAL",
        "name": "Short-horizon reversal",
        "canonical_claim": "Extreme very-short-horizon price moves may be followed by partial reversal.",
        "factor_families": ("short_return", "gap", "extreme_move", "liquidity_shock"),
        "canonical_direction": "reversal",
        "references": ("Lehmann (1990)",),
        "caveats": ("microstructure artifacts", "event-driven continuation", "cost sensitivity"),
    },
    {
        "theory_id": "LONG_HORIZON_REVERSAL",
        "name": "Long-horizon reversal",
        "canonical_claim": "Extreme long-horizon prior winners and losers may subsequently reverse.",
        "factor_families": ("long_horizon_return", "drawdown", "valuation_context"),
        "canonical_direction": "reversal",
        "references": ("De Bondt & Thaler (1985)",),
        "caveats": ("distress exposure", "sample dependence", "long holding period"),
    },
    {
        "theory_id": "POST_EARNINGS_ANNOUNCEMENT_DRIFT",
        "name": "Post-earnings-announcement drift",
        "canonical_claim": "Prices may continue in the direction of earnings surprise after the announcement.",
        "factor_families": ("earnings_surprise", "earnings_timing", "post_event_return", "volume_response"),
        "canonical_direction": "surprise-direction continuation",
        "references": ("Bernard & Thomas (1989)",),
        "caveats": ("estimate-vintage quality", "release-time alignment", "decay through time"),
    },
    {
        "theory_id": "PRICE_VOLUME_PARTICIPATION",
        "name": "Price-volume / participation confirmation",
        "canonical_claim": "Price moves accompanied by unusual participation may have different continuation or exhaustion behavior than similar moves on weak participation.",
        "factor_families": ("relative_volume", "turnover", "volume_shock", "price_change"),
        "canonical_direction": "conditional continuation or exhaustion",
        "references": ("market-microstructure and technical-analysis literature",),
        "caveats": ("no universal bullish/bearish direction", "event confounding", "share-count changes"),
    },
    {
        "theory_id": "VOLATILITY_CONTRACTION_EXPANSION",
        "name": "Volatility contraction / expansion",
        "canonical_claim": "Unusually compressed realized range or volatility may precede larger subsequent absolute moves.",
        "factor_families": ("realized_volatility", "range_width", "bollinger_width", "atr"),
        "canonical_direction": "absolute-move expansion; not directional by itself",
        "references": ("volatility and breakout literature",),
        "caveats": ("direction requires separate evidence", "threshold/horizon sensitivity"),
    },
    {
        "theory_id": "VOLATILITY_CLUSTERING",
        "name": "Volatility clustering",
        "canonical_claim": "High-volatility states tend to be followed by relatively high volatility and low-volatility states by relatively low volatility.",
        "factor_families": ("realized_volatility", "range", "atr", "squared_return"),
        "canonical_direction": "variance persistence",
        "references": ("Engle (1982)", "Bollerslev (1986)"),
        "caveats": ("not inherently directional", "regime transitions"),
    },
    {
        "theory_id": "BREAKOUT_PRIOR_EXTREMES",
        "name": "Breakout / prior-extreme continuation",
        "canonical_claim": "Movement through prior price extremes or trading ranges may predict continuation when persistent information or order-flow imbalance is present.",
        "factor_families": ("prior_high_low", "range_break", "52_week_high_proximity", "volume_confirmation"),
        "canonical_direction": "conditional continuation",
        "references": ("George & Hwang (2004)",),
        "caveats": ("false breakouts", "parameter dependence", "gap/event confounding"),
    },
    {
        "theory_id": "GAP_CONTINUATION_REVERSAL",
        "name": "Gap continuation versus fill",
        "canonical_claim": "Overnight gaps may continue or fill depending on catalyst, gap size, participation, liquidity, and market regime.",
        "factor_families": ("overnight_gap", "premarket_volume", "opening_range", "catalyst", "relative_volume"),
        "canonical_direction": "conditional continuation or reversal",
        "references": ("market-microstructure and event-study literature",),
        "caveats": ("event information and opening liquidity are material conditioners",),
    },
    {
        "theory_id": "LIQUIDITY_ILLIQUIDITY",
        "name": "Liquidity / illiquidity effects",
        "canonical_claim": "Liquidity state and shocks may contain information about subsequent expected return and path/adverse movement.",
        "factor_families": ("amihud_illiquidity", "turnover", "spread_proxy", "dollar_volume"),
        "canonical_direction": "conditional return/path effect",
        "references": ("Amihud (2002)",),
        "caveats": ("implementation costs", "size confounding"),
    },
    {
        "theory_id": "MARKET_SECTOR_RELATIVE_STRENGTH",
        "name": "Market/sector-relative strength",
        "canonical_claim": "A security's trend and return relative to its market or sector may contain information distinct from absolute movement.",
        "factor_families": ("market_relative_return", "sector_relative_return", "cross_sectional_rank", "breadth"),
        "canonical_direction": "conditional relative continuation",
        "references": ("relative-strength and momentum literature",),
        "caveats": ("benchmark choice", "sector regime changes", "factor crowding"),
    },
    {
        "theory_id": "MARKET_BREADTH_CONDITIONING",
        "name": "Market breadth / participation conditioning",
        "canonical_claim": "Breadth and participation of the surrounding market may condition the durability or reversal risk of a single-name move.",
        "factor_families": ("advance_decline_breadth", "percent_above_trend", "cross_sectional_dispersion", "sector_breadth"),
        "canonical_direction": "conditioning variable, not universal direction",
        "references": ("cross-sectional market-state literature",),
        "caveats": ("universe-composition sensitivity", "not a stand-alone directional rule"),
    },
    {
        "theory_id": "OFF_EXCHANGE_PARTICIPATION",
        "name": "Off-exchange / alternative-venue participation",
        "canonical_claim": "Unusual off-exchange participation may contain information about liquidity or demand/supply, subject to strict publication-time treatment.",
        "factor_families": ("finra_off_exchange_volume", "off_exchange_share", "turnover", "relative_volume"),
        "canonical_direction": "unknown; empirical determination required",
        "references": ("market-microstructure literature",),
        "caveats": ("publication timing", "venue composition", "not inherently bullish/bearish"),
    },
)

KNOWN_PREDICTIVE_THEORY_IDS = tuple(str(item["theory_id"]) for item in KNOWN_PREDICTIVE_THEORIES)

def known_predictive_theory_context() -> Mapping[str, object]:
    return {
        "version": KNOWN_PREDICTIVE_THEORY_CONTEXT_VERSION,
        "human_required_coverage": True,
        "authority": (
            "Human-required scientific coverage, but zero privileged evidentiary weight. Each theory family must be "
            "scientifically tested on the active ticker when available evidence can represent it, or explicitly marked "
            "OBJECTIVELY_NOT_TESTABLE when the required evidence is unavailable. Appearance in this catalog is not "
            "evidence that the theory is true or applies to this ticker."
        ),
        "anti_bias_rules": (
            "Do not assign scientific weight merely because a theory appears in this catalog.",
            "Do not treat catalog omission as evidence against pursuing another idea.",
            "Do not inherit canonical direction, threshold, horizon, representation, or method without active-subject scientific judgment.",
            "Required coverage does not limit novel discovery and does not require promotion of any finding or trading candidate.",
        ),
        "theories": [dict(item) for item in KNOWN_PREDICTIVE_THEORIES],
    }

def compact_known_predictive_theory_index() -> Mapping[str, object]:
    return {
        "version": KNOWN_PREDICTIVE_THEORY_CONTEXT_VERSION,
        "human_required_coverage": True,
        "theories": [
            {
                "theory_id": item["theory_id"],
                "name": item["name"],
                "factor_families": list(item["factor_families"]),
            }
            for item in KNOWN_PREDICTIVE_THEORIES
        ],
    }
