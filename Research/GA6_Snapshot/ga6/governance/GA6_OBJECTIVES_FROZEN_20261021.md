# GA6 research objective and validation governance — FROZEN DESIGN TARGET
Date: 2026-10-21. Status: APPROVED DESIGN, NOT CERTIFIED SOFTWARE.

## Scope
Retain existing GA6 general-market and 13-niche research, structural grammar, trading engine, max 40-session holding cap, risk controls, cost modeling, and PIT requirements. Engineering focus: concurrent discovery, parameter exploration, adaptive allocation, evidence accounting and later portfolio certification. Preserve at least 10 research elites per niche, separately flag certification. Do not silently substitute the six-role Genome sampling for executable grouped AND/OR logic; verify structural evaluator integration before claiming it.

## Discovery and selection
Find repeatable net-positive trading opportunities; do not maximize one in-sample fitness statistic. Account for slippage and costs before interpreting EV. Hard gates for statistical adequacy/frequency, tail losses and stability; rank survivors by at most three Pareto objectives: multiplicity-adjusted conservative net EV, capital-time efficiency, downside severity. Truncate per niche using deterministic crowding-distance/tie-breaking and bounded archives; maintain separate behavioral novelty archive. Do not equate positive fitness with novelty. Preserve rejected trials and full lineage.

## Multiple testing
Record ALL discovery and adaptive development-feedback trials, including failures and upweighted activities, with immutable trial IDs, data roles, parameter changes, candidate families, calendar dates, and test costs. Correct selection bias using calendar-block resampling across tickers, preserving market shocks, overlapping positions and serial dependence. Preregister benchmark and loss differential; SPA tests global superior predictive ability, and a dependence-aware stepwise procedure (Romano-Wolf/StepM) identifies survivors if justified. Deflated Sharpe is diagnostic, not a substitute for the family-wide ledger.

## Data roles and leakage
Discovery and adaptive development-feedback are BOTH model development; delayed rewards may only use development feedback. Locked validation and final holdout are separate, strictly single-use; no feedback to allocator or strategy design. Pre-register pass/fail criteria, permitted consultations (one each), data fingerprints and failure handling before accessing either. Failed/consulted locked data is retired into development; cannot be relabeled independent, and any replacement requires genuinely untouched data. Final holdout is never reused. All splits chronological and purged/embargoed. Compute per-split information horizon from maximum holding cap, longest feature lookback and state carry-over; record calculation and dates. Check usable duration and multiple-regime representation before selecting four segments; if insufficient, report infeasibility instead of fabricating independence.

## Adaptive compute
Start with 45% new structure+Sobol, 20% further Sobol, 25% evolutionary offspring, 10% challengers; update roughly every five generations. No activity >60%; minimum exploration and 13-niche protection. Delayed activity credit only after comparable dev-feedback outcomes, normalized for difficulty and CPU time, with pending-reward accounting and exploration safeguards. Raw positive fitness is NONCOMPLIANT as an allocator reward and MUST NOT be used for production promotion.

## Portfolio and evidence
Portfolio objective is compounded growth under explicit drawdown, expected-shortfall, exposure, overlap, cost and execution constraints; 35% CAGR is a research target, not evidence. Select by predeclared overlap-aware greedy forward simulation with nested chronological development folds, freeze algorithm before independent evaluation. Preserve generalists and niche specialists; candidate standalone EV does not imply portfolio value. 79-ticker DEV dataset is exploratory pending membership/provenance verification; do not label it PIT S&P500 certification. Validate PIT membership and realistic cost/slippage assumptions before interpretation.

## Release requirements
Versioned implementation, unit and integration tests, independent evaluation of discovery feedback and accounting, full portfolio replay, checkpoint resume, preflight, data provenance and research manifest. Do not mutate running GA6 or stop it until replacement passes release gates. No silent deviation; any change to this frozen design requires explicit approval.
