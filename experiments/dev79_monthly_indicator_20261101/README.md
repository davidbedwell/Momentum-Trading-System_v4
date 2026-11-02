# DEV79 monthly indicator reconstruction — completed offline

**No indicator passed discovery; blind was not evaluated.** Discovery covers 2009-01-02 through 2018-12-31 (120 monthly observations). The source extends through 2026-09-14, but there are deliberately no blind returns or blind portfolio artifacts. Production was not modified. No downloads, optimization, GA or monitoring were used.

## Fidelity boundary and fixed choices

The user referred to `indicator_experiment.py`, but no original script or attachment was present in the accessible workspace or `/tmp`. The only supplied specification was the indicator names and the prompt's constraints. This file is therefore an explicit **reconstruction**, not a verified execution or verbatim reproduction of the original code. Original formulas, quintile rounding, RSI initialization, finalist ordering and significance reference cannot be certified. No claim of exact preregistration replication is made. The conventions below were chosen before evaluating discovery and were not tuned to the results. The stated gate `t >= 2, p <= .05, excess > 0` was retained unchanged; none of the ten passes, so the choice of finalist ordering cannot open blind here.

All features use historical close prices and their available pre-2009 observations (source begins 2004-09-01). Higher scores rank first. Trading-session conventions: one month = 21 sessions, one year = 252. Ratios subtract one where shown; constant shifts do not affect rankings.

| Indicator | Reconstruction formula |
|---|---|
| mom_126d | C / C.shift(126) - 1 |
| mom_12m_skip1m | C.shift(21) / C.shift(252) - 1 |
| price_over_sma200 | C / SMA200 - 1 |
| sma50_over_sma200 | SMA50 / SMA200 - 1 |
| ema20_over_ema100 | EMA20 / EMA100 - 1; adjust=False, min periods 20/100 |
| near_52w_high | C / rolling252.max(C) - 1 |
| donchian_100d | C / rolling100.max(C) - 1; close-based because OHLC highs/lows were not specified |
| low_vol_60d | negative sample standard deviation of 60 one-session percentage returns |
| reversal_1m | -(C / C.shift(21) - 1) |
| rsi14_oversold | negative Wilder-style RSI; EWM alpha=1/14, adjust=False, min_periods=14 |

RSI uses pandas EWM initialization, not an initial 14-session simple average. No binary RSI threshold is imposed. Donchian could instead mean a channel location or breakout against a lagged channel in the absent script; this is a material fidelity limitation. Windows include the signal close. No forward filling is used for features. Indicators have their own finite-signal pools rather than a common intersection.

## Execution, eligibility and benchmark

At the last available close before the first trading session of each month, require a positive finite close and a finite score. Select `max(1, floor(N/5))` of the N eligible names; zero eligible names hold cash. Ties resolve alphabetically by ticker (stable sort over sorted pivot columns). Equal target weights, long-only, fully invested when fills permit. The first January 2009 signal uses December 31, 2008. Execute at the next actual session open. Monthly holdings drift between rebalances; returns run open to next rebalance open. December 2018 terminates at December 31 close, so discovery never uses a 2019 opening price. A hypothetical gated blind replay would reset to cash at the first 2019 open using the prior close, continue through available data end and mark the final partial month to close. No terminal liquidation is charged.

Use 10 bps on every bought or sold notional, including initial entry. Solve self-financing proportional commission with post-fee target weights: fee = .001 * sum(abs(target*(1-fee) - drifted_previous_weights)). Report **two-sided traded notional / pretrade NAV**, so a full replacement is approximately 2, initial entry approximately 1. Sum of monthly cost fractions is not the cumulative wealth drag in percentage points. Unchanged weights have zero cost only if they have not drifted. Missing entry opens cancel those target allocations into cash; a missing held open/mark raises an explicit error rather than inventing a fill or return. No such canceled target or held-mark error occurred. Fractional holdings, immediate sale funding, no settlement restrictions, taxes, cash yield, borrowing or additional slippage. This differs materially from the daily manager.

Benchmark: monthly equal weight over **exactly the same eligible indicator-specific DEV79 pool**, with the same execution and 10 bps costs. There is no SPY in the archive and none was synthesized. Each indicator has 500 independent monthly random top-quintile portfolio paths; NumPy default_rng seed 1 is reset per indicator/basis. Random selection samples without replacement from that month's same eligible pool and same k, with drift and actual transaction costs. The same seed/pool produces common random paths across indicators. The 500 rows are paths, not 500 independent market histories.

## Price basis and provenance

Primary: `C = adj_close`, `O = open * (adj_close / close)`. All entry, exit and daily marks are on that consistent adjusted basis. This avoids the erroneous raw-open versus adjusted-close return mismatch. **Adjusted close may reflect future dividends/restatements; the factor is not certified point-in-time.** Ratios cancel constant scaling but do not remove changing dividend adjustments. This is a dividend-adjusted return proxy, not an independently validated cash-dividend ledger; dividends are not credited a second time.

Sensitivity: `C = close`, `O = open`, no cash dividends. The archived raw-named OHLC are already split-consistent: our source continuity audit finds 36/36 major splits (including reverse splits) favor already-adjusted continuity. No second split multiplier is applied. This heuristic is not vendor certification. Both bases retain historical restatement and retrospective survivor-universe bias; DEV79 is not a historical index roster. No PIT universe membership or vendor-as-of certification is available.

Source: `/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet`. SHA256 `7eb869d0059dd976705c9673c5098d611b38c4970645168a28882fe15c055e0a`. 394,795 rows, 79 tickers. Python 3.12.3, pandas 3.0.6, NumPy 2.5.4. Final experiment runtime 5.71 seconds with CPU affinity [0]; single-thread library settings.

## Discovery results

Annualized excess is 12 × mean paired monthly strategy-minus-benchmark return; it is not a CAGR difference. The gate uses the two-sided one-sample Student t-test on these paired monthly excess observations. This test/reference is a reconstruction assumption because the original code was unavailable. The single finalist is highest positive-direction t. The blind gate is not changed for the random empirical p-value or multiplicity diagnostic.

| Basis | Indicator | CAGR | Benchmark CAGR | Ann. excess | t | p | Daily-mark max DD | Mean turnover |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| adjusted | mom_126d | 18.22% | 19.59% | -1.19% | -0.428 | 0.6692 | 21.80% | 0.684 |
| adjusted | mom_12m_skip1m | 17.62% | 19.14% | -1.15% | -0.361 | 0.7187 | 25.78% | 0.532 |
| adjusted | price_over_sma200 | 16.86% | 19.29% | -2.18% | -0.689 | 0.4924 | 20.40% | 0.667 |
| adjusted | sma50_over_sma200 | 19.04% | 19.29% | -0.26% | -0.086 | 0.9317 | 21.21% | 0.468 |
| adjusted | ema20_over_ema100 | 19.67% | 19.55% | 0.02% | 0.006 | 0.9949 | 21.17% | 0.763 |
| adjusted | near_52w_high | 12.16% | 19.13% | -6.45% | -2.079 | 0.0398 | 17.97% | 1.115 |
| adjusted | donchian_100d | 10.52% | 19.55% | -8.28% | -3.058 | 0.0028 | 17.67% | 1.285 |
| adjusted | low_vol_60d | 12.37% | 19.69% | -6.96% | -2.098 | 0.0380 | 23.24% | 0.478 |
| adjusted | reversal_1m | 19.11% | 19.71% | 0.08% | 0.031 | 0.9755 | 35.97% | 1.610 |
| adjusted | rsi14_oversold | 23.19% | 19.70% | 3.56% | 1.380 | 0.1703 | 29.74% | 1.468 |
| price_only | mom_126d | 15.64% | 16.85% | -1.08% | -0.374 | 0.7090 | 23.20% | 0.679 |
| price_only | mom_12m_skip1m | 15.34% | 16.40% | -0.77% | -0.242 | 0.8094 | 26.08% | 0.539 |
| price_only | price_over_sma200 | 15.06% | 16.55% | -1.34% | -0.437 | 0.6627 | 22.32% | 0.653 |
| price_only | sma50_over_sma200 | 17.48% | 16.55% | 0.80% | 0.263 | 0.7928 | 21.24% | 0.466 |
| price_only | ema20_over_ema100 | 18.20% | 16.82% | 1.16% | 0.443 | 0.6583 | 22.83% | 0.749 |
| price_only | near_52w_high | 9.51% | 16.39% | -6.48% | -2.098 | 0.0380 | 19.34% | 1.067 |
| price_only | donchian_100d | 7.44% | 16.82% | -8.73% | -3.247 | 0.0015 | 20.78% | 1.281 |
| price_only | low_vol_60d | 8.28% | 16.96% | -8.36% | -2.499 | 0.0138 | 22.51% | 0.496 |
| price_only | reversal_1m | 16.29% | 16.97% | 0.02% | 0.008 | 0.9936 | 37.34% | 1.616 |
| price_only | rsi14_oversold | 20.87% | 16.97% | 3.92% | 1.496 | 0.1373 | 30.70% | 1.473 |

RSI is the finalist on both bases. Adjusted RSI random-path CAGR mean is 17.21%, 5–95% range 13.60–20.91%, empirical upper-tail p = 0.00798. Price-only RSI random p = 0.00399. These apparently favorable random-path ranks do **not** satisfy or override the required benchmark-relative t/p gate. All blind status is `NOT_EVALUATED_GATE_FAILED`; absence of blind returns is intentional, not missing work.

Maximum DD uses observed daily closes and intervening rebalance opens, including initial capital and costs. It is not an intraday-high/low drawdown. Monthly-only DD is also recorded. CAGR uses 252 sessions/year; monthly Sharpe uses zero risk-free rate and sqrt(12), sample standard deviation. The shortened terminal month still contributes one monthly t-test observation.

## Code audit and statistical limitations

Since the original code was absent, these are audited failure modes and explicit reconstruction choices, not claims that particular lines of the original script were inspected:

* **NaN selection:** ranking an array before restricting eligibility can select NaNs, and computing k from all columns can inflate the portfolio. We first restrict to finite scores and prior closes, then compute k. Missing scores never enter selected or random portfolios; empty pools remain cash. `eligibility_summary.csv` quantifies monthly exclusions and eligible/selected counts for every indicator and basis. A return being known in hindsight is not used to define eligibility. Finite indicators can still differ in warmup behavior.
* **Random baseline:** sampling from every DEV79 name, including not-yet-listed names or missing-feature stocks, creates an unmatched baseline. All 500 paths use exactly the eligible pool, k, drift accounting and costs. Empirical p = (1 + number random CAGR >= strategy CAGR)/501; it is a conditional randomization comparison, not the preregistered significance test. It does not establish OOS alpha or remove survivor bias.
* **Monthly turnover costs:** a flat 20 bps charge every month misprices unchanged positions; charging just 10 bps on a full replacement misses the sale leg. The engine charges both sides of actual drift-adjusted notional. New entries pay costs; the final unliquidated mark does not. The eligible benchmark is charged on the same basis. Unit tests include entry, unchanged holdings, drift and complete replacement.
* **Multiplicity:** the unadjusted gate is retained, not silently replaced with a corrected gate. Highest-t selection among ten indicators creates selection bias; correlated indicators do not eliminate it. `p_bonferroni_10` and gate Bonferroni p are diagnostic only (RSI = 1.0 on both bases). Considering two bases creates an additional research choice; sensitivity is not an independent confirmation. Negative-t small p results are underperformance and fail the positive gate. IID t-test assumptions may fail under serial dependence, nonnormality and changing universes. No HAC/blocked bootstrap or formal family-level validation is claimed.

## Daily manager context only

The existing daily manager's saved discovery-period NAV (same 2009–2018 dates, price-only) has CAGR -0.88%, total return -8.47%, and daily max DD 22.74%. The monthly price-only RSI reconstruction has CAGR 20.87% and max DD 30.70%. This is **context, not causal evidence that monthly trading beats daily trading**: stock selection, exposure, sizing, risk controls, initial execution, settled-cash constraints and rebalance rules all differ. The manager's full-history context in its existing comparison.csv is CAGR -0.23%, max DD 23.86%; that broader period is not matched to monthly discovery. We did not run monthly blind to align those periods. `daily_manager_context.json` records the exact source hash and matched-period calculation; the manager was not rerun or modified.

## Reproduction and saved files

From repository root: `bash experiments/dev79_monthly_indicator_20261101/run.sh`. Uses installed `/opt/mts/.venv`; no package installation or network. The run is pinned to CPU 0 and each command has a 900-second hard limit. Original request's 15-minute budget was respected.

* `indicator_experiment.py`: runnable reconstructed experiment and conditional blind code.
* `test_experiment.py`, `tests.log`: seven passing tests for finite eligibility, matching random pool/seed, empty cash pool, drift/cost accounting, future/prefix invariance, prior-close/next-open execution, adjusted open consistency, and gate boundaries.
* `validate_results.py`, `validation.log`: independent saved-artifact reconciliation of all 20 discovery portfolios, all 10,000 random paths, execution boundaries, costs, weights, terminal NAV and daily drawdown; confirms zero blind artifacts.
* `metrics.csv`, `gates.json`: all per-indicator discovery metrics and explicit blind gate decisions. No blind metric rows exist because both gates failed.
* `adjusted/discovery/<indicator>/` and `price_only/discovery/<indicator>/`: `monthly.csv` (signals, executions, eligibility, returns, turnover, costs), `holdings.csv` (weights, scores), `daily_marks.csv` (strategy/benchmark NAV), `random_trials.csv` (500 paths' CAGR, return, turnover).
* `coverage.csv`, `eligibility_summary.csv`, `split_continuity.csv`, `split_audit.json`, `provenance.json`, `run.log`, `daily_manager_context.json`: input, corporate-action, runtime and context audit.
* `checksums.json`: artifact SHA256 manifest, excluding itself and Python bytecode.
