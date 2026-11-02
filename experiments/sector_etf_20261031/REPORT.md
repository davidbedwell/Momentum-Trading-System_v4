# Executed sector ETF experiment: STOP / no replication GO

Executed on 2026-10-31 using the supplied local parquet files. H1/H2/H3, cash-only H4, discovery, validation, chronological subsplits and full-period descriptive results were calculated. No sector endpoint passes the registered validation Holm threshold; all three top3 portfolios underperform SPY at both costs. Cash-only H4 improves drawdown but fails CAGR and Calmar requirements. Hybrid cash/SGOV H4 is unavailable because no SGOV series was supplied or found in the targeted readable local search. No production GO is permitted by the protocol.

## Integrity, sample and data limits

The original preregistration and acquisition source `run.py` are unchanged. Protocol SHA256: `23a49749f06cfc44c4c7f5a203e5f18cd04343d5763e7541100c4f977a2f756f`. The frozen four-hour ceiling is 14:37:02 UTC; execution completed before it. Earlier blocked reports and acquisition evidence are preserved. No paid requests, new downloads, main MTS changes, GitHub push or publication were performed.

**Incomplete registered sample:** the nine legacy ETFs begin 2005-09-01 and SPY begins 2005-01-03. Thus discovery 2000–2016 is evaluated only where observations and lookback exist; 2000–2004 and earlier warmup cannot be manufactured. Diagnostic early discovery is especially short. Validation covers 2017–2025. All 2026 rows are excluded before strategy calculations. XLRE and XLC enter only when observed and after the required lookback. No pre-inception fills, synthetic history or substitute indexes are used.

**Adjustment evidence:** all inputs have an explicit positive finite `adj_close` distinct from raw close. Dates are increasing within ticker, ticker/date keys are unique, and there are zero missing internal SPY-calendar sessions between each ticker’s first and last observed price. No adjusted opens are supplied. Sector files contain OHLCV and adjusted close, but lack dividends/split ledgers and embedded acquisition URL/timestamp. Their vendor adjustment is accepted as the supplied cache field, not independently certified or reconciled. SPY includes dividend/split fields; maximum daily residual between adjusted growth and `(close+dividend)/previous_close` is 0.000252 (reinvestment conventions/rounding can differ). See `data_audit.json` and `adjustment_diagnostics.json` for hashes, schemas and extreme daily returns.

**Holdout process:** discovery outputs were persisted and analysis code/discovery hashes sealed in `discovery_seal.json` before the separate explicit validation command; validation verified that seal. During discovery, the signal/label builder constructed all-date diagnostic arrays in memory before restricting persisted results to discovery; validation outcomes were not printed, examined, used to select parameters or persisted until the explicit run. This is a procedural limitation relative to strict computational isolation. The historical holdout was never independently custodial or blind. No code or parameter changes followed holdout inspection.

## Source observations

| Ticker | First observed | Last in source | Rows ≤2025 |
| --- | --- | --- | --- |
| XLB | 2005-09-01 | 2026-09-14 | 5115 |
| XLE | 2005-09-01 | 2026-09-14 | 5115 |
| XLF | 2005-09-01 | 2026-09-14 | 5115 |
| XLI | 2005-09-01 | 2026-09-14 | 5115 |
| XLK | 2005-09-01 | 2026-09-14 | 5115 |
| XLP | 2005-09-01 | 2026-09-14 | 5115 |
| XLU | 2005-09-01 | 2026-09-14 | 5115 |
| XLV | 2005-09-01 | 2026-09-14 | 5115 |
| XLY | 2005-09-01 | 2026-09-14 | 5115 |
| XLC | 2018-06-19 | 2026-09-14 | 1895 |
| XLRE | 2015-10-08 | 2026-09-14 | 2573 |
| SPY | 2005-01-03 | 2026-09-15 | 5283 |


## Timing, accounting and inference

Signals use observed month-end closes, trailing 1/6/12 calendar months with the latest trading close on/before the lookback date, no skip, a minimum of nine eligible sectors and deterministic ticker tie-breaks. Monthly targets execute next session close; the first exposed return is the following close-to-close return. Daily H4 uses the same one-session delay and 200 observed sessions including signal day. Holdings drift between rebalances; self-financing transaction costs apply per dollar traded, including entry and final liquidation in every reported period. Long-short spread has 200% gross / zero net target exposure; its cost counts both legs, without borrow or financing. This diagnostic is not a deployable short strategy. Cash earns zero.

Each strategy starts only when its required signal can be executed; SPY comparators with matched start dates are included in the performance CSV. Portfolio metrics use actual calendar elapsed time from initial close, initial wealth 1, daily net returns, annualized daily volatility and annual dollars traded divided by wealth (not half turnover). Equal-weight baseline uses observed available sectors monthly without a momentum lookback. Full-period results are descriptive. Forward prediction labels run from signal close to future month-end close; these gross spreads differ from the separately delayed, costed trading portfolios. Labels crossing split/subsplit boundaries are removed.

IC and gross forward-spread inference aggregates sectors by month, uses fixed six-lag Newey–West mean SE and two-sided normal p-values, and circular 12-month moving blocks, 2,000 replications, seed 20261031, percentile 95% intervals. Holm correction covers the five IC endpoints per split. Spread and active-return p-values are descriptive. Three-month labels overlap. H4 resamples paired whole daily months in 12-month blocks, preserving within-month drawdowns; bootstrap CAGR uses 252 sessions/year whereas reported point CAGR uses calendar elapsed time. H4 sign-tail p-values use a +1 finite-replication correction and Holm across its two endpoints at each reported cost; 30bps remains sensitivity.

## Main split prediction diagnostics

### discovery

| Endpoint | Months | Mean IC | IC block 95% CI | HAC p | Holm p | Gross forward spread | Spread HAC p | Spread block 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1_1m | 129 | -0.0434 | [-0.1060, 0.0231] | 0.1958 | 0.9792 | -0.20% | 0.4734 | [-0.70%, 0.36%] |
| H1_3m | 127 | -0.0253 | [-0.1374, 0.0901] | 0.6508 | 1.0000 | -0.32% | 0.6744 | [-1.75%, 1.24%] |
| H2_1m | 123 | 0.0089 | [-0.0583, 0.0779] | 0.8097 | 1.0000 | -0.12% | 0.7291 | [-0.73%, 0.51%] |
| H2_3m | 121 | -0.0150 | [-0.1126, 0.0857] | 0.7923 | 1.0000 | -0.57% | 0.4608 | [-1.95%, 0.82%] |
| H3_1m | 134 | -0.0114 | [-0.0749, 0.0495] | 0.7195 | 1.0000 | -0.11% | 0.6598 | [-0.56%, 0.31%] |


### validation

| Endpoint | Months | Mean IC | IC block 95% CI | HAC p | Holm p | Gross forward spread | Spread HAC p | Spread block 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1_1m | 107 | 0.0051 | [-0.0662, 0.0782] | 0.8885 | 1.0000 | 0.05% | 0.8747 | [-0.58%, 0.73%] |
| H1_3m | 105 | 0.0644 | [-0.0019, 0.1355] | 0.0949 | 0.4746 | 0.61% | 0.4049 | [-0.68%, 2.11%] |
| H2_1m | 107 | 0.0267 | [-0.0373, 0.0905] | 0.4515 | 1.0000 | 0.42% | 0.1834 | [-0.18%, 1.02%] |
| H2_3m | 105 | 0.0586 | [-0.0468, 0.1575] | 0.3045 | 1.0000 | 0.55% | 0.5724 | [-1.34%, 2.47%] |
| H3_1m | 107 | -0.0206 | [-0.1010, 0.0651] | 0.6147 | 1.0000 | -0.27% | 0.3611 | [-0.84%, 0.30%] |


## Net investable portfolios and cost sensitivity

CAGR and MDD are annual growth and signed peak-to-trough loss. Each cell is `CAGR / MDD / Calmar`. Main SPY row has its available split start; matched SPY rows in CSV provide exact comparisons for shortened discovery strategies.

### discovery

| Strategy | 15bps | 30bps |
| --- | --- | --- |
| SPY | 7.44% / -55.19% / 0.135 | 7.41% / -55.19% / 0.134 |
| equal_weight | 8.29% / -53.32% / 0.155 | 8.21% / -53.37% / 0.154 |
| H1_top | 3.76% / -51.54% / 0.073 | 2.55% / -52.36% / 0.049 |
| H2_top | 5.05% / -46.83% / 0.108 | 4.10% / -47.22% / 0.087 |
| H3_top | 3.79% / -61.72% / 0.061 | 1.38% / -63.10% / 0.022 |
| H4_cash | 4.66% / -25.81% / 0.181 | 3.60% / -28.22% / 0.128 |


### validation

| Strategy | 15bps | 30bps |
| --- | --- | --- |
| SPY | 14.98% / -33.72% / 0.444 | 14.94% / -33.72% / 0.443 |
| equal_weight | 12.05% / -36.18% / 0.333 | 11.96% / -36.18% / 0.331 |
| H1_top | 9.91% / -29.06% / 0.341 | 8.67% / -30.48% / 0.284 |
| H2_top | 12.38% / -31.28% / 0.396 | 11.47% / -31.35% / 0.366 |
| H3_top | 8.05% / -46.35% / 0.174 | 5.26% / -46.46% / 0.113 |
| H4_cash | 10.03% / -25.71% / 0.390 | 9.12% / -27.91% / 0.327 |


## Delayed, net long-short spreads and active monthly inference

Spread mean and intervals below are monthly net portfolio returns, after both-leg trading costs. Top3 active means compare compounded monthly returns with SPY on exactly the same daily interval.

### discovery

| Strategy | bps | Months | Monthly mean | HAC p | Block 95% CI |
| --- | --- | --- | --- | --- | --- |
| H1 | 15 | 129 | -0.29% | 0.0548 | [-0.59%, 0.01%] |
| H1_net_spread | 15 | 129 | -0.59% | 0.0329 | [-1.12%, -0.02%] |
| H2 | 15 | 123 | -0.19% | 0.3147 | [-0.56%, 0.19%] |
| H2_net_spread | 15 | 123 | -0.41% | 0.2274 | [-1.06%, 0.22%] |
| H3 | 15 | 134 | -0.30% | 0.0196 | [-0.51%, -0.08%] |
| H3_net_spread | 15 | 134 | -0.38% | 0.0878 | [-0.79%, -0.01%] |
| H1 | 30 | 129 | -0.39% | 0.0121 | [-0.69%, -0.07%] |
| H1_net_spread | 30 | 129 | -0.79% | 0.0053 | [-1.33%, -0.20%] |
| H2 | 30 | 123 | -0.26% | 0.1676 | [-0.65%, 0.12%] |
| H2_net_spread | 30 | 123 | -0.56% | 0.1016 | [-1.22%, 0.08%] |
| H3 | 30 | 134 | -0.49% | 0.0001 | [-0.70%, -0.28%] |
| H3_net_spread | 30 | 134 | -0.78% | 0.0004 | [-1.18%, -0.41%] |


### validation

| Strategy | bps | Months | Monthly mean | HAC p | Block 95% CI |
| --- | --- | --- | --- | --- | --- |
| H1 | 15 | 108 | -0.38% | 0.1062 | [-0.83%, 0.10%] |
| H1_net_spread | 15 | 108 | -0.17% | 0.6168 | [-0.79%, 0.52%] |
| H2 | 15 | 108 | -0.20% | 0.3183 | [-0.55%, 0.27%] |
| H2_net_spread | 15 | 108 | 0.12% | 0.6902 | [-0.40%, 0.71%] |
| H3 | 15 | 108 | -0.49% | 0.0519 | [-1.03%, -0.05%] |
| H3_net_spread | 15 | 108 | -0.45% | 0.1460 | [-1.11%, 0.10%] |
| H1 | 30 | 108 | -0.48% | 0.0472 | [-0.93%, 0.02%] |
| H1_net_spread | 30 | 108 | -0.37% | 0.2833 | [-1.00%, 0.32%] |
| H2 | 30 | 108 | -0.27% | 0.1891 | [-0.61%, 0.21%] |
| H2_net_spread | 30 | 108 | -0.02% | 0.9597 | [-0.54%, 0.57%] |
| H3 | 30 | 108 | -0.70% | 0.0045 | [-1.24%, -0.27%] |
| H3_net_spread | 30 | 108 | -0.89% | 0.0037 | [-1.53%, -0.34%] |


## Cash-only H4 paired inference

Absolute MDD improvement is SPY loss magnitude minus H4 loss magnitude, in percentage points. Relative drawdown reduction is separately used for the frozen 20% threshold.

| Split | bps | Endpoint | Block 95% CI | Sign-tail p | Holm p |
| --- | --- | --- | --- | --- | --- |
| discovery | 15 | cagr_difference | [-10.62%, 6.71%] | 0.4098 | 0.8196 |
| discovery | 15 | absolute_mdd_improvement | [-15.23%, 46.93%] | 0.5137 | 0.8196 |
| discovery | 30 | cagr_difference | [-11.82%, 5.96%] | 0.3138 | 0.6277 |
| discovery | 30 | absolute_mdd_improvement | [-20.22%, 44.59%] | 0.6007 | 0.6277 |
| validation | 15 | cagr_difference | [-9.17%, -0.84%] | 0.0170 | 0.0340 |
| validation | 15 | absolute_mdd_improvement | [-6.77%, 21.02%] | 0.2679 | 0.2679 |
| validation | 30 | cagr_difference | [-10.21%, -1.66%] | 0.0050 | 0.0100 |
| validation | 30 | absolute_mdd_improvement | [-10.73%, 20.04%] | 0.4078 | 0.4078 |


## Frozen decisions

All sector hypotheses: **STOP / no replication GO**. Validation Holm p is at least 0.4746, above 0.05. H1 discovery IC is negative at both horizons; H2 discovery IC is positive only at 1m; H3 discovery and validation IC are negative. Every fixed top3 portfolio has lower validation CAGR than SPY at both costs. A positive H2 net spread alone cannot satisfy the conjunctive rule. This combines economic underperformance with imprecise predictive evidence; it does not prove every true IC is zero.

Cash-only H4: **STOP / no replication GO**. At 15bps the relative MDD reduction is 23.74%, exceeding 20%, but Calmar is lower than SPY at both costs and the paired intervals do not exclude zero in the desired direction for both endpoints. Hybrid H4: **not evaluated**, missing SGOV after its actual availability; cash is not relabeled as SGOV. Missing early discovery and limited source provenance further constrain conclusions.

## Chronological subsplits and full descriptive results

All five IC endpoints, both costs, spread portfolios, baselines, matched SPY comparators, volatility, turnover and first/last return dates are retained in CSV. The compact tables below show the 15bps investable portfolios; 30bps values and full uncertainty are in the linked machine-readable artifacts.

### discovery_early

| Strategy | First return | CAGR | MDD | Calmar | Vol | Annual turnover |
| --- | --- | --- | --- | --- | --- | --- |
| SPY | 2005-01-04 | -5.19% | -50.76% | -0.1022 | 23.32% | 0.5042 |
| H4_cash | 2005-10-19 | -0.82% | -20.40% | -0.0404 | 9.69% | 10.6043 |
| equal_weight | 2005-10-04 | -5.36% | -47.76% | -0.1122 | 23.68% | 0.9319 |
| H1_top | 2006-04-04 | -10.07% | -43.58% | -0.2311 | 22.70% | 8.1302 |
| H2_top | 2006-10-03 | -10.38% | -40.51% | -0.2561 | 25.66% | 7.2616 |
| H3_top | 2005-11-02 | -11.41% | -57.07% | -0.2000 | 30.77% | 14.5112 |


### discovery_late

| Strategy | First return | CAGR | MDD | Calmar | Vol | Annual turnover |
| --- | --- | --- | --- | --- | --- | --- |
| SPY | 2009-01-02 | 14.32% | -27.13% | 0.5277 | 17.23% | 0.2494 |
| H4_cash | 2009-01-02 | 6.94% | -22.74% | 0.3054 | 11.90% | 5.2381 |
| equal_weight | 2009-01-02 | 14.33% | -27.77% | 0.5161 | 17.19% | 0.5358 |
| H1_top | 2009-01-02 | 8.94% | -24.61% | 0.3633 | 16.67% | 7.9331 |
| H2_top | 2009-01-02 | 9.81% | -22.96% | 0.4271 | 16.59% | 5.9402 |
| H3_top | 2009-01-02 | 10.46% | -31.85% | 0.3284 | 19.35% | 16.3242 |


### validation_early

| Strategy | First return | CAGR | MDD | Calmar | Vol | Annual turnover |
| --- | --- | --- | --- | --- | --- | --- |
| SPY | 2017-01-03 | 15.79% | -33.72% | 0.4682 | 20.06% | 0.5006 |
| H4_cash | 2017-01-03 | 10.91% | -16.62% | 0.6568 | 12.77% | 5.4950 |
| equal_weight | 2017-01-03 | 11.69% | -36.18% | 0.3231 | 20.02% | 0.8228 |
| H1_top | 2017-01-03 | 10.83% | -29.06% | 0.3726 | 20.11% | 7.7701 |
| H2_top | 2017-01-03 | 10.12% | -31.28% | 0.3235 | 20.85% | 5.4567 |
| H3_top | 2017-01-03 | 6.13% | -46.35% | 0.1322 | 24.20% | 18.3508 |


### validation_late

| Strategy | First return | CAGR | MDD | Calmar | Vol | Annual turnover |
| --- | --- | --- | --- | --- | --- | --- |
| SPY | 2021-01-04 | 14.27% | -24.50% | 0.5825 | 17.12% | 0.3983 |
| H4_cash | 2021-01-04 | 9.26% | -25.71% | 0.3603 | 11.58% | 5.9825 |
| equal_weight | 2021-01-04 | 12.27% | -19.28% | 0.6363 | 14.93% | 0.7207 |
| H1_top | 2021-01-04 | 9.12% | -20.68% | 0.4411 | 17.18% | 7.8666 |
| H2_top | 2021-01-04 | 14.16% | -16.55% | 0.8555 | 16.87% | 5.8026 |
| H3_top | 2021-01-04 | 9.55% | -27.33% | 0.3496 | 18.07% | 17.1447 |


### full

| Strategy | First return | CAGR | MDD | Calmar | Vol | Annual turnover |
| --- | --- | --- | --- | --- | --- | --- |
| SPY | 2005-01-04 | 10.63% | -55.19% | 0.1926 | 19.06% | 0.0949 |
| H4_cash | 2005-10-19 | 7.04% | -25.81% | 0.2727 | 11.68% | 6.1261 |
| equal_weight | 2005-10-04 | 9.96% | -53.32% | 0.1868 | 18.46% | 0.4069 |
| H1_top | 2006-04-04 | 6.53% | -51.54% | 0.1268 | 18.46% | 7.6076 |
| H2_top | 2006-10-03 | 8.44% | -46.83% | 0.1801 | 18.86% | 5.6477 |
| H3_top | 2005-11-02 | 5.69% | -61.72% | 0.0921 | 22.23% | 16.3470 |


## Artifacts and reproduction

Run from the repository root with `/opt/mts/.venv/bin/python` (NumPy, pandas, SciPy, PyArrow):

```bash
/opt/mts/.venv/bin/python -m unittest discover -s experiments/sector_etf_20261031/tests -v
/opt/mts/.venv/bin/python experiments/sector_etf_20261031/analyze.py discovery
/opt/mts/.venv/bin/python experiments/sector_etf_20261031/analyze.py validation
/opt/mts/.venv/bin/python experiments/sector_etf_20261031/build_report.py
```

Fourteen tests pass, covering frozen integrity, admission, delayed execution, entry/exit accounting, drifting holdings, deterministic bootstrap and Holm correction. The acquisition tests use mocked failures; their printed offline output is a test fixture, not a new acquisition attempt. Tests log: `outputs/analysis_tests.log`.

All outputs: [analysis directory](outputs/analysis/). Main files: [discovery inference](outputs/analysis/discovery_inference.csv), [validation inference](outputs/analysis/validation_inference.csv), [discovery performance](outputs/analysis/discovery_performance.csv), [validation performance](outputs/analysis/validation_performance.csv), [validation active/spread inference](outputs/analysis/validation_active_inference.csv), [H4 paired intervals](outputs/analysis/validation_h4_paired.json), [data audit](outputs/analysis/data_audit.json), [discovery seal](outputs/analysis/discovery_seal.json). Individual daily return/turnover paths and monthly forward diagnostics are also saved.

Existing limitations remain: only 9–11 related ETFs; sector classification and family-selection changes; overlapping labels; one historical holdout; retrospective vendor adjustments; zero-interest cash; no tax, impact, financing or borrow model. The shortened discovery is not the full registered sample. No retuning or deployment follows this result.
