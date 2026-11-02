# DEV87 frozen RSI validation — executed and audited

Executed only the RSI control and four frozen rules. No fitting, threshold changes, search, GA or production changes. Verification PASS: original-engine monthly control reconciliation, DEV79 reconstruction and memberships/features, independent dollar accounting with bisection fees, screening predicates, matched exposure, endpoints and daily marks. Numerical errors are in verification.json.

Source contains 87 tickers, 418,594 rows, 2005-09-14 00:00:00 through 2026-09-14 00:00:00. Both requested eras are complete by observed first/last trading sessions and start separately in cash; warmup uses all available preceding observations. Coverage files disclose individual ticker histories.

Universe overlap: 0 exact ticker overlaps, 0 normalized overlaps, 0 shared supplied security IDs with the full 79-ticker DEV79 source (77 pre-2019). Symbol-level stock holdout passes: **True** (including Yahoo symbol aliases). Exact overlaps: none. See overlap lists and identity mappings. Supplied identifiers do not establish exhaustive corporate rename history; no external identity registry was available.

Frozen definitions: prior-session RSI14 lowest max(1,floor(eligible/5)), stable ties over sorted tickers; k2_2-4 = MA20 distance < 0 and acceleration21 > 0; k1_4 = acceleration21 > 0; k1_1 = return252 > 0; k2_1-2 = return252 > 0 and MA20 distance < 0. Strict finite predicates, no fill. See FROZEN_SPEC.md for exact formulas.

Adjusted open = open × adj_close/close. Monthly equal-weight rebalancing, 10 bp per side on risky trade value, exact self-financing fees, drift between rebalances, cash earns zero. Missing target opens cancel purchases without reallocating; missing held opens or marks fail. December ends at its final close, no liquidation fee or next-January return. Daily MDD includes close marks and next-open endpoints, as in the original engine. CAGR uses 252/session count; Sharpe uses monthly net mean/sample SD × sqrt(12), zero risk-free. Mean exposure is mean monthly target risky exposure. Matched controls use the full RSI basket on exactly the rule’s active months, with their own costs and drift; this matches binary capital exposure, not stock count, beta or risk.

## 2009-2018 — frozen primary validation

|Rule|CAGR|Daily MDD|Sharpe|Active months|Stock-months|Exposure|Matched CAGR|Matched MDD|Matched Sharpe|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|control|23.39%|41.96%|1.158|120/120|1819|100.00%|23.39%|41.96%|1.158|
|k2_2-4|15.87%|53.76%|0.504|99/120|368|82.50%|14.37%|37.12%|0.804|
|k1_4|11.09%|51.54%|0.523|103/120|479|85.83%|15.33%|37.12%|0.845|
|k1_1|22.80%|27.18%|1.406|115/120|1084|95.83%|23.79%|27.66%|1.371|
|k2_1-2|24.41%|25.60%|1.565|113/120|992|94.17%|25.71%|23.51%|1.530|

Annual compounded net returns (continuous portfolio path within each era):

|Year|control|k2_2-4|k1_4|k1_1|k2_1-2|
|---|---:|---:|---:|---:|---:|
|2009|51.02%|72.20%|16.33%|44.02%|37.72%|
|2010|34.17%|9.94%|-1.66%|35.86%|36.64%|
|2011|-0.93%|-10.49%|-16.97%|-0.28%|20.22%|
|2012|22.81%|33.81%|38.03%|25.87%|23.97%|
|2013|32.37%|34.76%|41.22%|29.45%|29.04%|
|2014|17.50%|4.60%|6.85%|17.04%|10.88%|
|2015|2.86%|-12.78%|-14.55%|5.69%|10.11%|
|2016|48.34%|34.24%|38.81%|51.44%|54.87%|
|2017|34.28%|5.41%|9.63%|32.56%|32.31%|
|2018|3.83%|10.29%|11.08%|-1.56%|-2.20%|

Canceled selected/matched target entries: 0; sessions: 2516.

## 2019-2025 — separate later-period transfer

|Rule|CAGR|Daily MDD|Sharpe|Active months|Stock-months|Exposure|Matched CAGR|Matched MDD|Matched Sharpe|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|control|19.27%|43.16%|0.830|84/84|1390|100.00%|19.27%|43.16%|0.830|
|k2_2-4|18.98%|49.76%|0.680|65/84|297|77.38%|13.57%|39.12%|0.821|
|k1_4|25.01%|51.09%|0.800|68/84|391|80.95%|13.06%|42.21%|0.776|
|k1_1|12.83%|41.68%|0.671|82/84|675|97.62%|15.92%|43.16%|0.788|
|k2_1-2|13.46%|41.68%|0.714|82/84|596|97.62%|15.92%|43.16%|0.788|

Annual compounded net returns (continuous portfolio path within each era):

|Year|control|k2_2-4|k1_4|k1_1|k2_1-2|
|---|---:|---:|---:|---:|---:|
|2019|47.53%|25.52%|27.33%|28.61%|25.21%|
|2020|32.10%|52.63%|98.97%|-13.61%|-15.29%|
|2021|37.39%|25.76%|25.76%|22.19%|22.52%|
|2022|-34.92%|-41.62%|-43.87%|-20.97%|-16.67%|
|2023|50.42%|140.06%|134.78%|36.30%|45.95%|
|2024|16.13%|-1.51%|3.68%|27.25%|26.09%|
|2025|12.46%|1.20%|9.25%|24.86%|21.25%|

Canceled selected/matched target entries: 0; sessions: 1760.

Primary-period interpretation: k2_1-2 improves CAGR and drawdown versus the always-invested RSI baseline, but trails its matched control in CAGR (24.41% versus 25.71%). The acceleration rules do not improve baseline CAGR or daily drawdown. In the separate later period, k1_4 has the highest frozen-rule CAGR (25.01%) but daily MDD is 51.09%; no rule is retuned or chosen prospectively from these results.

The separate verify.py audits persisted files: source hashes, fees, annual compounding, all portfolio metrics, endpoint labels/NAV, and requested memberships. Its output is artifact_verification.json; run it after study.py.

Full selected and matched metrics are in metrics.csv; annual.csv includes both portfolios, active months, stock-months and exposure. Each period directory contains candidate features/flags, requested/executed selections, eligibility, all monthly fees/turnover/net/gross returns and labeled daily NAV. verification.json records source/code/spec SHA256 and numerical reconciliation errors. Reproduce with `/opt/mts/.venv/bin/python experiments/dev87_rsi_frozen_validation_20261101/study.py`.

Fixed historical universes retain survivorship/availability bias and uncertain delisting coverage; vendor adjusted prices are not independently point-in-time certified. Frozen rules were selected from DEV79 exploratory results; overlap and prior research prevent treating a contaminated universe as independent confirmation. Later-period results are reported separately without retuning and are not a claim of untouched blind data. Daily MDD follows the original sampled marks, not an intraday high/low loss measure.
