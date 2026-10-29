# MTS v4 — Signal Meaning State Matrix Protocol — 2026-10-02

## Research question
What market states change the meaning of an MTS signal?

## Governance
Use only the consumed prior-67 Discovery population and consumed heldout-50 population. Remaining Discovery names, Verification A remainder, and Verification B remain sealed.

Discovery is not restricted by the current Pareto frontier. Candidate state architectures may be nonlinear, conditional, interaction-based, or dominated during intermediate mechanism research. Advancement is Pareto-controlled: a candidate cannot advance if another tested candidate is at least as good on every controlling objective and strictly better on at least one. Mechanistically informative dominated candidates remain documented but do not become deployment candidates.

## State dimensions
All state variables are causal and lagged to information available by the prior close.

1. MTS signal intensity: new-signal count and active-position count relative to expanding 60-session and expanding-history distributions; bins low/normal/high/extreme.
2. Volatility: 20d realized level relative to expanding history; 20d/60d expansion ratio; bins contracting/stable/expanding/exploding.
3. Trend/MA structure: price vs SMA50/100/150/200; SMA slopes; fast/slow relationships (20/50, 20/100, 50/100, 50/150, 50/200); distance from MA normalized by realized volatility.
4. Breadth: fraction of available current-universe constituents above SMA50/100/200 and breadth change over 5/20 sessions. Current-S&P survivorship caveat applies.
5. Correlation/dispersion: cross-sectional daily return dispersion plus average/median pairwise market co-movement proxies where computationally practical; portfolio loss synchronization as diagnostic only when it can be lagged causally.
6. Market acceleration: SPY 5/10/20/60-session returns; change in return/trend; drawdown velocity.

## Core inquiry
Do identical levels of MTS excitement have materially different forward outcomes depending on the surrounding state? Specifically test whether high/extreme signal intensity is an opportunity in healthy/expanding regimes but a warning during systemic deterioration.

## Outcomes
For each state and interaction, report forward 1/5/10/20-session aggregate MTS returns, trade-level forward outcomes where available, win rate, downside-tail outcomes, subsequent portfolio drawdown, state persistence, and sample size. Report both populations independently before pooled summaries.

## Candidate controllers
After descriptive state mapping, construct prespecified controller classes from discovered mechanisms: graded exposure (125/100/75/50/25/0%), entry gating, and full risk-off only for confirmed systemic states. Risk-off cash earns 3% annualized. Re-entry uses asymmetric hysteresis.

## Pareto-controlled advancement
Controlling objectives: terminal wealth/CAGR, max drawdown, daily CVaR5, worst-day loss, and robustness across the two consumed populations and four heldout eras. Operational diagnostics (risk-off fraction, switch count, whipsaw, missed upside) are reported and may break near-ties but do not replace the controlling objectives. Pareto dominance is evaluated within comparable controller classes and again across surviving classes.

## Controls
No-control MTS and SMA50/200 remain controls. Volatility expansion 20d/60d >1.5 is a previously observed comparator, not a privileged solution. No untouched evidence is used for threshold selection.
