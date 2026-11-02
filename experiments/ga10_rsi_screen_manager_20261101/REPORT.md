# GA10 experimental prototype results

Functionality smoke passed; completed one bounded training search. No production changes or GA6/GA7 replay. Stopped at the frozen budget.

|Split|Strategy|Net CAGR|Daily MDD|Mean exposure|Turnover|
|---|---|---:|---:|---:|---:|
|train|ga10|9.77%|17.01%|26.53%|62.50|
|train|monthly_rsi_setup|53.80%|23.19%|71.94%|83.89|
|train|monthly_rsi|35.82%|29.74%|100.00%|89.54|
|examined_holdout|ga10|-2.23%|21.10%|13.76%|27.22|
|examined_holdout|monthly_rsi_setup|15.53%|32.99%|81.80%|91.82|
|examined_holdout|monthly_rsi|11.82%|26.67%|100.00%|86.34|

train: GA10 CAGR difference vs setup baseline -44.03%; vs RSI baseline -26.05%. MDD preference met: True. Actions: `{"entry": 591, "hold": 1731, "add": 1526, "reduce": 0, "exit": 591}`.

examined_holdout: GA10 CAGR difference vs setup baseline -17.76%; vs RSI baseline -14.05%. MDD preference met: True. Actions: `{"entry": 202, "hold": 1150, "add": 847, "reduce": 0, "exit": 202}`.

The monthly screen only grants entry eligibility. GA10 can decline entry, enter later in the month, and continue managing positions offscreen. The baselines deliberately purchase their monthly baskets. All use the same 10 bp per-side notional cost and adjusted next-open accounting. Training selection is lexicographic feasible CAGR / infeasible MDD; evaluation never participates in selection. Drawdown stop cannot guarantee a 25% realized limit through gaps.

2014–2018 is previously examined holdout, not pristine validation. The frozen screen itself was selected by earlier research. Adjusted archive prices and retrospective DEV79 membership are not certified PIT; no unbiased deployability or alpha claim is supported. No data after 2018 enter features or evaluation. Missing held prices fail closed. Fractional shares, instant sale proceeds, no market impact, taxes, settlement delays or cash interest. Final positions marked to close without liquidation fees.

Reproduce: `bash experiments/ga10_rsi_screen_manager_20261101/run.sh`. See PLAN.md, test_ga10.py, smoke_gate.json, bounded/search.csv, bounded/genome.json, per-strategy daily paths/trades, monthly_screen.csv and provenance.json. This completes the prototype; further GA scale is not authorized by these returns.

Prototype behavior: the selected genome made no reduce trades, although the reduction branch passed a forced-state test. Offscreen management fills: {'train': {'offscreen_management_fills': 589, 'entries_outside_screen': 0}, 'examined_holdout': {'offscreen_management_fills': 359, 'entries_outside_screen': 0}}. The learned drawdown stop uses a persistent high-water mark and can leave a fully liquidated account in cash for the rest of a split; no reset or restart rule was tuned. Low exposure and cash lockout limit this prototype.

Validation: four focused tests passed; an independent dollar ledger reconciled all 12 smoke/bounded saved portfolio paths, including fees, cash, open and close NAV. Both frozen training genomes match the highest exported training fitness. See verification.json.
