# MTS v4 — Discovery Risk-State Allocation Protocol — 2026-10-02

## Objective
Test whether the EV/p10 ranking edge can improve compounded wealth without degrading both max drawdown and CVaR5 by suppressing portfolio reallocation during unusually risky opportunity-set states.

## Evidence boundary
Discovery Development only for candidate generation. No additional Verification A and no Verification B access. Existing Discovery Holdout remains closed until representatives are frozen.

## Fixed predictor and allocation form
Keep causal historical EV/p10 unchanged. Use same-day top-50% ranking with fixed-budget redistribution, because the prior architecture work showed this is the most promising exposure-controlled family. Test caps 1.25x and 1.50x only.

## Causal risk-state gates
For each signal date, summarize only information known before entry:
- median 20-session realized volatility across that day's signaled opportunities;
- median ATR/price across that day's signaled opportunities.
Compare today's value only with the expanding distribution of prior signal-date medians. No future feature values or outcomes may be used.

Test overlay-active states:
1. realized-volatility <= prior median;
2. realized-volatility <= prior 75th percentile;
3. ATR/price <= prior median;
4. ATR/price <= prior 75th percentile;
5. BOTH realized-volatility and ATR/price <= their prior medians;
6. BOTH <= their prior 75th percentiles.

## Required metrics/gate
Unchanged: positive mean contribution; >=60% positive ticker/year/family breadth; ticker-cluster CI lower bound >0; <=15% ticker/genome positive-contribution concentration; terminal wealth > equal sizing; and max drawdown/CVaR5 may not both worsen. Report exposure-matched equal sizing.

## Selection
Prefer a broad, simple gate that passes at both 1.25x and 1.50x. Do not select an isolated cap or threshold. Freeze at most two structurally distinct representatives before any Discovery Holdout replay.

## Integrity
Risk gates may use causal pre-entry features only. A3 outcomes do not determine thresholds. No relaxation of the tail-risk gate.
