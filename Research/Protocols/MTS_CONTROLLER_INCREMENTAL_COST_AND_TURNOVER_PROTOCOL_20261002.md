# MTS v4 — Controller Incremental Cost and Turnover Protocol — 2026-10-02

## Purpose
Decompose baseline MTS implementation cost from incremental controller cost and test lower-turnover implementations of the already-established state mechanism before Pareto advancement.

## Evidence boundary
Consumed heldout50 plus already-consumed state findings only. No remaining Discovery, Verification A remainder, or Verification B.

## Baseline
For each era and each cost assumption, simulate the identical canonical MTS portfolio with no state controller under the same transaction-cost accounting. Cost assumptions remain 0, 10, 25, 50 bps per dollar traded. The 3% proxy applies only to cash deliberately sidelined by a controller state; ordinary baseline cash receives no artificial bond return.

## Decomposition
For every controller/cost/era report: cost-matched baseline terminal wealth; controller terminal wealth; wealth delta versus cost-matched baseline; baseline turnover; controller turnover; incremental turnover dollars and percentage; forced-liquidation turnover; blocked-entry turnover avoided where measurable; upside/downside capture against the cost-matched baseline.

## Lower-turnover mechanisms
Preserve the same causal state definitions and 3/5-session hysteresis. Test only implementation changes, not new predictive hypotheses:
1. entry block only;
2. immediate full liquidation (existing comparator);
3. no forced liquidation, block entries until clear;
4. one-time partial liquidation of 25%, 50%, 75% of each live position on risk-state entry, then block new entries; no repeated daily liquidation;
5. one-time full liquidation on risk-state entry, not repeated liquidation bookkeeping.
All exposure remains <=100%; no leverage.

## Advancement
Pareto controls advancement across wealth/CAGR, upside capture, MDD/CVaR/worst day, downside capture, robustness across four eras, and cost-matched deployability. Preserve near-frontier candidates. Do not open untouched evidence in this stage.
