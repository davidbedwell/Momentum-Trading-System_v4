# MTS v4 — Discovery Risk-Budgeted Allocation Protocol — 2026-10-02

## Objective
Test whether the broad same-day EV/p10 fixed-budget redistribution edge can survive under an explicit portfolio risk budget, without weakening the prior tail-risk gate.

## Evidence
Discovery Development only for generation and selection. Existing Discovery Holdout unavailable until representative candidates are frozen. No additional Verification A and no Verification B access.

## Fixed ranking mechanism
Use the unchanged causal EV/p10 score. Restrict architecture to same-day fixed-budget redistribution, using the already observed broad structural settings top 25% and top 50%, with redistribution caps 1.10x, 1.25x, 1.50x. These are architecture controls, not newly optimized thresholds.

## Risk-budget families
Apply simple prospective portfolio controls independently of future returns:
1. Gross-exposure ceiling: scale new allocations when projected gross exposure would exceed a fixed ceiling.
2. Active-position/overlap heat ceiling: scale incremental redistribution as contemporaneous active trade count rises.
3. Combined gross + overlap ceiling.

Use only coarse ceilings derived from the equal-sizing Development exposure distribution: baseline average gross, baseline 90th-percentile gross, and baseline peak gross as reference anchors. Do not search fine numerical thresholds.

## Required comparisons
Compare each risk-budgeted allocation with ordinary equal sizing and an exposure-matched equal-sizing control. Report terminal wealth/CAGR, max drawdown, CVaR5, average/peak gross exposure, breadth, concentration, ticker-cluster CI, and fraction/time of risk-budget binding.

## Nomination gate
Retain the existing gate unchanged: positive mean contribution; >=60% positive tickers, years, families; ticker-cluster CI lower bound >0; <=15% positive-contribution concentration per ticker/genome; terminal wealth > equal sizing; and max drawdown/CVaR5 not both worse. Require neighboring/simple parameterizations to support the relationship.

## Integrity
A3 outcomes may motivate the portfolio-risk question but may not set numerical thresholds. No Verification evidence may be used for parameter selection. No paper/live promotion from this experiment.
