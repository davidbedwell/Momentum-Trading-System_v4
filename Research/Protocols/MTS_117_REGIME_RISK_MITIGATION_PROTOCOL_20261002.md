# MTS v4 — 117-Stock Regime Risk Mitigation Protocol — 2026-10-02

## Objective
Determine whether the dominant MTS portfolio drawdowns are systemic regime failures and whether causal regime controls can materially reduce max drawdown/CVaR while preserving most of the gross return edge.

## Evidence boundary
Use only the already-consumed 67-stock Discovery research population plus the already-consumed heldout-50 population. Do not access the remaining Discovery bank, Verification A remainder, or Verification B.

## Baselines
Evaluate the 67-stock and 50-stock populations separately and the pooled 117-stock diagnostic. Preserve each population's existing trade paths and exits. Primary capital baseline is equal sizing with finite cash. Sidelined cash earns 3.0% annualized, accrued daily.

## Causal market-state inputs
All regime decisions use only information available at the prior market close. Candidate inputs: SPY price relative to 100/150/200-session trend; 50/100/200-session trend slope; trailing market drawdown from 63/126/252-session high; 20/60-session realized volatility and volatility expansion; MTS signal crowding measured by prior-session active-position and new-signal counts relative to expanding historical quantiles.

## Candidate families
1. Trend state: prior close below SMA100/SMA150/SMA200, with optional negative slope confirmation.
2. Drawdown state: prior close 8/12/16/20% below trailing 252-session high.
3. Volatility state: realized vol above expanding 75th/85th/90th percentile; optional 20d/60d expansion ratio >1.25/1.50.
4. Crowding state: active-position or new-signal count above expanding 75th/85th/90th percentile.
5. Composite state: 2-of-3 and 3-of-4 combinations of trend, drawdown, volatility and crowding flags.
6. Change-sensitive state: rapid 10/20-session market decline plus volatility expansion.

## Anti-whipsaw / hysteresis
For every binary risk-off trigger, test re-entry only after one of: trigger clears for 1/3/5/10 consecutive sessions; SPY closes back above the selected trend for 1/3/5 sessions; or a two-threshold hysteresis band where exit uses the stricter threshold and re-entry uses the looser recovery threshold.

## Exposure responses
Test independently: block new entries only; scale new entries to 75/50/25%; scale all open exposure toward 75/50/25%; full liquidation to cash/bond proxy. For liquidation, fills occur at the next available session open/first available path mark; no same-close foresight. Existing positions otherwise retain frozen exits.

## Evaluation
Report terminal wealth, CAGR, max drawdown, daily CVaR5, p05, worst day, time in risk-off state, number of regime switches, median risk-off duration, whipsaw count, return sacrificed during false exits, avoided loss during true stress, recovery/re-entry delay, and downside capture versus the unguarded baseline. Report 2008-09, 2011, 2018, 2020 and 2022 stress windows explicitly when covered.

## Search/selection rule
Do not restrict discovery to a Pareto frontier. Retain and report all materially distinct candidates that improve either drawdown, CVaR, worst-day loss, CAGR, terminal wealth, or return-to-drawdown. Flag dominated candidates but do not discard them solely for being dominated. Emphasize robust neighborhoods and consistency across the 67 and 50 populations rather than a single optimum.

## Scientific controls
Include SMA50/200 crossover as a simplistic benchmark only. Compare every complex rule against it and against no regime control. No threshold may be chosen from untouched evidence. No result may be promoted to Verification from this experiment alone.
