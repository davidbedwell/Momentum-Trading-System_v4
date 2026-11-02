# DEV87 frozen RSI validation — BLOCKED, not executed

The requested source cannot be read under this session's filesystem permissions:
`/opt/mts/thunder-migration/mts-certification-20261011/dev87/dev87_raw.parquet`.

An actual pandas parquet read using `/opt/mts/.venv/bin/python` failed with `PermissionError: [Errno 13] Permission denied`. The session does not permit access escalation. No performance results, ticker overlap findings, control reconciliation, or verification PASS are claimed. Independent stock holdout status remains **unverified**. The stated 87 tickers and 2019–2025 coverage could not be confirmed.

## Frozen specification inspected

Reference: `experiments/dev79_rsi_indicator_combinations_20261101/study.py`, its REPORT.md, the source `dev79_monthly_indicator_20261101/indicator_experiment.py`, and `dev79_rsi_winner_characteristics_20261101/study.py`.

Only these prespecified rules are authorized, always alongside the monthly RSI14 lowest-20% control:

- k2_2-4: ma_distance_20 < 0 AND acceleration_21 > 0.
- k1_4: acceleration_21 > 0.
- k1_1: return_252 > 0.
- Optional included specification k2_1-2: return_252 > 0 AND ma_distance_20 < 0.

RSI is 100−100/(1+gain/loss), gain/loss EWM alpha=1/14, adjust=False, min_periods=14. Prior global session positive finite adjusted close and finite RSI determine eligibility; select max(1, floor(eligible/5)) using stable descending negative-RSI order over sorted ticker columns. Features use prior-session adjusted closes, no fill: return_252=C/C.shift(252)−1; ma_distance_20=C/rolling(20).mean()−1; acceleration_21=(C/C.shift(21)−1)−(C.shift(21)/C.shift(42)−1). Nonfinite features fail strict predicates. No threshold fitting or optimization.

Adjusted open is open × adj_close/close. Equal-weight selected names rebalance at first observed session open monthly. Exact self-financing commission is 0.001 times absolute risky-asset trade value per side, solved against post-fee equity; holdings drift between rebalances. Cash earns zero; sales into cash incur costs. Preserve original missing-opening execution policy and fail for missing held marks. The DEV79 combination implementation asserts all selected opens available, whereas the original baseline cancels unavailable purchases; any such discrepancy must be disclosed and reconciled rather than silently changing screening.

Run January 2009–December 2018 separately from January 2019–December 2025 if available. Each era starts in cash, uses available historical warmup, and ends at its final December close without liquidation fee. Specifically, December 2018 must not use a January 2019 exit. Partial forward coverage must be disclosed.

Full-period CAGR uses 252/session count; daily MDD includes close marks and opening endpoints; Sharpe is mean monthly net return / sample standard deviation × sqrt(12), zero risk-free rate. Report annual compounded net returns, stock-month counts, active months and mean exposure. Each rule's matched control holds the RSI control basket on exactly its active months, cash otherwise, with its own costs and drift; this matches binary exposure, not risk or stock count.

## Required unfinished verification

Read the actual DEV79 development source (`/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet`) and compare its complete ticker set with DEV87, including normalized symbols and any available identity/rename evidence. Report every overlap as contamination; do not describe a contaminated universe as independent. Reconstruct DEV79 baseline memberships/features and reconcile the known original monthly series and 23.1936803841% CAGR before transferring the method. Independently replay DEV87 dollar accounting and screening, reconcile its control to the frozen original engine, check all memberships, fees, exposure, endpoints, annual aggregation and daily drawdowns. Export selections, candidate features/flags, monthly and annual returns, daily NAV with date/mark labels, metrics, coverage, source hashes, overlap lists and verification errors.

No GA or production changes were made. The validation needs the DEV87 file made readable in this session, or copied by an authorized actor into the workspace. No source access restrictions were bypassed.
