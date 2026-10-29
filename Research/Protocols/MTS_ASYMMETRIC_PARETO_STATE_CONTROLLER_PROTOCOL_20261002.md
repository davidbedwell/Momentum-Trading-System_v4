# MTS v4 — Asymmetric Pareto State Controller Protocol — 2026-10-02

## Frozen objective
Build a causal state controller that preserves MTS profitable participation while selectively removing harmful downside. Exposure is capped at 100%. No leverage candidate may enter this stage.

## Evidence boundary
Use only already-consumed prior-67 Discovery and consumed heldout-50 evidence. Remaining Discovery names, Verification A remainder, and Verification B remain sealed.

## State basis
Use findings already observed in the frozen signal-meaning state matrix as hypothesis-generating evidence, not virgin evidence. Candidate neighborhoods are predeclared around:
- MTS signal intensity: high/extreme versus lower states, using causal expanding-history thresholds.
- volatility change: stable/moderate expansion/explosive expansion, including neighborhoods around 20d/60d ratios 1.25, 1.40, 1.50, 1.60.
- trend/MA context: price and slope relationships using 20/50/100/150/200 windows; SMA50/200 is a control, not privileged.
- breadth condition/change.
- market acceleration / drawdown velocity.
- lagged correlation/dispersion or loss-synchronization proxies when causally available.

## Controller classes
Exposure levels: 100%, 75%, 50%, 25%, 0%. No exposure >100%.
- Normal/productive state: 100%.
- Caution: 75% or 50%.
- Severe stress: 25%.
- Confirmed systemic warning: 0%, with 3% annualized risk-off cash.
Test entry-only scaling and whole-portfolio scaling/liquidation separately where canonical simulator semantics support them.
Use asymmetric recovery hysteresis neighborhoods of 1/3/5/10 sessions.

## Asymmetric controlling objectives
Do not use symmetric variance/standard deviation as a controlling risk objective.
1. Wealth: terminal wealth and CAGR.
2. Upside participation: positive-day/positive-period MTS return capture and productive-state capture.
3. Downside protection: max drawdown, daily CVaR5, worst-day loss, negative-day/negative-period downside capture.
4. State discrimination: productive-excitement participation retained versus systemic-warning losses avoided.
5. Robustness: prior67, heldout50, and each of the four heldout eras.

## Operational diagnostics
Risk-off fraction, switch count, whipsaw count, median state duration, re-entry delay, turnover, transaction-cost sensitivity, and missed-upside sacrifice. These do not replace primary objectives.

## Pareto governance
Discovery/search is not constrained by the current Pareto frontier. Advancement is Pareto-controlled within comparable controller classes and across survivors: a candidate is dominated when another candidate is no worse on every controlling objective and strictly better on at least one, subject to robustness checks.

Retain a near-Pareto band because sampling noise can make tiny differences meaningless. Near-frontier candidates remain eligible for robustness comparison when their objective differences are practically small. Exact tolerances must be reported rather than hidden in a scalar score.

Do not impose an arbitrary MDD ceiling or minimum upside-capture floor before mapping the attainable frontier. No weighted scalarization may choose the winner before the multidimensional frontier is visible.

## Validation requirements
Report populations separately and heldout50 by four eras. A candidate that succeeds only in one crisis/era is not robust. No ex-post selection from a single era. No promotion to untouched Verification evidence from this experiment alone.
