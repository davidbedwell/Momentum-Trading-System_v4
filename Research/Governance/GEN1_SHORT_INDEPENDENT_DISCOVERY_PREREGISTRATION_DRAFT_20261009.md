# SHORT-only discovery preregistration — engineering draft, NOT frozen

Status: DRAFT FOR REVIEW; no GA launch or selection authorized. Original Gen1 168-parent allocation unchanged.

## Research hypothesis and primary comparison
A separately evolved SHORT entry genome, using point-in-time signals and a predeclared holding policy, can achieve positive net returns after conservative executable short-sale costs and outperform matched passive SHORT exposures on the same entries. Existing 12 preliminary SHORT genomes are reference comparators only; do not seed populations with them or optimize toward their rules/results.

## Scope and protection
DEV80 discovery only. No DEV37, DEV50, BLIND17 reads. No future market-state labels, trough-based hindsight, or data-derived episode boundaries selected using returns after the entry date. Preserve the original 4,360 and all original 12 SHORTs. Never assume stock-day trade rows or overlapping positions are independent market episodes.

## Evolution and measurement
Use the original 8 gene families, SHORT-only chromosomes, canonical genotype deduplication, declared mutation/crossover operators, bounded compute and deterministic seeds. Freeze population size, generations, stop/plateau rules and costs before running. Compare a predeclared family of horizons (original 1,2,3,5,7,10,15,20,63 first); expanded 1–126 horizons require separate multiplicity budget. Evaluate chromosome and horizon together without choosing the best horizon on test data. All prospective portfolio signals must be executable at the next valid open after information availability.

## Episodes and uncertainty
Predefine disjoint chronological train/selection/test periods and purging/embargo covering maximum holding length. Report separately the GFC, COVID shock/rebound, 2022 bear and other distinct market episodes when covered by DEV80, but do not claim independent crash validation from many stocks during the same event. Include positive/negative regime control episodes. Treat the number of independent episodes as the effective upper bound on event-level generalization. Predeclare multiplicity control across genomes/horizons/regimes (e.g. episode-blocked max-statistic resampling), with frozen seeds, family-wise error 0.05 and confidence intervals; document low-power failure where too few episodes exist.

## SHORT-specific execution gates
Audit historical borrow availability, borrow fee, hard-to-borrow restrictions, recall, dividend liability, price gaps, delisting outcomes, liquidity, impact, spread and regulatory costs. Distinguish historical measured fees from synthetic assumptions. If borrow histories or delisting returns are missing, classify performance as non-executable research proxies, not certified tradeable alpha. Benchmark against matched passive short and cash on the same dates and cost conventions. Require realistic concurrent-position and equity/margin constraints and portfolio CAGR/MDD before promotion.

## Stop rules and certification
No fixed LONG/SHORT quota. Fail closed if insufficient independent episodes, PIT release timestamps, borrow evidence, costs, sample support, or multiplicity-adjusted advantage. Do not expand the search after seeing test results. No Gen2 parent-pool amendment without explicit approval after certified SHORT results. Freeze final numerical hyperparameters and thresholds before any discovery run.

## Prerequisites still unresolved
1. Historical borrow/fee and delisting availability and coverage.
2. Source-feature release-time provenance and timestamp contracts.
3. Numerical GA configuration, resource budget, and selection criteria.
4. Exact episode segmentation and multiplicity resampling implementation with synthetic tests.
5. Economic portfolio simulation and sample sufficiency rules.
