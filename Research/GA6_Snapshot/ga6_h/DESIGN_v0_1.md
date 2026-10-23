GA6-H DESIGN v0.1 — 2026-10-22

MISSION: Independently evolve predictive rankings of stocks likely to outperform over the next 1–40 trading sessions. No GA6 regime niches. Chromosomes encode feature transformations, interactions, ranking aggregation, missing-value handling, and prediction horizon.

CAUSALITY: Point-in-time eligible universe including delisted stocks, historical membership, split-adjusted and executable pricing. Signals available at close t, trades no earlier than next open. Earnings/filings require actual publication timestamps. No hindsight winner screening. Freeze chronology, purge overlapping forward labels, prohibit future-aware normalization.

FEATURE FAMILIES: Momentum/acceleration, relative strength, volume/liquidity, volatility compression/expansion, trend geometry, sector leadership, breadth, PIT earnings/revisions. Evolve nonlinear combinations without niche taxonomy.

DISCOVERY FITNESS: Multiobjective top-k excess forward returns net of costs, rank correlation, stability, downside tail, confidence/sample support and turnover. Pareto retain diversity. Portfolio CAGR/MDD belong to separate portfolio evaluation, not sole genetic objective.

PORTFOLIO: Independently simulate daily top-k stock rankings with 40-session maximum hold, realistic fills, cash constraints, 10bps comparable costs, 3% typical position size and up to 10% within frozen risk limits. Benchmarks: momentum, sector-relative-strength, random eligible stocks, SPY and cash proxy. No compulsory GA6 niche strategy overlay.

VALIDATION: Rolling chronological walk-forward with purging/embargo; additional stock-disjoint transport, market episode tests, uncertainty and multiple-testing audit. Respect existing GA6 blind partitions; previously examined 2025–2026 period is not pristine. Report hit rate, excess returns, CAGR, MDD, turnover, sector exposure, capacity and confidence intervals.

ENGINEERING PHASES:
1. Audit historical data coverage and PIT/delisting/earnings integrity.
2. Build immutable timestamped features and 1–40-session labels with leakage tests.
3. Implement baseline rankers and standalone stock portfolio evaluator.
4. Implement GA6-H evolutionary search with checkpoint/restart and reproducibility hashes.
5. Validate rolling walk-forward and stock-disjoint transport.
6. Matched portfolio comparison: GA6 niche, GA6-H independent, opportunity auction, adaptive allocator.
7. Certify out-of-sample and paper trade only after gates pass.

OPERATIONS: Keep GA6 optimizer running unchanged. Isolate code and output under /opt/mts/ga6_h/. Do not oversubscribe CPU with a concurrent full-scale run. Capture data hashes, seeds, splits and code hashes. The existing 503-member September 2026 snapshot is not by itself historical PIT membership.
