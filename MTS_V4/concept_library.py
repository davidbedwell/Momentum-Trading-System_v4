from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping


@dataclass(frozen=True, slots=True)
class ResearchConcept:
    """A non-authoritative description that may stimulate scientific inquiry.

    Concepts are not findings, definitions, rules, or accepted market truths.
    They are candidate human/AI descriptions whose empirical content, scope,
    interactions, failure modes, and usefulness remain open to RD investigation.
    """

    concept_id: str
    name: str
    description: str
    source_class: str
    questions: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def payload(self) -> dict[str, Any]:
        return asdict(self)


class ResearchConceptLibrary:
    """Open vocabulary of scientific idea seeds supplied to the AI RD.

    Deterministic code stores and transports descriptions only. It does not
    rank concepts, select which RD should investigate, convert them into
    hypotheses automatically, or treat their presence as evidence.
    """

    def __init__(self, concepts: Iterable[ResearchConcept] = ()) -> None:
        self._concepts: dict[str, ResearchConcept] = {}
        for concept in concepts:
            self.add(concept)

    def add(self, concept: ResearchConcept) -> None:
        if not concept.concept_id.strip():
            raise ValueError("concept_id cannot be blank")
        if concept.concept_id in self._concepts:
            raise ValueError(f"duplicate concept_id: {concept.concept_id}")
        self._concepts[concept.concept_id] = concept

    def all(self) -> tuple[ResearchConcept, ...]:
        return tuple(self._concepts[key] for key in sorted(self._concepts))

    def payloads(self) -> tuple[dict[str, Any], ...]:
        return tuple(item.payload() for item in self.all())


def seed_market_concepts() -> ResearchConceptLibrary:
    """Human idea seeds, deliberately broad and explicitly non-authoritative."""
    seed = "HUMAN_DESCRIPTION_NOT_ESTABLISHED_FACT"
    concepts = (
        ResearchConcept(
            "human.risk_reward_path_time",
            "Risk, reward, path, and time",
            "RP-0001 expressed one useful human model: a movement's practical value may depend on potential reward in relation to adverse movement, the path taken, and the time required. Its historical thresholds and formulations are examples rather than scientific boundaries.",
            seed,
            (
                "What measurable relationships among reward, adverse excursion, path, and time actually exist?",
                "Which representations generalize, and where do they fail?",
            ),
        ),
        ResearchConcept(
            "human.support_resistance",
            "Support and resistance",
            "Traders often describe price regions as support or resistance when prior trading behavior appears to impede movement, attract reactions, or concentrate decisions. Breakthroughs are sometimes described as producing continuation, rejection, retest, or role reversal. None of those behaviors is presumed.",
            seed,
            (
                "Can such regions be defined from observable data without circularity?",
                "Do interactions with them alter subsequent movement distributions?",
                "Are breakthrough, rejection, retest, or role-reversal descriptions reproducible?",
            ),
        ),
        ResearchConcept(
            "human.trend",
            "Trend",
            "Market participants often describe sustained directional structure as trend, using ideas such as higher highs and lows, lower highs and lows, slope, persistence, or directional return. These are competing descriptions rather than a fixed definition.",
            seed,
            (
                "Which representations of directional persistence contain predictive information?",
                "How does any observed persistence vary with horizon, volatility, volume, or regime?",
            ),
        ),
        ResearchConcept(
            "human.momentum",
            "Momentum",
            "Momentum is commonly used to describe persistence, acceleration, or strength of price movement, sometimes relative to recent history. The term has multiple human meanings and no one formulation is privileged here.",
            seed,
            (
                "Which measurable forms of persistence, acceleration, or relative strength are distinct?",
                "When, if ever, do they predict continuation or reversal?",
            ),
        ),
        ResearchConcept(
            "human.mean_reversion",
            "Mean reversion",
            "A common market theory proposes that some departures from a reference level or recent distribution tend to be followed by movement back toward it. The relevant reference, scale, horizon, and conditions are unresolved scientific questions.",
            seed,
            (
                "Under what conditions do departures tend to persist versus revert?",
                "What candidate reference levels, if any, are empirically useful?",
            ),
        ),
        ResearchConcept(
            "human.volatility_regime",
            "Volatility and volatility regimes",
            "Traders describe markets as alternating among lower- and higher-volatility conditions and sometimes expect volatility to cluster, compress, or expand. These descriptions may concern magnitude rather than direction.",
            seed,
            (
                "Does volatility exhibit persistent or transitional structure useful to forecasting movement magnitude or path?",
                "Do compression and expansion concepts survive alternative measurements and horizons?",
            ),
        ),
        ResearchConcept(
            "human.volume_participation",
            "Volume and participation",
            "Trading volume is often treated as a proxy for market participation or activity and is frequently interpreted jointly with price movement. Aggregate volume alone does not establish participant identity, intent, accumulation, or distribution.",
            seed,
            (
                "What relationships exist between unusual volume, price displacement, volatility, and subsequent movement?",
                "Does high activity with limited price movement identify conditions different from high activity with large displacement?",
            ),
        ),
        ResearchConcept(
            "human.liquidity_imbalance",
            "Liquidity, imbalance, and price impact",
            "Market theories often connect available liquidity, order-flow imbalance, transaction size, and price impact. Observable proxies may be incomplete and should not be treated as direct measures of hidden intent.",
            seed,
            (
                "Which observable liquidity or imbalance measures precede changes in movement magnitude, direction, or path?",
                "How stable are those relationships across instruments and regimes?",
            ),
        ),
        ResearchConcept(
            "human.breakout_consolidation",
            "Consolidation and breakout",
            "Traders often describe bounded or compressed price behavior as consolidation and movement beyond that region as breakout. Human theory variously predicts continuation, failure, retest, or no special consequence.",
            seed,
            (
                "Can consolidation be represented without embedding the desired outcome?",
                "How do post-boundary movement distributions compare with appropriate controls?",
            ),
        ),
        ResearchConcept(
            "human.gaps_discontinuities",
            "Gaps and discontinuities",
            "Price discontinuities between trading periods are often described as information shocks, imbalance, or areas that may later be revisited. Those narratives are hypotheses rather than established causes.",
            seed,
            (
                "Do discontinuities contain information about subsequent direction, magnitude, path, or volatility?",
                "What contextual variables alter any relationship?",
            ),
        ),
        ResearchConcept(
            "human.relative_strength",
            "Relative strength and leadership",
            "Market participants compare an instrument's behavior with a benchmark, sector, peer group, or market and sometimes interpret persistent outperformance or underperformance as leadership or weakness.",
            seed,
            (
                "Does relative performance add predictive information beyond the instrument's own history?",
                "Which comparison sets and horizons, if any, generalize?",
            ),
        ),
        ResearchConcept(
            "human.market_regime",
            "Market regime and context dependence",
            "Many trading theories propose that relationships change with broader market conditions rather than remaining stationary. Candidate regimes may involve direction, volatility, liquidity, correlation, macro conditions, or combinations not yet anticipated.",
            seed,
            (
                "Which relationships are stable and which are conditional?",
                "Can useful contextual states be discovered without forcing a predetermined regime taxonomy?",
            ),
        ),
        ResearchConcept(
            "human.cross_asset_sector_context",
            "Cross-asset, sector, and market context",
            "An instrument's movement may be related to contemporaneous or preceding behavior in its sector, index, related assets, rates, volatility measures, or other external context. Human narratives about those links are not assumed causal.",
            seed,
            (
                "Which external relationships add information beyond ticker-local evidence?",
                "Are observed relationships contemporaneous, leading, lagging, conditional, or unstable?",
            ),
        ),
        ResearchConcept(
            "human.off_exchange_block_options",
            "Off-exchange, block, and options activity",
            "Large, off-exchange, block, or options activity is sometimes interpreted as informed or institutional positioning. Transaction class or size alone does not establish participant identity, intent, direction, hedging purpose, or causation.",
            seed,
            (
                "Does elevated activity coincide with otherwise unusual price/volume states?",
                "Does it predict subsequent expansion, direction, continuation, or reversal after controlling for observable context?",
            ),
        ),
        ResearchConcept(
            "human.seasonality_calendar",
            "Seasonality and calendar effects",
            "Human market literature describes recurring behavior associated with time of day, day of week, month, earnings cycles, expirations, and other calendar structures. Apparent recurrence may be unstable, conditional, or spurious.",
            seed,
            (
                "Which temporal patterns survive out-of-sample testing and multiple comparisons?",
                "Do calendar effects interact with other observable market states?",
            ),
        ),
        ResearchConcept(
            "human.interaction_non_linearity",
            "Interactions and nonlinear conditions",
            "Trading ideas are frequently stated as combinations: a variable may matter only when another variable is elevated, suppressed, aligned, or changing. A weak marginal relationship does not rule out conditional structure, but combinations also create overfitting risk.",
            seed,
            (
                "Which interactions are reproducible rather than artifacts of search?",
                "Can discovered combinations generalize across time or subjects?",
            ),
        ),
    )
    return ResearchConceptLibrary(concepts)
