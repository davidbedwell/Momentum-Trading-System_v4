from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


UNVERIFIED_EXTERNAL_RESEARCH_LEAD = "UNVERIFIED_EXTERNAL_RESEARCH_LEAD"
HUMAN_ORIGIN_RESEARCH_LEAD = "HUMAN_ORIGIN_RESEARCH_LEAD"


@dataclass(frozen=True, slots=True)
class ResearchLead:
    """Non-authoritative external or human trading theory supplied to the AI RD.

    A ResearchLead is not a finding, rule, signal, preferred threshold, or accepted
    relationship. It exists only to make a falsifiable idea available for autonomous
    scientific investigation. The RD may test, modify, combine, defer, reject, or
    replace any lead.
    """

    lead_id: str
    name: str
    claimed_relationship: str
    questions: tuple[str, ...]
    source_class: str = UNVERIFIED_EXTERNAL_RESEARCH_LEAD
    source_urls: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def concept_metadata(self) -> dict[str, Any]:
        return {
            "research_lead": True,
            "status": self.source_class,
            "claimed_relationship": self.claimed_relationship,
            "source_urls": list(self.source_urls),
            "scientific_authority": "AI_RESEARCH_DIRECTOR_ONLY",
            "rd_may_test_modify_combine_defer_reject_or_replace": True,
            "deterministic_thresholds": False,
            "deterministic_signal": False,
            **dict(self.metadata),
        }


def seed_external_research_leads() -> tuple[ResearchLead, ...]:
    """Internet/human trading folklore converted into falsifiable idea seeds.

    Sources document that traders advocate or discuss the theory. Source presence
    is not evidence that the relationship is true or profitable.
    """
    return (
        ResearchLead(
            "lead.low_float_rvol_catalyst",
            "Low float, exceptional participation, and catalyst",
            "Some momentum traders claim that relatively small public float, unusually high relative volume or float turnover, and a fresh material event can interact to produce unusually large subsequent moves.",
            (
                "Do float, relative volume, float turnover, and event context interact predictively?",
                "Are any apparent thresholds real, continuous, nonlinear, regime-dependent, or unstable?",
                "Which event classes, if any, materially change the relationship?",
            ),
            source_class=HUMAN_ORIGIN_RESEARCH_LEAD,
            source_urls=(
                "https://www.warriortrading.com/gap-go/",
                "https://lightspeed.com/active-trading-blog/what-is-float-rotation-in-stock-trading",
            ),
            metadata={"human_seed_examples_only": {"float_shares": 10_000_000, "relative_volume": 5.0}},
        ),
        ResearchLead(
            "lead.gap_and_go",
            "Gap-and-go continuation",
            "A common day-trading theory proposes that a meaningful premarket gap accompanied by fresh news, strong participation, and a break of premarket or opening-range highs may continue in the gap direction.",
            (
                "Which combinations of gap size, participation, event context, and opening behavior predict continuation rather than reversal?",
                "Does premarket-high or opening-range structure add information beyond gap and volume alone?",
            ),
            source_urls=("https://www.warriortrading.com/gap-go/",),
        ),
        ResearchLead(
            "lead.gap_fade_vs_continuation",
            "Gap fade versus continuation",
            "Trader literature contains competing gap theories: some gaps continue while others reverse toward the prior close. The discriminating conditions are unresolved.",
            (
                "What observable-at-T variables discriminate continuation from gap fill or reversal?",
                "Do catalyst class, gap magnitude, premarket path, volume trajectory, or broader regime change the odds?",
            ),
            source_urls=(
                "https://www.tradingsim.com/blog/morning-reversal-gap-fill",
                "https://www.tradingsim.com/blog/day-trading-earnings-gaps",
            ),
        ),
        ResearchLead(
            "lead.opening_range_breakout",
            "Opening-range breakout",
            "A widely discussed setup claims that a break of an early-session range can precede directional continuation, particularly when accompanied by a gap, strong participation, or trend context.",
            (
                "Does opening-range breakout have predictive value after controlling for gap, volatility, and participation?",
                "Which range definitions, if any, generalize without privileging a fixed 1-, 5-, 15-, or 30-minute window?",
            ),
            source_urls=(
                "https://www.tradingsim.com/blog/1-minute-orb",
                "https://www.tradingsim.com/blog/opening-range",
            ),
        ),
        ResearchLead(
            "lead.premarket_high_break",
            "Premarket-high breakout",
            "Momentum traders commonly treat a break of the premarket high on expanding participation as a possible continuation event.",
            (
                "Does a premarket-high break change subsequent return or path distributions?",
                "Is any effect conditional on gap size, catalyst, float, volatility, opening range, or market regime?",
            ),
            source_urls=(
                "https://www.warriortrading.com/gap-go/",
                "https://www.tradingsim.com/blog/day-trading-breakouts",
            ),
        ),
        ResearchLead(
            "lead.vwap_reclaim_hold",
            "VWAP reclaim, hold, and rejection",
            "Intraday trading literature often treats reclaiming, holding, or rejecting VWAP as evidence of changing directional pressure or trend quality.",
            (
                "Do VWAP reclaim, hold, rejection, or distance states contain incremental predictive information?",
                "Are they merely contemporaneous descriptions, or do they discriminate later continuation and reversal after controls?",
            ),
            source_urls=("https://www.tradingsim.com/blog/vwap-indicator-guide",),
        ),
        ResearchLead(
            "lead.float_rotation",
            "Float rotation",
            "Small-cap momentum traders track cumulative volume divided by public float and claim that the number and timing of float rotations may identify unusually intense participation, continuation, crowding, exhaustion, or reversal.",
            (
                "Does continuous float turnover predict subsequent magnitude, direction, continuation, reversal, or path quality?",
                "Are rotation milestones meaningful or artifacts of arbitrary thresholds?",
                "Does rotation timing matter more than end-of-day rotation count?",
            ),
            source_urls=(
                "https://lightspeed.com/active-trading-blog/what-is-float-rotation-in-stock-trading",
                "https://scanrover.com/blog/what-is-float-rotation",
            ),
        ),
        ResearchLead(
            "lead.volume_price_absorption",
            "High volume with limited price displacement",
            "Trader theories often interpret unusually high activity with muted price movement as possible absorption, accumulation, distribution, or hidden liquidity. Those causal labels are unverified.",
            (
                "Does abnormal volume combined with suppressed price displacement precede expansion more often than matched controls?",
                "Can off-exchange, options, or other evidence distinguish later direction, continuation, or reversal without inferring hidden intent?",
            ),
            metadata={"related_existing_concept": "human.off_exchange_block_options"},
        ),
        ResearchLead(
            "lead.catalyst_class_effects",
            "Catalyst-class differentiation",
            "Market reactions may differ across earnings, guidance, regulatory, clinical, M&A, contract, financing, analyst, legal, management, product, and other event classes rather than behaving as a single generic news variable.",
            (
                "Which event classes, if any, alter subsequent movement distributions after conditioning on price and participation state?",
                "Does event novelty, timing, direction, or magnitude interact with float, gap, volatility, or prior trend?",
            ),
        ),
        ResearchLead(
            "lead.gap_magnitude_nonlinearity",
            "Gap-magnitude nonlinearity",
            "Trader playbooks frequently use minimum gap thresholds, while competing theories suggest very large gaps may become exhaustion or reversal candidates. The relationship need not be monotonic.",
            (
                "Is gap magnitude related continuously or nonlinearly to continuation, reversal, magnitude, or path?",
                "Do any apparent breakpoints survive alternative samples, subjects, and regimes?",
            ),
            source_urls=("https://www.tradingsim.com/blog/day-trading-earnings-gaps",),
        ),
        ResearchLead(
            "lead.setup_regime_dependence",
            "Setup dependence on market regime",
            "Many trader setups are claimed to work differently depending on broader market direction, volatility, liquidity, sector behavior, or risk appetite.",
            (
                "Are candidate setup relationships stable or conditional on independently observable market context?",
                "Can regime conditioning improve generalization without post-hoc overfitting?",
            ),
            metadata={"related_existing_concept": "human.market_regime"},
        ),
    )
