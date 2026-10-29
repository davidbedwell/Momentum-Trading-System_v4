# MTS v4 — Cross-Sectional Evolutionary Portfolio Architecture Protocol — 2026-10-02

## Status
FROZEN DESIGN / PRE-LAUNCH. The prior controller incremental-cost study is closed. Complete the launch gate below before the first GA fitness evaluation.

## Central hypothesis
The next major MTS improvement may come less from discovering another isolated single-stock entry rule and more from evolving how already-qualified opportunities compete for scarce portfolio capital.

Central question:
**Given many valid MTS opportunities, which deserve capital now, which incumbents deserve to remain, how much evidence should a challenger need to displace one, and when should capital remain in the safe asset instead?**

This is independent MTS research. Public/observable third-party portfolio concepts may generate questions, but no proprietary third-party thresholds, rules, weights, chromosomes, or undisclosed implementation are assumed.

## Architectural separation
Evolve three linked but separately auditable layers.

### Layer A — Opportunity / stock-quality genes
Seed with the existing portable MTS research rather than discarding it:
- momentum
- trend
- breakout
- mean reversion / pullback / reversal
- volatility level/change
- volume / liquidity / money-flow proxies
- relative/cross-sectional strength
- market/regime structure
- earnings/event information where causally available
- sector-relative features
- breadth/context interactions

Allow GA to combine families, but retain lineage so we can tell whether improvement came from a new stock signal or from portfolio competition.

### Layer B — Portfolio-competition genes
New primary expansion space:
- cross-sectional candidate rank
- rank percentile / rank margin
- incumbent rank
- challenger minus incumbent score
- minimum challenger improvement required to switch
- incumbent persistence / rank decay
- rank-change velocity
- minimum holding period
- switch hysteresis / confirmation sessions
- cooldown after replacement
- portfolio slot count
- maximum simultaneous positions
- fixed versus bounded slot weights
- minimum candidate-quality threshold for filling a slot
- empty-slot behavior: safe asset rather than forced equity
- replacement priority: weakest incumbent versus closest comparable incumbent
- sector concentration cap
- correlation / common-factor exposure cap
- dispersion preference
- duplication penalty for highly similar genomes/signals
- optional portfolio marginal-contribution score: candidate benefit conditional on current holdings

### Layer C — Capital / market-state genes
Portfolio-level state remains distinct from stock selection:
- 0–100% equity exposure ceiling; NO leverage in this research stage
- residual capital -> 3% annualized safe-asset proxy
- existing causal systemic-state variables: MTS excitement, volatility expansion, breadth, acceleration, trend/MA structure, correlation/dispersion
- state-dependent slot count
- state-dependent minimum rank threshold
- state-dependent challenger improvement threshold
- block versus partial de-risk versus liquidation controller only as independently testable layer
- asymmetric recovery hysteresis

## Chromosome concept
A chromosome should encode a complete causal portfolio policy, not merely an entry condition. Conceptual form:

ELIGIBILITY -> QUALITY SCORE -> CROSS-SECTIONAL RANK -> SLOT/INCUMBENT COMPETITION -> SWITCH DECISION -> POSITION SIZE -> SAFE-ASSET RESIDUAL -> PORTFOLIO STATE CONTROL

Every decision must be reconstructable from information available before the trade decision. No future outcome information may enter ranking or switching.

## GA search strategy
Use hierarchical/co-evolutionary search rather than one giant unconstrained genome from the start.

Phase 1: freeze a representative library of existing portable opportunity genomes and evolve only portfolio-competition genes. This isolates whether architecture itself adds value.

Phase 2: allow competition genes to co-evolve with mixtures/weights of existing opportunity families.

Phase 3: permit new Layer-A feature combinations only after demonstrating that Layers B/C add portable value. This prevents a combinatorial explosion and tells us where improvement originates.

Phase 4: interaction expansion: state-dependent competition, e.g. a challenger may require a larger advantage during fragile/high-correlation states than during healthy dispersion.

## Scarcity / selective-switch experiments
Predeclare controls:
1. current independent-signal allocation;
2. top-N candidates with no incumbent protection;
3. top-N plus incumbent/challenger threshold;
4. top-N plus threshold + minimum hold/hysteresis;
5. above + safe-asset residual when fewer than N qualify;
6. above + diversification/correlation constraints;
7. above + existing systemic-state controller.

Candidate slot neighborhoods should be broad enough to discover structure, not copied from any observed portfolio: e.g. 5, 8, 10, 15, 20, 30, 50 slots. Challenger margins should be represented continuously/quantile-based where possible rather than arbitrary fixed percentages.

## Turnover is endogenous
Do NOT merely subtract transaction costs after selection. Switching itself should have an explicit hurdle. A challenger should be allowed to replace an incumbent only when its expected incremental benefit exceeds the estimated cost/friction plus a robustness margin.

Measure:
- gross turnover
- replacement turnover
- avoidable churn
- median holding period
- switches per year
- benefit per switch
- foregone gain from rejected challengers
- avoided loss from accepted switches
- net value added per unit turnover

## Safe-asset residual
Do not force all slots full. If only K candidates clear the quality/competition threshold, fill K slots and route remaining capital to the 3% safe-asset proxy. Test whether opportunity scarcity itself contains state information.

## Correlation/diversification expansion
Test as independent genes/constraints, not assumed truths:
- pairwise trailing correlation
- sector/industry overlap
- market beta/common-factor similarity if causally available
- return dispersion
- genome-family concentration
- marginal portfolio correlation

Question: can a slightly lower-ranked candidate improve portfolio outcome because it adds less shared downside exposure?

## Fitness / Pareto system
Do not optimize a single Sharpe-like scalar. Pareto remains controlling for advancement.

Primary dimensions:
1. terminal wealth / CAGR
2. positive-return / productive-state capture
3. MDD
4. CVaR5 and worst-day loss
5. negative-return / systemic-state capture
6. net-of-cost performance
7. turnover / value per switch
8. robustness across populations and eras
9. state discrimination
10. concentration / common-exposure risk where relevant

Use a predeclared near-Pareto tolerance for estimation noise. Standard deviation is diagnostic, not controlling.

## Anti-overfit requirements
- causal/PIT features only
- freeze evidence partitions before search
- GA discovery population distinct from advancement populations
- minimum event/trade counts
- neighboring-parameter stability
- lineage diversity: do not let one feature family monopolize population merely through near-duplicates
- complexity penalty / parsimony diagnostic
- transaction-cost stress
- crisis and normal-state decomposition
- four-era stability
- no untouched Verification data until the architecture has survived consumed-evidence development gates

## Research-space exhaustion audit before launch
Before freezing the executable protocol, classify existing MTS work into:
A. deeply searched and transported;
B. searched but weak/thin;
C. feature available but insufficiently combined;
D. architecture barely explored;
E. unavailable/missing data.

For each current family quantify number of generated genomes, portable survivors, transport breadth, parameter diversity, interaction depth, and downstream portfolio testing. The purpose is to decide whether Phase 1 should exploit existing genomes or whether specific Layer-A families deserve simultaneous expansion.

## Success criterion
Success is NOT merely higher gross return. The architecture is useful if scarce-capital competition produces a materially better asymmetric frontier: preserve more of MTS's profitable behavior, remove more harmful behavior, reduce unnecessary turnover, and remain robust across eras/populations after costs.

## Failure criterion
If selective competition mainly concentrates exposure, increases regime sensitivity, or achieves gross improvement only through unstable ranking/churn, reject the architecture even if one historical period looks excellent.

## Leverage
Explicitly excluded. Maximum equity exposure = 100%. Any future leverage research remains quarantined and requires separate validation of unusually high-probability setups.

## Phase 1 frozen launch definition
Phase 1 holds the existing MTS portable opportunity-genome catalog fixed. It does NOT search new Layer-A predictive genes. The search evolves only Layer-B portfolio competition and the safe-asset decision, using already-consumed evidence.

### Marginal safe-asset hurdle
Every equity slot competes not merely against other equities but against the 3% annualized safe asset. A candidate should receive capital only when its causal expected incremental value exceeds:
1. the safe-asset opportunity return over the relevant expected holding horizon;
2. estimated entry/exit friction;
3. any incremental switching friction if displacing an incumbent; and
4. a robustness margin evolved/tested without future information.

The GA may leave any number of slots empty. Empty capital receives the 3% proxy. Full equity investment is an outcome, not a requirement.

### Incumbent/challenger principle
A challenger must compete against the incumbent's current causal score, persistence, and switching cost. A tiny rank advantage is insufficient by construction unless the GA demonstrates that such switching adds robust net value. Candidate replacement thresholds/hysteresis are evolvable.

### Phase 1 evidence boundary
Use only already-consumed development evidence and the already-consumed heldout50/four-era laboratory as permitted by the final executable partition to be generated before the first GA fitness evaluation. Untouched Verification A remainder and Verification B remain sealed. No additional stock is opened merely to enlarge Phase 1.

### Phase 1 primary controls
- canonical current independent-signal allocation;
- fixed existing opportunity genomes + simple top-N competition;
- top-N + incumbent/challenger threshold;
- threshold + persistence/hysteresis;
- threshold + safe-asset hurdle/residual;
- diversification/correlation additions only after simpler competition architecture is measured.

### Current-controller relationship
The just-closed state-controller findings are frozen inputs, not tuning targets. Phase 1 first evaluates portfolio competition without silently reoptimizing the controller. The low-turnover `xexp_c5_block` and practical-knee `xexp_neg_c3_partial50` may later be layered as predeclared comparators after the competition mechanism is understood.

## Launch gate
This protocol becomes executable only after:
- research-space exhaustion audit is written;
- exact Phase 1 consumed-development partition is enumerated;
- GA chromosome schema/ranges are machine-readable and frozen;
- fitness/Pareto and near-Pareto tolerances are machine-readable and frozen;
- canonical baseline identity test is implemented;
- transaction-cost accounting is cost-matched;
- commit hash is recorded before first search evaluation.
