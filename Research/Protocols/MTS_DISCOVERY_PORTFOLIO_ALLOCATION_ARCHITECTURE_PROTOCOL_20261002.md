# MTS v4 — Discovery Portfolio Allocation Architecture Protocol — 2026-10-02

## Objective
Explain and exploit the observed distinction between broad positive EV/p10 trade-level contribution and lower compounded portfolio wealth. Discovery only. Do not consume additional Verification A or any Verification B evidence.

## Fixed predictor
Keep the already-replicated causal score unchanged: historical expected return / historical p10 downside, using only outcomes completed strictly before each signal date, minimum history N=100, backoff genome -> family -> global -> unavailable. No new signal-quality predictor search in this experiment.

## Scientific question
Test whether portfolio implementation, rather than predictor validity, caused the A3 wealth shortfall. In particular test capital reduction, incremental-capital overlays, and contemporaneous opportunity ranking.

## Development evidence
Use only the existing Discovery Development period before the frozen split. Existing Discovery Holdout remains unavailable during candidate generation and selection. It may be replayed only after candidate families and representative parameterizations are frozen.

## Candidate architecture families
1. Legacy centered sizing control: 0.75x–1.50x using the frozen EV/p10 calibration.
2. Boost-only overlay: never reduce a trade below 1.0x; allocate incremental capital only to higher EV/p10 scores.
3. Conservative boost-only overlay: smaller incremental caps to test whether modest extra capital preserves compounding.
4. Same-day relative-rank overlay: compare only opportunities signaled on the same date and boost stronger contemporaneous opportunities without reducing the rest.
5. Fixed-budget same-day redistribution: preserve approximately the same total weight among same-day opportunities while shifting weight toward higher-score opportunities.
6. Exposure-matched versions where scientifically meaningful, to separate ranking value from merely adding gross exposure.

## Parameter discipline
Use broad simple grids only: uplift/cap levels 1.10x, 1.25x, 1.50x and same-day top fractions 25%, 50%. No fine threshold optimization. Prefer broad plateaus and simpler rules.

## Required Development reporting
For every candidate report terminal wealth/CAGR, max drawdown, CVaR5, average/peak gross exposure, mean trade sizing contribution, positive ticker/year/family breadth, ticker and genome concentration, and ticker-cluster bootstrap CI. Report comparison to equal sizing and exposure-matched equal sizing when applicable.

## Nomination
A candidate family can advance only if it shows positive mean trade contribution, >=60% positive tickers, >=60% positive years, >=60% positive families, ticker-cluster 95% CI lower bound >0, no >15% positive-contribution concentration in one ticker or genome, and terminal wealth above equal sizing without both max drawdown and CVaR5 worsening. Neighboring/simple parameterizations must support the same directional relationship.

## Integrity
No Verification A or B access. No use of the five A3 ticker outcomes to select numerical parameters. A3 motivates only the architecture question. No paper/live promotion from this experiment.
