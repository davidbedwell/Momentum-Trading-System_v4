# MTS v4 — Discovery Fixed-Budget Opportunity Ranking Protocol — 2026-10-02

## Objective
Determine whether causal EV/p10 provides genuine portfolio-level allocation value among contemporaneous opportunities when total capital/heat is held fixed.

## Evidence
Discovery Development only during generation and selection. Discovery Holdout unavailable until representative candidates are frozen. No additional Verification A and no Verification B access.

## Fixed predictor
Causal historical expected return / historical p10 downside. Minimum completed-history N=100; genome -> family -> global -> unavailable backoff. No future outcomes. Predictor definition and historical estimator are not retuned here.

## Core design
On each signal date, hold the total nominal weight assigned to that day's eligible opportunities equal to the equal-sizing control. Redistribute that fixed budget according to EV/p10 rank. This removes the primary gross-exposure explanation for the earlier boost-only results.

## Candidate families
A. Two-level rank redistribution: top 25% or 50% receive relative weight 1.10, 1.25, or 1.50; remaining same-day opportunities receive the compensating lower weight so the day's total remains unchanged.
B. Rank-proportional redistribution: simple monotonic rank weights with maximum/minimum ratios 1.25, 1.50, and 2.00, normalized to mean weight 1.0 each signal date.
C. Score-proportional redistribution: positive EV/p10 scores winsorized only by broad caps, then normalized to mean weight 1.0 each signal date. Include a neutral fallback for unavailable scores.

## Controls
For each architecture include equal same-day allocation and deterministic seeded random-rank redistribution with identical daily weight distributions. Ranking value requires EV/p10 to outperform the matched random-rank distribution, not merely equal sizing.

## Required reporting
Terminal wealth/CAGR, max drawdown, CVaR5, average/peak exposure, positive ticker/year/family breadth, ticker/genome concentration, ticker-cluster CI, and paired wealth differences versus equal and matched random-rank controls. Report whether total same-day nominal allocation is conserved to numerical tolerance.

## Nomination
Require positive mean contribution, >=60% positive tickers/years/families, positive ticker-cluster CI lower bound, <=15% ticker/genome positive-contribution concentration, wealth above equal sizing, and not both max drawdown and CVaR5 worse. Additionally require wealth above the matched random-rank control. Neighboring parameterizations must show the same directional relationship.

## Integrity
Do not relax the prior tail-risk gate. Do not use A3 outcomes to set numerical parameters. No Holdout/A/B access during Development search.
