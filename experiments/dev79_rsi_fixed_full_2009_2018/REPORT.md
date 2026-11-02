# Fixed RSI full retrospective: endpoint blocked

Frozen rule uniquely established from the saved 2009–2013 discovery ranking: `stabilization_09`, RSI lowest20% basket AND `ma_distance_20 < 0` AND `acceleration_21 > 0`. Original discovery cutoff 2014-01-01; last discovery entry 2013-11-01 and exit 2013-12-02. No new ranking, calibration, warmup phase, fallback or optimization. Existing pre-entry features used unchanged.

Applied unchanged to all 120 entry months, January 2009–December 2018. 2009–2013 is **in-sample retrospective**; 2014–2018 is **previously examined OOS**, with **no new validation claim**.

Full-period net CAGR, monthly MDD and Sharpe are **unavailable**. Original next-month-first-session adjusted-open accounting requires January 2019 data to value December 2018. Those data are prohibited. Neither a zero return, omitted month, nor a December liquidation is substituted. Final liquidation and December NAV cannot be reconciled. All 120 monthly decisions are exported; 119 returns are observed. The supplied history carries fixed-universe/survivorship and vendor price-adjustment limitations.

|Strategy|Years / months|Active months|Selected stock-months|Net CAGR|Monthly MDD|Sharpe|
|---|---:|---:|---:|---:|---:|---:|
|frozen_all|10 / 120|92|321|unavailable|unavailable|unavailable|
|baseline_rsi_lowest20pct|10 / 120|120|1651|unavailable|unavailable|unavailable|

Costs and observed accounting match the prior study: 10bps per buy/sell notional, equal monthly weights, drift-adjusted turnover, zero-return cash for empty selections. Initial purchase charged. Monthly net = (1-cost) × (1+gross) − 1. No terminal fee fabricated. Sharpe convention: monthly mean/sample SD × sqrt(12), zero risk-free rate; CAGR annualizes at 12/months and MDD includes initial NAV. Annual observed segments continue the same portfolio without annual restarts; 2018 metrics are unavailable.

Artifacts: `selected_stocks.csv`, `candidate_membership.csv`, `monthly_return_reconciliation.csv` (120 rows per strategy, stock lists, NAV, fees and missing terminal return), `stock_return_reconciliation.csv` (drift/target weights, trades, fees and return contributions), `annual_metrics.csv`, `full_period_metrics.csv`, `audit.json`. Independent dollar-accounting replay, exact stored rule flags and prior frozen_all memberships all PASS. No production files, GA, raw data or 2019+ observations used. Reproduce with `bash experiments/dev79_rsi_fixed_full_2009_2018/run.sh` (900-second timeout).
