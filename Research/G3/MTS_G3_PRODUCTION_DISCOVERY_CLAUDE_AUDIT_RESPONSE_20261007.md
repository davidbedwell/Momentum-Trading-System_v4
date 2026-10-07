

# Cold Methodological Audit — MTS G3 Production Specialist Discovery Protocol

Reviewer: Independent methodological audit
Date: 2026-10-07
V3 outcome: NOT PROVIDED / NOT CONSULTED

---

## 1. Search Reachability

### 1A. Feature-space combinatorial coverage vs. budget

**MAJOR**

The genome grammar allows 2–8 modules, each with 1–4 predicates × 1–6 opportunity terms × direction × lifecycle parameters. A conservative lower bound on the structured search space exceeds 10^30 configurations. The budget is 409,600 island-individual-generation slots (before cache hits). Even accounting for mutation/crossover locality, the protocol provides no analysis or even heuristic estimate that the search can reach meaningfully diverse behavioral regions rather than collapsing to a few basins per island.

**Fix:** Before freeze, require a reachability pre-study: run 2 islands for 20 generations on development data and measure (a) the fraction of CVT cells ever occupied, (b) effective behavioral diversity trajectory, (c) proportion of random immigrants that reach cells not previously occupied. If CVT occupancy at generation 20 is <15% of 256 cells across both islands combined, either increase population, generation budget, or immigration rate, or justify the shortfall. Log the pre-study result in the search ledger; it does not constitute outcome-based budget adjustment because it uses only development data and measures coverage, not quality.

---

### 1B. Island plateau freeze — free-rider starvation of diversity

**MAJOR**

"Second consecutive plateau freezes that island and stops further evolutionary evaluation work there; freed worker capacity is reallocated to active islands without changing any population size." This means frozen-island genomes stop evolving but no new island is spawned. If 6 of 8 islands plateau early, all 64 cores serve only 2 islands of fixed population 256 — the extra cores accelerate generation throughput but do not expand the population or search frontier. The protocol explicitly forbids changing population size, so the cores can only reduce wall-clock time, not improve reachability. In the worst case diversity collapses to two basins.

**Fix:** When an island freezes, allow one of two pre-committed options (chosen before launch): (Option A) spawn a fresh random-initialised island of population 256 inheriting the freed workers but sharing no genetic material; or (Option B) permit the receiving active islands to temporarily expand population by up to 50% with fresh random immigrants only (not clones), reverting at next migration. Either option must be declared and frozen before launch. Log the choice and every triggered reallocation.

---

### 1C. Migration novelty criterion undefined

**MINOR**

"Migration every 20 generations moves behaviorally novel genomes only" — no operational definition of "behaviorally novel" for migration eligibility is given. Is it novelty relative to the receiving island's population? A threshold on behavioral distance? Top-k by archive sparseness?

**Fix:** Define: a migrant is eligible if its behavioral descriptor's Euclidean distance to the nearest member of the receiving island's current population exceeds the receiving island's median nearest-neighbor distance. Evaluate migrant on receiving-island semantics before admission. Log all migration eligibility decisions.

---

## 2. Genome Breadth / Named-Strategy Leakage

### 2A. "Return-path shape coefficients" and "action-sequence frequencies" in behavioral descriptor

**MINOR**

These descriptor components are not operationally defined. "Return-path shape coefficients" could be anything from Fourier coefficients to polynomial fits. Ambiguity here risks post-hoc descriptor shopping or inadvertent embedding of a named strategy archetype.

**Fix:** Specify the exact computation: e.g., "cubic polynomial coefficients fit to the cumulative-return path normalised to unit duration and unit terminal return, yielding 4 coefficients (a0–a3)." Similarly define action-sequence frequencies as the empirical frequency vector over a declared enumeration of lifecycle action n-grams. Freeze definitions in the descriptor manifest before launch.

---

### 2B. Direction policy "conditional sign" is under-specified

**MINOR**

The genome grammar allows direction policy: "long, short, or conditional sign." The conditional variant's structure is not bounded. If it can reference arbitrary feature expressions, it effectively doubles the predicate budget per module and may encode complex regime-switching.

**Fix:** Constrain conditional sign to reference exactly one already-declared applicability predicate from the same module with a deterministic sign map (predicate true → long, false → short, or vice versa). Log the constraint in grammar documentation.

---

## 3. QD / Pareto Mechanics

### 3A. Pareto front size can collapse under strict 3-objective dominance with uncertainty bounds

**MAJOR**

With three objectives each evaluated via bootstrap confidence bounds (LCB for reward, UCB for downside and duration), dominance becomes very hard to establish — most organisms will be mutually non-dominated, yielding a massive Pareto rank-1 set. Tournament selection then falls through to behavioral novelty, effectively turning the algorithm into pure novelty search with no exploitation pressure. Conversely, if by chance the bounds are tight for a few organisms, the front could be tiny.

**Fix:** Add a pre-committed diagnostic: after the first 10 generations on each island, report the Pareto rank-1 fraction. If >90% of the evaluated population is rank-1, switch tournament tiebreaker order to: (1) Pareto rank, (2) lower uncertainty width (mean across objectives), (3) behavioral novelty. This preserves exploitation incentive while keeping novelty as final tiebreaker. The switch rule and threshold must be frozen before launch and is not outcome-dependent — it is structural.

---

### 3B. Bootstrap cluster definition — temporal overlap criterion is ambiguous

**MAJOR**

"Signals whose forward paths overlap in time and share broad market exposure are one cluster." This is the only definition of the bootstrap resampling unit, yet it leaves critical decisions unspecified:

- What constitutes "broad market exposure"? Correlation? Sector? Beta bucket?
- What overlap fraction triggers clustering — any single day, >50% of holding period?
- Is clustering transitive (A overlaps B, B overlaps C → all one cluster)?

The cluster count directly determines the effective sample size for every bootstrap bound and thus every promotion decision. Ambiguity here is a first-order threat to pseudoreplication control.

**Fix:** Specify: two events belong to the same cluster if their holding periods share ≥1 calendar day AND their entry-date broad-market-beta quintiles (computed from a pre-frozen market model on development data) are identical. Clustering is transitive (connected components). Log the market-beta quintile breakpoints and the resulting cluster count distribution across organisms. If any candidate's cluster count falls below 25, it cannot promote (already required, but now mechanically defined). Freeze this definition before launch.

---

### 3C. 500 bootstrap resamples — adequacy for 3-objective tail quantiles

**MINOR**

500 resamples provide ±~4.5% sampling error on the 10th percentile bootstrap quantile. For a 3-objective Pareto treatment where dominance hinges on these bounds, Monte Carlo noise in the bounds may cause non-reproducible archive membership.

**Fix:** Increase to 2000 bootstrap resamples for archive-contender evaluation (the protocol already permits cheap point estimates for non-contenders, so compute cost is bounded). Alternatively, record and freeze the bootstrap seed per organism so that archive membership is deterministic given the seed, and log sensitivity to seed choice for a 5% subsample.

---

## 4. Uncertainty / Pseudoreplication

### 4A. Cost robustness only tested at discrete points, not at the archive boundary

**MAJOR**

Archive promotion requires LCB > 0 at 10 bps and point mean > 0 at 20 bps. But the cost schedule (0/5/10/20/50 bps) is discrete; no interpolation or monotonicity check is required. An organism that is profitable at 10 bps and 20 bps but not at 15 bps (due to non-linear turnover interaction) could promote. More importantly, the protocol does not require that the *bootstrap LCB* remain > 0 at 20 bps — only the point mean. This is inconsistent: the 10-bps gate uses a rigorous uncertainty bound, but the 20-bps stress test drops to a point estimate, creating a weak link.

**Fix:** Require bootstrap LCB > 0 at 10 bps (already present) AND bootstrap LCB > 0 at 15 bps (interpolated by re-evaluating at 15 bps, not by arithmetic on 10/20 results). The 20-bps point-mean check may remain as an additional screen. This closes the gap without requiring full uncertainty at 20 bps (which would be overly conservative for discovery).

---

### 4B. Perturbation robustness check — "75% of deterministic perturbation cases" may be too lenient

**MINOR**

With ~N numeric thresholds per genome (entry threshold, take-profit, stop-loss, horizon, add, reduce, trailing, abstention — roughly 7–15 per organism), a ±10% perturbation grid produces a large combinatorial space. The protocol says "perturbing every numeric threshold by ±10%" but does not specify whether this is one-at-a-time or joint. If one-at-a-time with ~12 parameters → 24 perturbations → 75% = 18 must pass. If joint (3^12 ≈ 531k), the check is computationally prohibitive.

**Fix:** Specify: perturbation is one-at-a-time (each parameter ±10%, others held), producing 2N cases. At least 75% of these 2N cases must show median net reward > 0. Log N and the pass fraction. This is computable and interpretable.

---

### 4C. No explicit handling of survivorship / delisting bias in opportunity evidence

**MAJOR**

The feature boundary section requires PIT timing but says nothing about survivorship bias in the ticker universe. If the simulation universe excludes delisted stocks, the specialist may learn to avoid situations that historically led to delisting — a form of look-ahead. Conversely, including delisted stocks requires careful handling of terminal returns.

**Fix:** Require that the simulation universe includes all tickers present in the source data at each decision timestamp, including those that subsequently delist. Terminal events (delisting, acquisition, bankruptcy) must be handled with a pre-committed return convention (e.g., use last available price, or CRSP delisting return if available) declared and frozen before launch. Log the convention and the fraction of opportunity events that involve terminal tickers.

---

## 5. Archive Promotion Thresholds

### 5A. Ticker concentration rule has a loophole for short specialists

**MINOR**

"No single ticker supplies >50% of positive net PnL" — for a short specialist, PnL comes from price declines. If the specialist fires on 50 tickers but one ticker's collapse dominates positive PnL, this is the same concentration risk. The rule as written applies, but "positive net PnL" for a short position may be ambiguous if the accounting convention isn't specified.

**Fix:** Clarify: "positive net PnL" means the contribution to total profit from events with positive realized returns (i.e., profitable events), regardless of direction. Equivalently: for each ticker, sum the PnL of all profitable events involving that ticker; no single ticker's sum may exceed 50% of the total profitable-event PnL.

---

### 5B. Promoted QD archive cap — 4 per cell × 256 cells = 1024 max, but Pareto rank used for eviction

**MINOR**

When a cell already has 4 candidates and a new non-dominated candidate enters, the eviction rule ("uncertainty-aware Pareto rank then novelty") may systematically evict the most novel organism in favor of a more typical high-performing one, undermining the QD purpose.

**Fix:** Evict by: first remove any dominated organism; if all 5 are mutually non-dominated, evict the one with smallest behavioral distance to its nearest neighbor in the same cell (least novel within-cell). This preserves within-cell diversity.

---

## 6. Multiplicity

### 6A. Null calibration method not specified

**MAJOR**

"Production discovery reports empirical false-discovery burden from the already frozen matched-null gate plus max-statistic null calibration for archive promotion." The matched-null gate and max-statistic calibration are referenced but not defined in this protocol. How many null runs? What is the null genome? Is it a permutation null (shuffled labels), a random-genome null (random genomes evaluated identically), or a time-shifted null? The choice materially affects the false-discovery estimate.

**Fix:** Specify: (a) Matched null: run N_null ≥ 4 complete evolutionary searches (same budget, grammar, features) on time-permuted return series (block-permuted with block size = 60 sessions to preserve local autocorrelation but destroy cross-sectional signal). (b) Max-statistic calibration: from each null run, record the best LCB achieved by any promoted genome. The empirical max-statistic null distribution is the set of these N_null maxima. A production candidate's LCB must exceed the 75th percentile of this null distribution (in addition to all other promotion criteria). (c) Report the full null archive size and quality distribution alongside the production archive. Freeze N_null and block size before launch.

---

### 6B. Restart policy underspecified

**MINOR**

"No unlogged restart is permitted" but the protocol does not define what constitutes a restart vs. a resume. If a machine crashes at generation 87 and resumes from the generation-87 checkpoint, is that a restart? If someone re-launches from generation 0 with a different random seed, is that a new experiment?

**Fix:** Define: a *resume* replays from the last valid checkpoint and must reproduce the state hash; it is not a new multiplicity entry. A *restart* is any launch from generation 0 or from a checkpoint with any changed parameter (including seed); it is a new multiplicity entry and counts against the search budget. Log both.

---

## 7. Scope Leakage

### 7A. Scope generation uses discovery-data firing distributions — circularity risk

**MAJOR**

Scope is "generated only from causal observable firing/context distributions on discovery data." But the candidate genome was *optimized* on the same discovery data. This means scope boundaries are implicitly optimized — the genome learned to fire in profitable regions, and the scope is then drawn around those regions. At transport, a scope that was effectively fit to discovery data may not generalize.

**Fix:** One of: (a) Generate scope from a held-out scope-calibration fold (e.g., the first 20% of discovery data by time, excluded from fitness evaluation). The genome is still evaluated on the remaining 80%. (b) Require scope boundaries to be defined only from pre-committed feature quantile breakpoints (e.g., volatility deciles, sector membership) that do not depend on where the genome actually fired. (c) If neither is feasible, flag scope as provisional and require scope validation at transport using a pre-committed boundary-stability test (the scope must contain ≥80% of transport-period firings without boundary adjustment). Option (b) is simplest and most robust.

---

## 8. Protected-Data Barriers

### 8A. No explicit data-partition definition

**MAJOR**

The protocol references "discovery data," "development data" (for descriptor scaling), and "transport data" (downstream) but never defines the temporal or structural boundaries between them. Without an explicit, immutable partition definition, there is no auditable barrier.

**Fix:** Add a data-partition manifest: define discovery data as [date_start, date_end], development data (for descriptor scaling/CVT fitting) as a subset [dev_start, dev_end] ⊂ [date_start, date_end] or a structurally separate sample, and transport data as [transport_start, transport_end] with transport_start > date_end + gap (specify gap ≥ 0 sessions). Freeze all boundaries before launch. Hash all data partitions. No organism may be evaluated on transport data until candidate freeze.

---

### 8B. Development data used for descriptor scaling — potential information leakage into search

**MINOR**

"Descriptors are robust-scaled using development data only and frozen at launch." If development data is a subset of discovery data, then descriptor scaling parameters (medians, IQRs) encode information about the data on which genomes are evaluated. This is standard practice and low risk, but the protocol should clarify whether development data is discovery data or a separate sample.

**Fix:** Clarify: if development data ⊂ discovery data, this is acceptable but must be documented. If development data is separate, document the source. In either case, descriptor scaling parameters are frozen before the evolutionary run begins and are not updated.

---

## 9. Compute Budget

### 9A. No wall-clock budget or timeout

**MINOR**

The protocol caps evolutionary work in island-individual-generation slots but has no wall-clock limit. A pathological genome that takes extremely long to evaluate (e.g., fires on every ticker at every timestamp) could stall the run indefinitely.

**Fix:** Add a per-organism evaluation timeout (e.g., 120 seconds wall-clock). Organisms exceeding the timeout are assigned worst-rank on all objectives and flagged. Add a total wall-clock hard stop (e.g., 14 days) after which the run terminates and outputs whatever archives exist. Both limits frozen before launch.

---

### 9B. 409,600 slots × (evaluation cost) — no estimate of per-slot cost

**MINOR**

The protocol requires "exact one-generation benchmark must be recorded before launch ETA is published" — good — but does not require a go/no-go decision if the benchmark reveals the run is infeasible within available compute.

**Fix:** Add: if the one-generation benchmark × 200 generations × 8 islands exceeds 14 days wall-clock on 64 cores (or whatever the hard wall-clock stop is), the protocol must be revised (e.g., reduce population or generations) before launch. This is a pre-committed feasibility gate.

---

## 10. Checkpoint / Restart

### 10A. State hash verification on resume is good but hash algorithm not specified

**MINOR**

"Resume must reproduce uninterrupted state hashes" — what hash? SHA-256? CRC32? The choice affects collision resistance and auditability.

**Fix:** Specify SHA-256 for all checkpoint state hashes. Log the hash with every checkpoint. Resume verification compares the SHA-256 of the recomputed state from the checkpoint against the stored hash.

---

### 10B. Checkpoint storage and retention policy

**MINOR**

Checkpoints every generation across 8 islands × 200 generations = 1,600 checkpoints. Size is unspecified. If each is large, storage may be a practical issue.

**Fix:** Specify: retain all checkpoints, or retain every 10th generation plus the last 3 consecutive checkpoints per island. Estimate per-checkpoint size in the pre-launch benchmark. Total checkpoint storage must not exceed a pre-committed limit (e.g., 500 GB).

---

## 11. 64-Core Utilization

### 11A. Parallelization architecture not specified

**BLOCKER**

The protocol says "Full 64-core worker pool is used for organism evaluation; BLAS threads fixed to 1" but does not specify *how* cores are allocated to work. Key questions:

- Are organisms within a generation evaluated in parallel? (Presumably yes, but not stated.)
- Is there a master/worker architecture, or are islands themselves parallelized (8 islands × 8 cores)?
- Can organisms from different islands be evaluated concurrently?
- What is the synchronization model — synchronous generational (all organisms evaluated before selection) or asynchronous?

Without this, there is no way to verify that 64 cores are actually used, or that the parallelization does not introduce non-determinism that breaks checkpoint reproducibility.

**Fix:** Specify: (a) Synchronous generational model: all organisms in a generation are evaluated before selection proceeds. (b) Within a generation, organism evaluations are distributed across the 64-core pool as independent tasks (no shared mutable state). (c) All 8 islands' current-generation organisms may be queued concurrently into the shared pool. (d) Evaluation results are deterministic regardless of execution order (no floating-point order dependence across organisms). (e) Checkpoint hashes cover the full population state after each synchronous generation boundary. (f) Pre-launch benchmark must demonstrate ≥85% CPU utilization across 64 cores during organism evaluation phases.

---

### 11B. Island plateau freeze — core reallocation mechanics

**MINOR**

Linked to Issue 1B. When an island freezes, the protocol says cores are reallocated but doesn't specify how the job scheduler redistributes work. If the scheduler is unaware of island state, frozen-island cores may idle.

**Fix:** Specify: the work queue draws from active islands only. Frozen islands submit no evaluation tasks. The scheduler is stateless with respect to island identity — it simply processes the next available task. Log per-generation core utilization.

---

## 12. Additional Issues

### 12A. No explicit treatment of non-stationarity within discovery data

**MAJOR**

The discovery window may span years. Market structure, volatility regimes, and sector composition change. A genome that works only in one sub-period may promote if overall statistics pass thresholds. The protocol has no requirement for temporal stability within discovery data.

**Fix:** Add a sub-period consistency check to promotion criteria: split discovery data into 3 equal temporal thirds. A candidate must show point-estimate positive net return at 10 bps in at least 2 of 3 thirds. This is a weak filter that catches pure-regime specialists without requiring uniform performance. Log per-third statistics for all candidates.

---

### 12B. "Causal feature" used without definition

**MINOR**

The term "causal feature" appears throughout but is never defined. In the context of this protocol, it appears to mean "observable feature available at decision time with verified publication timing" — i.e., a look-ahead-free feature. The word "causal" implies a stronger epistemological claim.

**Fix:** Replace "causal feature" with "decision-eligible feature" or define "causal" explicitly in a glossary section: "'Causal' in this protocol means: the feature value is determined solely by information published before or at the decision timestamp, as verified by the PIT timing test. No claim of economic causation is made."

---

### 12C. No explicit handling of identical/near-identical genomes across islands

**MINOR**

If two islands independently converge to the same genome (or near-identical genomes), they count as separate organisms in the archive. This inflates apparent diversity and multiplicity burden without adding real discovery.

**Fix:** Define genome identity: two genomes are "duplicates" if their behavioral descriptors are within Euclidean distance ε (pre-committed, e.g., 0.01 after scaling) and their opportunity evidence overlap (Jaccard on fired-event sets) exceeds 0.95. Duplicates from different islands are merged in the archive (keep the one with lower uncertainty width). Log all merges.

---

## Summary Table

| # | Issue | Severity | Section |
|---|-------|----------|---------|
| 1A | Reachability not assessed | MAJOR | Search |
| 1B | Plateau freeze starves diversity | MAJOR | Search |
| 1C | Migration novelty undefined | MINOR | Search |
| 2A | Descriptor components undefined | MINOR | Genome/QD |
| 2B | Conditional sign unbounded | MINOR | Genome |
| 3A | Pareto front may collapse or explode | MAJOR | QD/Pareto |
| 3B | Cluster definition ambiguous | MAJOR | Uncertainty |
| 3C | 500 bootstrap resamples thin for tails | MINOR | Uncertainty |
| 4A | Cost robustness gap at 15 bps | MAJOR | Promotion |
| 4B | Perturbation scheme ambiguous | MINOR | Promotion |
| 4C | Survivorship bias unaddressed | MAJOR | Data |
| 5A | Ticker concentration for shorts ambiguous | MINOR | Promotion |
| 5B | QD eviction undermines diversity | MINOR | QD |
| 6A | Null calibration unspecified | MAJOR | Multiplicity |
| 6B | Restart vs. resume undefined | MINOR | Multiplicity |
| 7A | Scope circularity with discovery data | MAJOR | Scope |
| 8A | Data partitions undefined | MAJOR | Data |
| 8B | Development data source ambiguous | MINOR | Data |
| 9A | No wall-clock timeout | MINOR | Compute |
| 9B | No feasibility go/no-go gate | MINOR | Compute |
| 10A | Hash algorithm unspecified | MINOR | Checkpoint |
| 10B | Checkpoint retention unspecified | MINOR | Checkpoint |
| 11A | Parallelization architecture missing | BLOCKER | Compute/Cores |
| 11B | Core reallocation mechanics missing | MINOR | Compute |
| 12A | No temporal stability check | MAJOR | Promotion |
| 12B | "Causal" undefined | MINOR | Terminology |
| 12C | Cross-island duplicate handling missing | MINOR | Archive |

**Counts: 1 BLOCKER, 10 MAJOR, 16 MINOR**

---

## FREEZE DECISION

**FREEZE_READY: NO**

The protocol has **1 BLOCKER** (parallelization architecture is unspecified, making it unverifiable that 64 cores are actually utilized and that determinism is maintained) and **10 MAJOR** issues spanning cluster definition ambiguity, data partition boundaries, null calibration, scope circularity, survivorship bias, search reachability, Pareto front dynamics, temporal stability, cost robustness, and island plateau handling. Several of these (3B, 6A, 8A, 11A) could individually invalidate the experiment's scientific claims.

**Minimum path to freeze:** Resolve the BLOCKER and all MAJOR issues. MINOR issues should be addressed but are not individually gate-blocking. After revisions, re-audit before freeze.
