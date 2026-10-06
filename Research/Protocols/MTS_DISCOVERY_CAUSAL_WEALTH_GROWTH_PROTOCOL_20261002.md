# MTS v4 — Discovery Causal Wealth Growth Protocol — 2026-10-02

## Objective
Test the original capital-allocation principle as a wealth-growth mechanism: when causal evidence identifies unusually attractive opportunities, allow portfolio exposure to grow rather than forcing every candidate back to equal-sizing exposure.

The objective is long-horizon wealth accumulation subject to explicit measurement of drawdown, tail risk, concentration, and exposure. Exposure matching remains a diagnostic decomposition, not the objective function.

## Evidence boundary
Discovery Development only for generation and selection. Discovery Holdout remains unavailable until candidate families and representative parameterizations are frozen. No additional Verification A access. Verification B remains sealed.

## Fixed predictive information
Use causal historical expected return / historical p10 downside (EV/p10), based only on outcomes completed strictly before each signal date, minimum history N=100, backoff genome -> family -> global -> unavailable. Do not retune the predictor from A3 outcomes.

## Wealth-growth hypotheses
Test broad, simple capital-growth response families rather than a fine optimum:

1. Individual opportunity boost: never reduce below 1.0x; stronger EV/p10 opportunities may receive up to 1.10x, 1.25x, 1.50x, 1.75x, or 2.00x.
2. Same-day opportunity-density boost: top 25% or 50% of contemporaneous EV/p10-ranked opportunities may receive those same broad caps.
3. Portfolio opportunity-density scaling: when the fraction/count of high-quality contemporaneous signals is elevated relative to causal historical opportunity density, permit total portfolio heat to rise in broad steps.
4. Hybrid ranking + heat: rank capital toward stronger simultaneous opportunities while allowing total exposure to expand when opportunity density is high.

No candidate may use future outcomes, future opportunity density, or Verification evidence.

## Controls
Report ordinary equal sizing and, as diagnostics, exposure-matched equal sizing for each candidate. A candidate is not rejected merely because exposure-matched excess return is small if its explicit hypothesis is that causal opportunity quality justifies additional exposure.

## Required reporting
For every candidate report terminal wealth, CAGR, max drawdown, CVaR5, daily volatility, average and peak gross exposure, minimum cash, positive ticker/year/family breadth, ticker/genome contribution concentration, ticker-cluster bootstrap CI, and wealth relative to ordinary and exposure-matched equal sizing.

Also report wealth-growth efficiency:
- terminal-wealth gain versus equal sizing;
- CAGR gain;
- max-drawdown change in percentage points;
- CVaR5 change in percentage points;
- wealth-gain per additional average gross-exposure point;
- CAGR-gain per additional max-drawdown point when max drawdown worsens.

## Discovery frontier
Do not require risk to be literally no worse than equal sizing. Construct a nondominated wealth/risk frontier. Candidate A dominates B only if A has at least as much terminal wealth and no worse max drawdown and CVaR5, with one strict improvement.

Candidates eligible for freezing must additionally retain broad evidence: positive mean sizing contribution; >=60% positive tickers, years, and families; ticker-cluster 95% CI lower bound >0; <=15% positive contribution from any one ticker or genome; and neighboring/simple parameterizations supporting the same directional relationship.

Do not select a single historical maximum solely because it has the greatest terminal wealth. Prefer broad plateaus and representative frontier points spanning conservative, intermediate, and aggressive exposure growth.

## Holdout rule
Before opening Discovery Holdout, freeze a small set of structurally representative frontier nominees and their exact parameters. Holdout is replayed once. No post-Holdout retuning.

## Integrity
A3 motivates the architecture question only. Its five outcomes do not set parameters. Remaining 55 Verification-A names stay researcher-blinded/sequestered. Verification B stays sealed. No paper/live promotion from Discovery alone.
