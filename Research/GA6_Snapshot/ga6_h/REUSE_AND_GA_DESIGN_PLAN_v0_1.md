# GA6 → GA6-H Reuse Audit and Engineering Plan v0.1

## Isolation
GA6-H is an independent stock-ranking research project. GA6 code, active run, checkpoints, cache, portfolios, and data remain unchanged. The nine governance/reference files in reuse_snapshot/ are hash-verified copies, not approved runtime dependencies. No imports from GA6 until standalone adaptation and unit/integration tests pass.

## Reuse candidates — adapt and validate
- Reproducibility: code/data fingerprints, deterministic RNG, atomic checkpoints, resumability, immutable trial manifests, caching keyed by feature universe/splits/cost assumptions, process pool concurrency, profiling, generation reporting.
- Scientific controls: chronology, purging/embargo, one-use validation access, trial-family multiplicity accounting, statistical pre-registration, confidence intervals, drawdown and episode diagnostics, Pareto diversity, baseline comparison.
- Market execution: next-session-open order scheduling, fees/slippage, settlement, split/dividend handling, position limits, 40-session exits, cash accounting and portfolio NAV. Review underlying GA5 and GA6 dependencies before porting; test using raw yfinance OHLCV and corporate actions; do not assume existing precomputed GA6 features are compatible.
- Risk overlays: A/B/B1/C/R-1 prospective state tapes, with lagged effective dates, as a separate optional portfolio experiment. Do not train ranking labels using hindsight defense.

## Must NOT transfer as-is
- GA6 niche taxonomy, niche membership, chromosomes, signal tree interpretation, fitness ranking, stock partition, hardcoded 503-symbol universe, GA5 feature tables, historical PIT membership claims, old data normalization, current GA6 result caches and checkpoints.
- GA6 specific scoring may be incompatible with GA6-H's cross-sectional objective. EV must explicitly state denominator: trade notional versus portfolio equity; include sample counts and uncertainty.

## GA6-H new work
1. Audit the 4,967 downloaded parquet histories for missing dates, corporate actions, stale tickers, minimum lookback, adjusted vs raw OHLC consistency, duplicates and exchange classification. Freeze universe snapshot and hash.
2. Build date-indexed, causal stock features from past-only prices/volume. Do not leak future prices via current survivorship screening or global normalizations. Current-listed survivor universe bias remains explicitly disclosed.
3. Create forward labels for each horizon 1–40 trading sessions, with executable next-open entry and declared exit convention, costs and delisting limitations. Purge overlapping labels and use chronological folds.
4. Implement independent baseline rankers, top-K simulator and GA6-H genome schema. Genome can evolve feature families, transformations, weights/interactions, normalization window, horizon, rank aggregation, and selection thresholds. No GA6 niche selection genes.
5. Pre-register objective hierarchy: rank predictive lift and top-K net excess forward return with uncertainty/support; Pareto penalize tail loss, turnover, instability, concentration and capacity. Independently report portfolio CAGR/MDD, cash use and exposure. Do not select final model based on its holdout performance.
6. Run small reproducible smoke tests, then full evolution only after CPU/memory benchmark and GA6 contention plan. GA6 is presently running 8 workers.
7. Compare standalone GA6-H, GA6, and their optional allocator only after each standalone evaluation is validated. Risk overlay with/without A/B/B1/C/R-1 on identical stock predictions.

## Validation and limits
Train/test in chronological order. Separate discovery, development feedback, locked validation and prospective final holdout. Previously observed dates cannot be represented as untouched. No paid PIT data: historical results are conditional on 2026 surviving tickers; cannot certify unbiased historical live-tradable universe performance. Forward paper-trading can collect new unbiased evidence.

## Engineering gates before evolutionary design is frozen
Data quality report; feature/label leakage tests; reference portfolio reconciliation; baseline metrics; measured evaluation latency and worker scaling; parameterized risk/cost model; trial ledger audit; test suite pass. Only then lock chromosome grammar, crossover/mutation, selection, population, generations, fitness and stopping rules.

## Mandatory quarterly disclosure embargo (2026-10-22 user decision)
- Block all NEW entries and position increases in a stock for the two trading sessions before, the disclosure session, and two trading sessions after its corporate quarterly financial-results disclosure (five sessions if announced on a trading session).
- For before-open or after-close disclosures, map the event to its first relevant trading session using actual announcement timestamp and exchange calendar. Preserve actual timestamps and distinguish known scheduled date from retrospectively recorded actual date.
- Mandatory/protective exits remain allowed, including during the embargo; do not force a sale solely due to a disclosure unless a separately specified policy requires it.
- Apply this stock-by-stock in both GA discovery portfolio simulations and validation; block at order-placement and fill time, not just at signal generation.
- Prevent future leakage: only embargo ahead of the event if the announced schedule was publicly known by the decision time. Missing PIT schedule evidence must be explicitly flagged; never silently treat today's earnings calendar as historically known.
- Unit tests: before-open and after-close events, weekends/holidays, reschedules, missing announcements, entry versus exit, and next-open execution.
- The exact convention for events announced outside market sessions must be frozen before backtesting and applied consistently.

## First data audit completed
- Audit outputs: /opt/mts/ga6_h/audits/price_audit_summary.json and price_coverage.parquet.
- 4,967 histories; 9,954,459 OHLCV rows; zero missing files, duplicate dates or unsorted files. 50 files with OHLC violations, 34 with invalid prices, 280 shorter than 252 sessions. Quarantine invalid rows in derived layers; preserve raw Parquet.
- Existing EODHD earnings archive: /opt/mts/thunder-migration/Downloads/EODHD_US_EARNINGS_ARCHIVE_2006_2026/us_common_stock_earnings_2006_2026.jsonl.gz. Observed fields include report_date, date, actual, before_after_market, code, but NO first-publication known_at timestamp. This can support retrospective disclosure exclusions, NOT causally proven pre-event schedule knowledge. Do not present embargo backtests using this archive as PIT certified. A timestamped announcement schedule source or conservative explicit caveat is required.
- GA6-H earnings embargo module and 5 passing unit tests: quarterly_embargo.py and test_quarterly_embargo.py. Integration with evaluator remains pending.
