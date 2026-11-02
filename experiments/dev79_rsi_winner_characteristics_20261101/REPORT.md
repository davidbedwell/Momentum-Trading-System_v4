# DEV79 RSI winner characteristics, 2009–2018

Executed historical descriptive study: 1651 selected stock-months, 1636 labeled, 457 winners across 119 outcome months. 32 continuous features and 68 threshold characteristics. No production changes, optimization, GA, or 2019+ observations.

## Method and boundary

Holdings are taken verbatim from `experiments/dev79_monthly_indicator_20261101/adjusted/discovery/rsi14_oversold/holdings.csv`. Daily file: `/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet`. Features use the immediately preceding global trading session, with no forward fill. Adjusted OHLC = raw OHLC × adj_close/close, matching the source experiment; volume is vendor volume without split adjustment. Vendor historical adjustment factors are not independently point-in-time certified. Source split audit favors already split-adjusted prices, but is a heuristic. RSI uses Wilder-style EWM alpha 1/14, matching source initialization; maximum source signal discrepancy = 7.1054274e-15.

Outcome is adjusted next calendar-month first observed session open / entry open − 1, no fees. Rank descending return with ticker ascending for exact ties; winners are exactly ceil(n/4) among observed outcomes each month (thus potentially above 25%). Missing outcomes are excluded from labels, never imputed. December 2018 is censored because its next open is in 2019; features and selected candidates remain exported. No 2019+ rows are loaded. Warmup uses available pre-2009 data.

All medians are contemporaneous within the selected RSI candidate month, without outcome information; strict inequalities exclude equal-to-threshold values. Fixed thresholds and definitions are in thresholds.csv. Returns use trading-session lags; volatility is sample daily standard deviation annualized sqrt(252); slopes are MA/MA 21 sessions earlier−1; drawdown is close/trailing maximum−1; ATR is simple 14-session mean true range / close. Reversal compares last 5-session return with preceding 21-session return (unequal horizons); acceleration compares consecutive 21-session returns. Relative strength subtracts compounded daily equal-weight available-return DEV79 universe performance; universe has 77 tickers and reflects the supplied fixed historical universe, with survivorship/availability bias. Ratios of rolling vendor volume may be split-sensitive.

## Source coverage discrepancy

The requested DEV79 label does not imply 79 observed price series here: the supplied file contains 77 tickers before 2019. Selected holdings range from 12 to 15 per month. The study preserves the supplied holdings rather than rebuilding a different universe or selection. Missing feature counts are disclosed in audit.json.

## Pooled prevalence ranking

|Characteristic|Winners n/N (%)|Nonwinners n/N (%)|Lift|
|---|---:|---:|---:|
|rsi14__gt_30|400/457 (87.5%)|1039/1179 (88.1%)|0.99|
|drawdown_21__gt_-0.1|315/457 (68.9%)|856/1178 (72.7%)|0.95|
|ma_slope_200_21__gt_0|288/444 (64.9%)|766/1162 (65.9%)|0.98|
|return_252__gt_0|282/444 (63.5%)|690/1158 (59.6%)|1.07|
|vol_60__above_month_median|263/454 (57.9%)|521/1174 (44.4%)|1.31|
|ma_slope_100_21__gt_0|254/451 (56.3%)|661/1171 (56.4%)|1.00|
|atr14_pct__above_month_median|255/457 (55.8%)|531/1179 (45.0%)|1.24|
|reversal_5_vs_prior21__gt_0|254/457 (55.6%)|636/1177 (54.0%)|1.03|
|vol_21__above_month_median|251/457 (54.9%)|534/1177 (45.4%)|1.21|
|return_252__above_month_median|240/444 (54.1%)|533/1158 (46.0%)|1.17|
|volume_ratio_5_20__above_month_median|246/457 (53.8%)|539/1178 (45.8%)|1.18|
|vol_10__above_month_median|241/457 (52.7%)|545/1179 (46.2%)|1.14|

## Year-by-year consistency

Positive winner-minus-nonwinner prevalence years among the leading pooled characteristics (out of evaluable years):

- rsi14__gt_30: 5/10
- drawdown_21__gt_-0.1: 5/10
- ma_slope_200_21__gt_0: 4/10
- return_252__gt_0: 7/10
- vol_60__above_month_median: 9/10
- ma_slope_100_21__gt_0: 5/10
- atr14_pct__above_month_median: 8/10
- reversal_5_vs_prior21__gt_0: 6/10
- vol_21__above_month_median: 7/10
- return_252__above_month_median: 7/10
- volume_ratio_5_20__above_month_median: 8/10
- vol_10__above_month_median: 8/10

## Co-occurring characteristics

Exhaustive pairs/triples of the fixed-rule family (excluding two redundant long-MA slopes), requiring at least 20 matching winners AND 20 matching nonwinners. Ranked by winner prevalence, not conditional win rate. All retained combinations are exported with yearly comparisons.

|Characteristic|Winners n/N (%)|Nonwinners n/N (%)|Lift|
|---|---:|---:|---:|
|rsi14__gt_30 & drawdown_21__gt_-0.1|301/457 (65.9%)|803/1178 (68.2%)|0.97|
|rsi14__gt_30 & return_252__gt_0|254/444 (57.2%)|621/1158 (53.6%)|1.07|
|rsi14__gt_30 & reversal_5_vs_prior21__gt_0|227/457 (49.7%)|562/1177 (47.7%)|1.04|
|return_252__gt_0 & drawdown_21__gt_-0.1|211/444 (47.5%)|564/1158 (48.7%)|0.98|
|rsi14__gt_30 & return_126__gt_0|209/450 (46.4%)|520/1170 (44.4%)|1.05|
|drawdown_21__gt_-0.1 & drawdown_63__gt_-0.1|206/454 (45.4%)|578/1174 (49.2%)|0.92|
|rsi14__gt_30 & return_252__gt_0 & drawdown_21__gt_-0.1|200/444 (45.0%)|531/1158 (45.9%)|0.98|
|rsi14__gt_30 & drawdown_63__gt_-0.1|198/454 (43.6%)|554/1174 (47.2%)|0.92|
|rsi14__gt_30 & drawdown_21__gt_-0.1 & drawdown_63__gt_-0.1|198/454 (43.6%)|554/1174 (47.2%)|0.92|
|return_126__gt_0 & return_252__gt_0|184/444 (41.4%)|438/1158 (37.8%)|1.10|
|rsi14__gt_30 & positive_fraction_63__gt_0.5|184/454 (40.5%)|478/1174 (40.7%)|1.00|
|return_126__gt_0 & drawdown_21__gt_-0.1|181/450 (40.2%)|465/1170 (39.7%)|1.01|

## Uncertainty and interpretation

CSV tables include numerator/denominator, winner and nonwinner prevalence, lift, prevalence difference, and marginal 95% Wilson intervals. These intervals assume independent stock-months and can understate uncertainty because months, tickers and characteristics are dependent; they are not simultaneous or cluster-adjusted. All comparisons and rankings are EXPLORATORY, with no significance claims or multiplicity-adjusted discovery claims. No predictive edge is validated. Many high-prevalence features are equally prevalent among nonwinners. Full year consistency reports positive-difference years out of evaluable years, plus the annual range; missing values use characteristic-specific denominators. Combinations are dependent and their sample-size filter is descriptive.

## Monthly iteration and verification

single_commonality.csv contains the full characteristic ranking separately for every one of the 120 months, every year, and pooled; monthly_summary.csv lists every month, including censored December 2018. stock_month_features.csv contains ranks, labels, return endpoints and every feature. characteristic_flags.csv permits reproduction of every comparison. cooccurrence_pooled.csv and cooccurrence_yearly.csv contain full retained pair/triple tables. year_consistency.csv summarizes annual single-feature consistency. audit.json records missingness, coverage and execution bounds. Assertions verify 120 months, pre-entry dates, rank counts, and no 2019+ data. Run with run.sh; validation uses verify.py.
