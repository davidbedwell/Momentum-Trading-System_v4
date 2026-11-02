# RSI multi-feature setup study, 2009–2018

Executed and verified 64 prespecified 2–4-condition rules. Discovery uses 2009–2013; 59 common walk-forward entry months run from 2014-01-02 through 2018-11-01, with final exit 2018-12-03. No production code changes, GA, 2019+ data, external fetches, or fitted OOS thresholds. Runtime 31.0 seconds, one numerical thread.

## Main OOS results

|Strategy|Winner hits / selected|Recall|Enrichment|CAGR net|MDD monthly|Sharpe|Positive precision months / active|
|---|---:|---:|---:|---:|---:|---:|---:|
|baseline_rsi_basket|236/862 (27.38%)|100.00%|1.00|15.08%|-17.71%|1.11|0/59|
|expanding_all|25/72 (34.72%)|10.59%|1.27|18.74%|-10.73%|1.02|15/28|
|expanding_trend_pullback|22/65 (33.85%)|9.32%|1.24|15.52%|-15.68%|1.06|18/33|
|expanding_stabilization|32/112 (28.57%)|13.56%|1.04|12.76%|-20.39%|0.70|16/34|
|expanding_volume_normalization|16/42 (38.10%)|6.78%|1.39|-1.13%|-19.81%|-0.06|13/27|
|expanding_relative_strength|14/52 (26.92%)|5.93%|0.98|18.53%|-15.42%|0.84|10/28|
|frozen_all|41/163 (25.15%)|17.37%|0.92|19.06%|-14.39%|0.91|21/48|

These are winner precision and recall, not winner feature prevalence. The baseline winner rate is above 25% because each month labels exactly ceil(observed basket size/4) winners. Read all families, including weak or negative results; no family is promoted by OOS rank. Expanding-all is the primary prespecified selection policy. Fixed-all provides a completely frozen 2013 comparator.

The overall expanding policy improves pooled winner precision and net CAGR here, but selects only 72 stock-months and is active in 28/59 months. It captures only 25/236 winners, and its Sharpe is below the basket. Volume normalization has the highest family precision yet loses money after costs; relative strength has below-baseline precision despite positive returns. The frozen overall rule also has below-baseline precision. This is mixed evidence, not a validated repeatable winner detector.

## Design and timing

See PLAN.md for the design saved before setup evaluation, rule_definitions.csv for all 64 exact conjunctions, and condition_definitions.csv for inputs. Four economic families cover positive long trend with pullback, falling selling momentum/stabilization, elevated prior volume followed by normalization, and improving relative strength while price is depressed. Each rule combines 2–4 named raw or derived feature predicates. Volatility contraction uses derived vol_10/vol_21; derived features may use multiple raw inputs. Recent reversal compares unequal horizons and is a stabilization proxy. Volume ratios identify an elevated prior 15-session mean, not a dated one-day spike; vendor volume can be split-sensitive. RS improvement reconstructs prior 42-session relative performance from 63/21-session stock and benchmark returns, then compares simple per-session averages; this is a horizon-normalized proxy, not regression slope.

All features are taken from the immediately preceding global trading session without forward fill. Monthly labels rank next-month adjusted open-to-open returns descending, ticker ascending for ties. Monthly basket membership is copied verbatim from the source lowest-20%-RSI14 holdings; 12–15 stocks from the same supplied fixed 77-ticker universe. Cross-sectional outcomes never enter selection. No benchmark/universe changes between variants. The primary common benchmark is the entire RSI basket; relative-strength features retain the source equal-weight daily available-return universe benchmark.

Within each evaluation year the rule is fixed; annual expanding calibration uses all earlier labeled months whose exit is strictly earlier than January entry. December just before each evaluation year is embargoed, including December 2013, so initial calibration ends November 2013. Eligible rules require >=40 labeled selections and >=24 active training months. Rank by mean monthly selected winner precision minus monthly basket winner rate, tie-break pooled enrichment then rule ID. Family policies apply that identical procedure within each family. A negative best score is not suppressed. No 2014–2018 tuning or OOS-ranked choice is used. selection_schedule.csv and calibration_YEAR.csv disclose every choice, score, eligibility and cutoff. Later walk-forward years legitimately train on already realized earlier evaluation years.

## Portfolio and missingness

Portfolios assign equal weights at each shared entry open, hold until next shared entry open, then rebalance with drift-adjusted weights. Empty selections hold zero-return cash; complements use the same calendar. Costs are 10bps times bought notional plus 10bps times sold notional. Initial entry and final liquidation are charged. Monthly net return is (1-start cost)*(1-gross loss or +gross gain)-1, with final liquidation multiplicatively deducted at final exit. All positions are scaled proportionally to fund costs. Turnover exports are two-sided gross traded notional/NAV, not half turnover; both buy and sell legs are provided. No slippage beyond these fees, tax, financing, or capacity model. Sharpe uses monthly net mean/sample standard deviation ×sqrt(12), zero risk-free rate. CAGR annualizes by 12/month count; MDD includes initial NAV and uses monthly observations, so intramonth drawdown is unknown. Annual rows summarize that year's segment of the continuous simulation, not independent annual restarts.

There are 1651 candidate stock-months, 1636 labeled. Only December 2018 lacks outcomes (15 stocks), and is excluded from every performance/label denominator. Its features and flags remain exported. Unknown feature conditions fail selection, are counted separately and are included in the unselected portfolio; no feature imputation. No missing OOS returns occurred. If an in-period return were missing its preassigned weight would use a disclosed zero-return proxy, rather than outcome-aware reweighting. Pooled returns in classification tables are stock-month means; strategy returns are monthly portfolio means including cash and fees. They answer different questions.

## Annual consistency and negative results

- expanding_all: annual enrichment >1 in 3/4 evaluable years; selected mean return beats unselected in 4/4 evaluable years; active-month selected mean return beats basket in 19/28 months.
- expanding_trend_pullback: annual enrichment >1 in 3/4 evaluable years; selected mean return beats unselected in 2/4 evaluable years; active-month selected mean return beats basket in 21/33 months.
- expanding_stabilization: annual enrichment >1 in 2/5 evaluable years; selected mean return beats unselected in 4/5 evaluable years; active-month selected mean return beats basket in 17/34 months.
- expanding_volume_normalization: annual enrichment >1 in 3/5 evaluable years; selected mean return beats unselected in 2/5 evaluable years; active-month selected mean return beats basket in 13/27 months.
- expanding_relative_strength: annual enrichment >1 in 2/5 evaluable years; selected mean return beats unselected in 4/5 evaluable years; active-month selected mean return beats basket in 13/28 months.
- frozen_all: annual enrichment >1 in 1/5 evaluable years; selected mean return beats unselected in 4/5 evaluable years; active-month selected mean return beats basket in 24/48 months.

|Policy|Selected gross stock-month mean|Unselected gross stock-month mean|Mean monthly two-sided turnover|
|---|---:|---:|---:|
|expanding_all|2.11%|1.34%|0.927|
|expanding_trend_pullback|1.57%|1.39%|1.098|
|expanding_stabilization|1.81%|1.35%|1.099|
|expanding_volume_normalization|-0.71%|1.52%|0.915|
|expanding_relative_strength|2.21%|1.36%|0.881|
|frozen_all|1.73%|1.33%|1.541|

All fixed rules, including ineligible and losing rules, are exported in discovery order in ranked_setups.csv, with OOS metrics alongside training fields. setup_monthly_metrics.csv exposes the full monthly denominators, selected/unselected gross means and precision/enrichment for every fixed rule. annual_metrics.csv provides annual selected/unselected counts and strategy performance. strategy_monthly_returns.csv provides all common-date portfolio paths and turnover. oos_classification_metrics.csv and strategy_metrics.csv cover all rules, adaptive/frozen policies, baseline and policy complements. policy_membership.csv makes the executed selections reviewable. policy_monthly_metrics.csv provides policy precision, recall, enrichment and selected/unselected return denominators on each OOS month.

## Earnings and limitations

Post-earnings family: **unavailable**. The existing feature file has no dated earnings variable or release timestamps. Local earnings cache/pilot files do not establish full 2009–2018 point-in-time release availability and issuer coverage; no earnings rule is manufactured from them. No raw market or earnings data file was needed or loaded. Inspection of fetch_earnings_batch5.py and analyze_pilot_earnings_2019.py confirmed that the existing pilot workflow targets 2019, outside the authorized study period; those observations were not loaded.

The prior descriptive study examined the full 2009–2018 sample, and the requested families were informed by it. Consequently this is chronological out-of-sample computation within an already explored historical period, not a pristine untouched confirmatory holdout. Sixty-four dependent rules, five adaptive selections and additional frozen diagnostics create substantial multiple-comparisons and selection risk. There are only 59 OOS months and few stocks per basket; stock/month dependence, sparse strict conjunctions and regime changes weaken inference. No p-values or significance claims are made; an OOS-positive row alone does not establish a reliable edge. Cash can improve MDD while reducing exposure, and selected rules may capture volatility rather than unique recovery information. No risk matching is claimed.

Inherited limitations: fixed historical universe survivorship/availability bias; 77 rather than nominal 79 tickers; vendor adjusted prices not independently certified point-in-time; possible split artifacts in vendor volume; label construction excludes unobserved returns; no independently validated delisting coverage. Relative-strength benchmark uses changing available members. Results apply only to this supplied basket and data convention.

## Reproduction and verification

Run `bash experiments/dev79_rsi_predictive_setups_20261101/run.sh` from repository root. A 900-second hard timeout bounds execution. study.py writes artifacts and asserts date boundaries, exact monthly winner counts/ties, open-to-open returns, 64-rule boundedness, strict calibration exit embargo, complementary policy membership, 59 equal OOS months per variant, no missing OOS returns, and finite accounting metrics. audit.json hashes source and frozen design and records missingness. verification.json records successful checks. verify.py independently replays dollar holdings, cash, fees, turnover and CAGR for all policies and complements, and reproduces training rankings and all fixed-rule OOS counts; validation.log records its result. No production files were changed by this study.
