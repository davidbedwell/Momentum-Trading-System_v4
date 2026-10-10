# Normal-only follow-on experiment — immutable source and exclusion manifest (2026-10-10)

## Decision
Preserve the active 32-worker Generation 3 run unchanged. Its original full-history results are a baseline, not invalidated or relabeled. The follow-on Normal-only study excludes crash dates from **training and evaluation eligibility**, not from the immutable underlying market store.

## Candidate exclusion intervals — NOT YET SCIENTIFICALLY FROZEN
The earlier exploratory market-episode diagnostic used these intervals:
- GFC: 2007-07-01 through 2009-06-30
- COVID: 2020-02-01 through 2020-06-30
- 2022 bear: 2022-01-01 through 2022-12-31

These are candidate date boundaries only. They were chosen for diagnostics, not validated as causal regime boundaries. Final exclusion boundaries must be frozen before running Normal-only candidate comparisons. Do not tune boundaries to maximize returns.

## Implementation rules
1. Create a separate derived Normal-only eligibility mask; do not delete, mutate, or overwrite PIT predictors, execution arrays, genome definitions, or full-history results.
2. Exclude entry dates within frozen crash intervals. Flag and separately report any pre-crash entry whose holding horizon overlaps an excluded interval; do not silently treat those paths as ordinary Normal trades.
3. Apply the same mask to every candidate and every generation. Record interval definitions, source dataset hashes, candidate population, code commit, and output hashes.
4. Do not change an active GA's data, checkpoint, fitness, selection, or promotion semantics mid-run.
5. Keep DEV37 transport-only, DEV50 preserved and untouched, and BLIND17 final blind.
6. Keep crash-defense research and its episode diagnostic outside Normal parent-selection gates.
7. Treat normal-only re-ranking of candidates discovered on full history as **post-selection sensitivity analysis**, not an independent clean Normal-only discovery run. A new Normal-only GA is needed for true regime-specialist discovery.