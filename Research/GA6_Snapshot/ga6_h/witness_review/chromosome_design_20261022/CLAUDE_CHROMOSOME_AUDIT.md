# GA6-H Chromosome Design Audit — Adversarial Quantitative Review

## Executive Summary

The architecture is structurally sound in its separation of concerns. The critical failures are concentrated in three areas: the diagnostic evaluator is a pure mathematical toy with zero connection to actual signal quality; the Pareto archive has a subtle stagnation-reset omission that will silently fail; and the simulator has several execution-realism gaps that will produce optimistic results. The chromosome grammar itself is mostly correct but has one meaningful restriction bug.

---

## (1) Chromosome Grammar, Tree Validity, Crossover, Mutation

### MUST-FIX

**Repeated-family prohibition is silently inherited.** `validate_tree` checks for duplicate *identical leaves* (same feature+window+transform+direction+threshold tuple), which is correct. However `random_genome` in `context_free_genome.py` draws leaves independently with no family-diversity enforcement, so you can get `momentum/20/zscore` and `momentum/40/rank` as siblings — this is fine and the spec explicitly wants it. **But** `crossover()` in `context_free_genome.py` uses `seen` to deduplicate by full leaf tuple, which is correct. The GA6 prohibition on repeated family is NOT present in this code. Confirm this is intentional and document it explicitly. **No code change needed, but add an assertion test.**

**`tree_crossover` in `genetic_operators.py` has a path-corruption bug.** When `target` is the empty tuple `()` (root node), the condition `if not target:` is `True` and replaces the entire tree with `donor`. But `donor_candidates` filters `if target or 'children' in n` — when `target=()`, `bool(())` is `False`, so it requires `'children' in n`, meaning a leaf donor at root is impossible. This is logically inconsistent: you can replace root with a branch donor but never with a leaf, silently skipping root-replacement when donor is a leaf. **Low impact but semantically wrong.** Fix: `if target == ():` explicitly.

**`structural_mutation` `group` action requires `len >= 3` but `ungroup` has no minimum-children guard.** After ungrouping, a branch could have 1 child, which fails `validate_tree`'s `len(children) < 2` check. The `try/except ValueError: continue` catches this, so it silently retries — not a crash, but wastes mutation budget. Add explicit guard.

**`crossover` in `context_free_genome.py` produces flat trees only.** It always creates `{'op':..., 'children': pool[:8]}` — a single-level tree. This destroys nested structure from parents. After 10 generations, population converges to depth-1 trees. `tree_crossover` in `genetic_operators.py` preserves depth correctly. **Use `tree_crossover` as the primary operator; demote `context_free_genome.crossover` to a fallback or remove it.**

### LOW-COST HIGH-VALUE

**`lag` gene is in the spec but absent from the code.** The spec says `Leaf: (feature_id, lag>=0, window, ...)`. The `leaf()` function and `validate_tree` have no `lag` field. Either remove `lag` from the spec or add it. Missing it means you cannot test "momentum 5 days ago" vs "momentum today" — a meaningful search dimension.

**`missing_policy` gene is in the spec, absent from code.** `score_tree` hard-codes `return None` on missing features (fail-closed). The spec lists `missing_policy` as a leaf gene. For exploratory research, fail-closed is defensible. Document the deviation explicitly.

---

## (2) Discovery-Only Fitness

### MUST-FIX BEFORE FIRST EXPERIMENT

**`diagnostic_evaluator` is not fitness — it is a mathematical function of genome parameters with zero connection to price data.** `net_ev = 1/(1+|hold_sessions-15|)` rewards hold=15 regardless of any signal quality. This will evolve chromosomes that hold for 15 sessions with low stop-losses, not chromosomes that find alpha. **Running the GA with this evaluator produces meaningless results that cannot be called "discovery."** The spec correctly warns "NOT historical trading evidence" but the architecture provides no path to plug in a real evaluator before the first experiment.

**Minimum viable real evaluator needed before first run:** For each chromosome, on a rolling training window, compute cross-sectional rank of each stock at close-t, then measure realized forward return at t+N (N = hold_sessions gene) for stocks that passed the entry filter. Fitness metrics:
- `net_ev`: mean(forward_return_top_k - forward_return_bottom_k) net of 20bps round-trip
- `ev_per_session`: net_ev / hold_sessions
- `reliability`: fraction of rolling windows where net_ev > 0
- `training_consistency`: Spearman rank-IC averaged across windows, sign-consistent fraction
- `opportunity_coverage`: mean daily count of passing stocks / universe size

This requires price data and feature computation. **Without this, the GA is a random genome generator with a preference for hold=15.**

**EPS values in `discovery_fitness.py` are arbitrary and untested.** `EPS['net_ev'] = 0.0001` means two chromosomes with net_ev of 0.0050 and 0.0051 land in different cells and are treated as meaningfully different. With noisy return estimates, this granularity is finer than estimation error. Consequence: archive fills with noise-differentiated cells, stagnation counter never triggers, reset never fires. **Set EPS to at least 1 estimated standard error of each metric on your training sample size.** Rough starting values: `net_ev: 0.002`, `ev_per_session: 0.0002`, `reliability: 0.05`, `training_consistency: 0.05`, `opportunity_coverage: 0.02`.

### LOW-COST HIGH-VALUE

**`opportunity_coverage` as `leaves/8` in the diagnostic evaluator is structurally wrong even as a placeholder.** More leaves does not mean more opportunities. Real coverage = count of (date, stock) pairs passing the filter / total eligible (date, stock) pairs. A chromosome with 8 leaves all requiring AND will have near-zero coverage; one with 2 OR leaves will have near-100%. The current proxy actively selects for complex AND trees.

**No fitness penalty for zero-trade chromosomes.** The spec correctly flags this. A chromosome that never fires gets `opportunity_coverage = 0` which is Pareto-dominated on that dimension — this is handled correctly *if* the real evaluator computes it. Verify the real evaluator explicitly returns 0.0 (not NaN) for zero-trade genomes.

---

## (3) Pareto Selection, Archive, Stagnation Reset

### MUST-FIX

**Stagnation reset is specified but not implemented.** `evolution_engine.py` tracks `last_improvement` and stops at `patience=100` generations of no archive improvement. The spec says "100-generation stagnation reset" — meaning *reset the population*, not *stop*. The current code terminates. If the intent is reset-and-continue: replace the `while` exit condition with a population re-initialization from `random_genome` while preserving the archive, then reset `last_improvement`. **This is a 10-line fix with significant search coverage impact.**

**Archive `update_archive` comparison uses Python tuple comparison on metrics dict values.** The tiebreak `(tuple(entry['metrics'][k] for k in OBJECTIVES), entry['genome'])` relies on `OBJECTIVES` iteration order being consistent. `OBJECTIVES` is a plain tuple so order is stable — this is fine. But the genome hash tiebreak means two genomes with identical metrics in the same epsilon cell are resolved by SHA-256 hash ordering, which is arbitrary but deterministic. Document this explicitly; it is not a bug but is surprising.

**`nondominated` in `evolution_engine.py` raises `RuntimeError('Pareto ranking failed')` if `nxt` is empty mid-loop.** This can happen with duplicate metric vectors (two genomes with identical fitness). The `validate_metrics` call does not deduplicate. Add: if `nxt` is empty and `seen < n`, assign remaining unranked indices to a new front rather than raising.

### LOW-COST HIGH-VALUE

**Archive is stored as a list of dicts with genome identity strings only.** When resuming, you cannot reconstruct the actual genome from the archive — only its hash. Store `asdict(genome)` in archive entries, not just `genome.identity()`. This is a 2-line change with zero runtime cost.

**`crowding` distance uses `records[i][0].identity()` as a tiebreak in `sorted`.** This is correct for determinism. No issue.

---

## (4) Data Leakage Safeguards

### MUST-FIX

**`daily_simulator.py` has no split/dividend adjustment verification.** The docstring says "diagnostic only on adjusted-for-splits data" but there is no assertion or flag that the input `bars` DataFrame is actually adjusted. A future-adjusted price series (where today's price is divided by all future splits) introduces look-ahead bias. **Add a `price_adjustment_type` parameter that must be explicitly set to `'backward_adjusted_verified'` or `'unadjusted'`; raise on anything else.**

**`entry_permitted` uses `signal_dt.tz_localize('America/New_York').replace(hour=16)`** — this hardcodes 4pm ET as the decision timestamp. Pre-market earnings releases (before 9:30am) on the signal date would be embargoed correctly, but after-hours releases on the *prior* day would not be caught if the `known_at` field in the schedule is missing. The `entry_allowed` function correctly returns `False` when `known_at` is absent and `decision_at` is provided — **this is correct fail-closed behavior**. Verify your earnings schedule data actually populates `known_at` with publication timestamps, not just announcement dates.

**`simulate()` computes `decision_at` as `dates[signal_i]` where `signal_i = i` (the current loop index).** But `pending` buys are generated at the *end* of day `i` for execution at day `i+1`. The decision timestamp should be close of day `i`, which is what the code does. This is correct. However, `signal_i` is stored as the loop index integer, not the actual date — if `dates` is reindexed or filtered, this could silently use the wrong date. **Use the actual date object, not the index.**

**Universe survivorship:** `UNIVERSE_REQUIREMENTS_v0_2.md` explicitly acknowledges survivor-only bias. The simulator has no mechanism to enforce that a stock present in `bars` on date `t` was actually listable/tradable on that date (not just that it exists in the current universe). **This is a known limitation, disclosed in the spec.** For exploratory research, acceptable — but every result must carry the disclaimer. Do not remove this limitation note from any reported output.

**Forward-label contamination in feature normalization.** `context_scoring.py` receives pre-computed `features` dict — the normalization (zscore, rank transforms) must be computed cross-sectionally using only stocks available at close-t, not the full panel. There is no enforcement of this in the scoring code. **The evaluator that computes features must enforce this; add a documented contract requirement.**

### DEFER UNTIL CERTIFICATION

PIT universe reconstruction with delisting history. The spec correctly defers this. Do not block exploratory runs on it.

---

## (5) Discovery vs Transport OOS vs Sealed Blind Separation

### MUST-FIX

**There is no code-level enforcement of the three-way split.** The spec describes it correctly but `evolution_engine.py` passes an `evaluator` function with no metadata about which date ranges it touches. A future developer could accidentally pass an evaluator that uses transport OOS dates. **Add a required `date_range` parameter to the evaluator interface: `evaluator(genome) -> (metrics, date_range_used)`. The engine should assert `date_range_used` is within the declared discovery window.**

**`daily_simulator.py` has no date-range guard.** It will simulate over whatever dates are in `bars`. Add `discovery_end_date` and `transport_start_date` parameters; raise if called with data crossing the boundary.

### LOW-COST HIGH-VALUE

**The spec notes "previously examined 2025–2026 period is not pristine."** There is no code-level flag marking these dates as contaminated. Add a `CONTAMINATED_PERIODS` constant in a config file and assert it is never used in discovery fitness evaluation.

---

## (6) Scientific Search Coverage and Runtime Engineering

### LOW-COST HIGH-VALUE

**`breed()` novelty exhaustion threshold of `population * 200` attempts is too low for large populations with tight grammar.** With population=100 and 8 possible windows × 10 features × 3 transforms × 2 directions = 480 distinct leaf types, the combinatorial space is large but the 80-attempt limit inside `tree_crossover` and `structural_mutation` means many mutations silently return the parent unchanged. **The `population * 200` outer limit is fine; the inner 80-attempt limit in operators should be raised to 200 for the `add_leaf` and `replace_leaf` actions specifically.**

**`ProcessPoolExecutor` with `chunksize` calculation `len(members)//(workers*4)` returns 0 for small populations.** `chunksize=0` raises in Python's executor. Fix: `max(1, len(members)//(workers*4))` — this is already present. No issue.

**Sobol threshold refinement mentioned in GA6 spec is absent from GA6-H.** For exploratory research, uniform random threshold sampling is fine. Defer Sobol.

**No population diversity metric is logged.** `summary` logs `unique` count but not phenotypic diversity (e.g., mean pairwise Hamming distance on leaf tuples). Without this, you cannot distinguish a converged population from a diverse one. **Add mean leaf-set Jaccard distance to summary — 5 lines, zero runtime cost.**

---

## Fastest Path: 5 Steps

**Step 1 (MUST, ~2 hours):** Replace `diagnostic_evaluator` with a minimal real evaluator: load 2 years of adjusted closes for 50–100 liquid stocks, compute 5 features (momentum-20, momentum-60, vol-20, volume-20, rs-20) as cross-sectional z-scores at each close, evaluate each chromosome by mean IC (Spearman rank correlation between score and 20-day forward return) across rolling 60-day windows. Map IC-mean → `net_ev`, IC-consistency → `reliability`, pass-rate → `opportunity_coverage`. This is ~80 lines and makes the GA scientifically meaningful.

**Step 2 (MUST, 30 minutes):** Fix EPS values to `{net_ev: 0.002, ev_per_session: 0.0002, reliability: 0.05, training_consistency: 0.05, opportunity_coverage: 0.02}`. Fix stagnation to reset population rather than terminate.

**Step 3 (MUST, 20 minutes):** Replace `context_free_genome.crossover` with `tree_crossover` as the primary operator. Add explicit `target == ()` check.

**Step 4 (LOW-COST, 1 hour):** Add `date_range` metadata to evaluator interface. Add `CONTAMINATED_PERIODS` config constant. Store full genome dict in archive entries.

**Step 5 (LOW-COST, 30 minutes):** Add Jaccard diversity metric to generation summary. Fix `nondominated` to handle duplicate fitness vectors without raising.

---

## Reject as Overengineering

- Full 503-stock PIT reconstruction before first experiment
- Sobol threshold refinement
- Lag gene implementation before basic IC evaluator works
- Stock-disjoint transport validation before discovery fitness is real
- Paired market episode analysis before any Pareto front exists

---

## Summary Table

| Issue | Classification | Effort | CPU Impact |
|---|---|---|---|
| Replace diagnostic evaluator with IC-based real evaluator | MUST-FIX | 2h | +significant (worth it) |
| Fix EPS granularity | MUST-FIX | 15min | negligible |
| Stagnation reset vs terminate | MUST-FIX | 20min | negligible |
| `tree_crossover` as primary operator | MUST-FIX | 20min | negligible |
| Date-range enforcement in evaluator interface | MUST-FIX | 1h | negligible |
| Archive stores full genome dict | LOW-COST | 10min | negligible |
| Jaccard diversity logging | LOW-COST | 20min | negligible |
| `nondominated` duplicate-fitness fix | LOW-COST | 15min | negligible |
| `ungroup` minimum-children guard | LOW-COST | 10min | negligible |
| Lag gene | DEFER | 2h | moderate |
| PIT universe reconstruction | DEFER | weeks | high |
| Sobol threshold refinement | REJECT | 1d | low |
| Stock-disjoint transport | DEFER until G6 gate | 1d | moderate |