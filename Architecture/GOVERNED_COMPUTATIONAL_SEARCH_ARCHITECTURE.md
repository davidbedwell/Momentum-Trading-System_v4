# MTS v4 Governed Computational Search Architecture

Date: 2026-09-28
Status: DESIGN BASELINE — implementation requires tests against governing amendments

## Purpose

Add massive inexpensive computational exploration beneath the AI Research Director without replacing Analysis or constraining RD scientific reasoning.

## Authority and data flow

Derived/PIT evidence -> Search Space Registry -> Search Optimizer <-> Analysis Engine -> Search Report -> AI Research Director

RD may then direct additional Search <-> Analysis iterations, direct Analysis work, create/modify families, or freeze a hypothesis for untouched validation.

## Core components

### SearchSpaceRegistry
Versioned definitions of available predictor genes, operators, parameter domains, structural constraints, outcome/horizon permissions, and family membership. Registration does not imply scientific value.

### StrategyFamily
A pluggable search-space profile. Initial implementation target: Momentum and Breakout. Framework must permit Trend, Mean Reversion, Volatility, Volume/Liquidity, Relative/Cross-Sectional, Event/Earnings, Market Structure/Regime, and cross-family composition.

### SearchOptimizer
Common protocol, not GA-specific. Inputs: authorized search space, discovery evidence reference, Analysis evaluation contract, objective vector, budget, seed, stopping conditions. Outputs: complete search ledger plus candidate/landscape report.

Initial optimizer: evolutionary/GA. Baseline optimizers should include random/quasi-random search so GA's added value can be measured rather than assumed.

### AnalysisAdapter
Translates candidate specifications into existing governed Analysis tasks/method executions. Analysis remains the calculator. Search must not create a parallel scientific/backtest authority.

### EvaluationCache
Semantic fingerprint of candidate + evidence + execution assumptions -> immutable deterministic result. Prevents paying compute repeatedly for equivalent phenotypes.

### SearchLedger
Append-only provenance: every unique candidate, ancestry/proposal source, objective components, Analysis refs, cache state, cohort/evidence identity, optimizer state, and compute telemetry.

### LandscapeReducer
Deterministic mechanical summarization only: exact/near duplicate collapse, parameter-neighborhood grouping, Pareto frontier construction, concentration statistics. It must preserve enough evidence for RD inspection and may not label scientific meaning.

### RDSearchReport
Compact but expandable package: search burden, candidate families, objective components, robust neighborhoods, failures/negative controls, sensitivity, concentration, costs, lineage, and exact Analysis references. Never only “the winner.”

## Family model

Families are search priors/grammars, not conclusions. A candidate may contain:
- observable entry predicates;
- direction;
- conjunction/disjunction structure within bounded complexity;
- horizon/holding policy;
- stop/invalidation/favorable-exit rules where authorized;
- context/regime predicates;
- cost/execution assumptions.

Cross-family composition should occur through explicit family identifiers and lineage, not by losing provenance in a single unrestricted genome.

## Initial families

Momentum: absolute/relative returns, skipped-month momentum, cross-sectional percentile, sector-relative strength, acceleration/deceleration, multi-horizon agreement, contextual breadth/regime.

Breakout: trailing range position/high-low structure, compression/volatility state, gap/volume participation, breakout magnitude, failed-breakout/re-entry structures, contextual market/sector state.

Do not invent missing features silently. SearchSpaceRegistry must distinguish currently implemented genes from proposed features requiring new deterministic computation.

## Fitness / objective vector

Do not default to raw return. Initial contract should support component outputs rather than one opaque score:
- path-executable gross/net expectancy;
- uncertainty/conservative estimate when requested;
- adverse excursion/risk-unit behavior;
- sample/opportunity count;
- temporal stability;
- cross-security stability;
- regime concentration;
- parameter-neighborhood stability;
- turnover and upper-bound costs;
- complexity/parsimony;
- concentration/independence;
- optional complementary value versus existing candidates.

Evolutionary selection may use Pareto ranking or an explicitly versioned aggregate objective. The component vector is retained regardless.

## Anti-overfitting design

Adaptive search sees Discovery only. Within Discovery, support chronological train/search and internal evaluation windows, rolling/walk-forward rotations, security-level splits, parameter perturbation, ablation, null/permutation controls, and search-over-null benchmark distributions.

Verification A/B remain inaccessible to Search.

## Efficiency design

1. Precompute reusable PIT features once.
2. Columnar/vectorized candidate evaluation where possible.
3. Semantic evaluation cache.
4. Batch candidates sharing outcome/horizon/path calculations.
5. Parallelize deterministic evaluations.
6. Early terminate objectively invalid/dominated candidates when doing so cannot bias retained metrics.
7. Compact RD reports; retain expandable provenance.
8. Spend AI tokens on interpretation and experiment design, not threshold enumeration.
9. Benchmark GA against cheaper random/quasi-random search.
10. Add GPU acceleration only after profiling shows the evaluation workload benefits.

## Suggested broader MTS improvements

### 1. Null-search calibration
Run the entire optimizer against shuffled/permuted outcomes. Measure the distribution of the best false discoveries after the same search budget. This directly informs RD interpretation of millions-of-trials selection effects.

### 2. Champion/challenger optimizer benchmarking
For the same family, evidence and compute budget, compare GA with random/quasi-random and later Bayesian/local optimizers. Keep the optimizer that finds broader, more stable empirical regions per unit compute—not merely the highest peak.

### 3. Feature lineage and availability registry
Every gene should declare PIT availability, source, transformation, lookback, missingness behavior, cost to compute, and whether it is predictor/context/outcome. Fail closed on unavailable or future-dependent genes.

### 4. Candidate complexity budget
Bound expression depth, number of predicates, threshold precision and interaction order. Complexity remains visible to RD. This reduces pathological curve fitting and improves executability.

### 5. Search-space versioning
A result is inseparable from the universe of possibilities available when it was found. Freeze and hash every search-space schema.

### 6. Ablation/inversion harness
For survivors, cheaply remove each component, invert relationships, perturb thresholds, and test neighboring horizons. Give Sol evidence about which pieces actually carry the effect.

### 7. Candidate-family independence map
Quantify overlap in signals/outcomes among survivors so Sol sees whether ten candidates are really one phenomenon.

### 8. Compute-budget governor
Hard limits by evaluations, wall-clock, CPU/GPU hours and optional dollar estimate. Resume from checkpoints without repeating Analysis.

### 9. Reproducible optimizer replay
Seed + search-space hash + evidence hash + software version should permit deterministic/reasonably reproducible replay, with nondeterministic hardware behavior explicitly recorded.

### 10. Preserve raw landscape access
Compression for Sol must never destroy access to underlying Analysis evidence. Sol can drill into any candidate, loser, neighborhood, control or direct Analysis question.

## Implementation order

Phase 0: governance + contracts + threat-model tests.
Phase 1: SearchSpaceRegistry, common SearchOptimizer protocol, SearchLedger, EvaluationCache, AnalysisAdapter.
Phase 2: random/quasi-random baseline + Momentum family; prove end-to-end mechanics cheaply.
Phase 3: GA/evolutionary optimizer on same frozen search space; compare against baseline.
Phase 4: Breakout family; prove family abstraction generalizes.
Phase 5: LandscapeReducer + compact RDSearchReport + Sol iterative loop.
Phase 6: null-search calibration, ablation, family-independence map, cross-family search.
Phase 7: add additional families based on measured value, not architectural enthusiasm.

## Acceptance conditions before paid autonomous use

- Search cannot access Verification A/B outcomes.
- Analysis remains deterministic calculation authority only.
- RD can bypass Search and query Analysis directly.
- Full multiplicity and lineage survive compaction.
- Identical candidate evaluations cache correctly.
- Search-space and evidence identities are immutable in a run.
- Null/control results cannot be suppressed.
- GA can be benchmarked against a non-GA optimizer under equal budget.
- Momentum and Breakout use the same core framework without family-specific forks.
- No search result can self-promote to validated hypothesis or trading eligibility.
