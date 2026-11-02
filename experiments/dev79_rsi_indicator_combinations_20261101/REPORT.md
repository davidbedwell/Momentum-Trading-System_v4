# RSI + fixed indicator combinations, exploratory 2009–2018

Executed all 129 combinations: 9 singles, 36 pairs, 84 triples, plus original control. Definitions and hypotheses were saved in PLAN.md before outcome computation. No outcome-based eligibility, support filter, threshold fitting, GA, production changes or 2019+ rows. All combinations ranked in full_ranked.csv, including sparse and losing rows.

Original control reconciles every monthly net return (max error 2.92e-16); CAGR 23.193680%, daily MDD 29.7378%, monthly Sharpe 1.1716, 1651 stock-months. Original CAGR uses 252/2516 session annualization.

Accounting follows original exactly, including December 31, 2018 terminal CLOSE rather than January 2019 open; no terminal liquidation. Other intervals are open-to-open. A strictly open-to-open full December result is unavailable without forbidden 2019 data. Empty cash earns zero gross return; selling into cash incurs the original commission. PLAN.md documents exact fees and feature definitions.

|Rank|Rule|CAGR|Daily MDD|Sharpe|Active months|Stock-months|Matched-control CAGR|
|---:|---|---:|---:|---:|---:|---:|---:|
|1|k2_2-4|33.30%|32.42%|1.16|92|321|13.87%|
|2|k1_4|27.75%|32.42%|1.00|96|426|14.36%|
|3|k1_1|27.19%|24.25%|1.64|118|981|26.20%|
|4|k2_5-6|25.74%|30.02%|0.76|77|183|12.34%|
|5|k2_1-2|25.44%|24.25%|1.55|117|893|22.83%|
|6|k1_6|24.15%|30.30%|1.09|106|441|17.61%|
|7|k1_2|23.98%|32.64%|1.21|120|1494|23.19%|
|8|control|23.19%|29.74%|1.17|120|1651|23.19%|
|9|k2_2-6|23.01%|33.12%|1.10|105|364|17.96%|
|10|k2_2-5|22.38%|37.37%|0.94|118|797|23.89%|
|11|k2_2-8|22.23%|34.08%|1.03|118|672|24.05%|
|12|k2_1-5|21.75%|27.77%|1.30|109|510|21.75%|

These are descriptive leaders after 129 dependent tests, not validated alpha. Entire 2009–2018 is exploratory in-sample. No blind or independent holdout claim. Prior feature exploration adds unquantified researcher selection. Fixed historical 77-ticker universe has survivorship/availability bias, uncertain delisting coverage and vendor adjustment provenance; vendor volume can be split-sensitive.

Each matched control uses the original basket on exactly the selected strategy active months and cash otherwise, including its own drift and transaction costs. This matches binary capital exposure, not volatility, beta or stock count. CAGR-minus-matched and active-month net means/gross excess separate selection evidence from cash timing; active averages are descriptive and omit cash-transition sale costs on inactive months. No active-month CAGR is mislabeled as calendar performance.

monthly.csv supplies every portfolio/month count, exposure, net/gross returns, fees and NAV. selections.csv and candidate_flags.csv expose all decisions. annual.csv supplies continuous-path year segments for all strategies and matched controls; year_slices.csv explicitly includes 2009, 2011, 2015–16, 2018. Annual/slice CAGR uses 12/months and MDD is monthly; full ranked MDD uses daily close marks plus opening endpoints. Full CAGR uses original session convention. daily_nav.npz columns follow control then itertools combination order, then matched controls in same order. Full rankings are available regardless of headline table. Verification independently replays monthly dollar accounting and exact memberships.

|Order|Tested|Above original CAGR|Median CAGR|Minimum CAGR|Maximum CAGR|
|---:|---:|---:|---:|---:|---:|
|1|9|4|21.55%|3.04%|27.75%|
|2|36|3|11.70%|-5.08%|33.30%|
|3|84|0|5.16%|-5.51%|19.59%|

Year slices below use the CAGR leader descriptively; all rules and matched controls are in year_slices.csv. Return is cumulative net return, not annualized for 2015–16.

|Slice|Portfolio|Net return|Exposure|Stock-months|
|---|---|---:|---:|---:|
|2009|control selected|68.94%|100.00%|144|
|2009|k2_2-4 selected|92.31%|58.33%|22|
|2009|k2_2-4 matched_control|53.79%|58.33%|84|
|2011|control selected|9.57%|100.00%|156|
|2011|k2_2-4 selected|-1.45%|83.33%|26|
|2011|k2_2-4 matched_control|-7.84%|83.33%|130|
|2015-16|control selected|23.67%|100.00%|349|
|2015-16|k2_2-4 selected|37.66%|79.17%|73|
|2015-16|k2_2-4 matched_control|5.61%|79.17%|276|
|2018|control selected|-5.84%|100.00%|180|
|2018|k2_2-4 selected|-14.29%|83.33%|43|
|2018|k2_2-4 matched_control|-9.74%|83.33%|150|

Verification PASS: independently reconstructed original prior-close eligibility and RSI ranking, all 129 conjunction memberships, matched exposure, every monthly dollar-accounting path (bisection fee solver; maximum error 5.14e-16), baseline monthly reconciliation (2.93e-16). See verification.json and validation.log. Reproduce with bash run.sh.
