# MTS v4 — Discovery Risk-Normalized Ranking Protocol — 2026-10-02

## Objective
Determine whether the causal EV/p10 ranking creates enough excess return per unit of portfolio risk to outperform equal sizing after the ranked portfolio is run at a modestly lower total risk budget.

## Evidence boundary
Discovery Development only for candidate generation. No additional Verification A and no Verification B access. Discovery Holdout remains closed until representatives are frozen.

## Fixed ranking architecture
Use same-day top-50% EV/p10 fixed-budget redistribution. EV/p10 is unchanged and fully causal. Test caps 1.25x and 1.50x. No volatility, ATR, concurrency, or A3-derived parameter enters the ranking.

## Coarse risk-budget grid
Run each ranked architecture at exactly 100%, 95%, and 90% of the ordinary equal-sizing base trade fraction. These coarse levels are frozen before results and are not optimized to a target drawdown. Also run equal sizing at the same 100%, 95%, and 90% base fractions.

## Primary comparison
A ranked candidate qualifies only if:
1. terminal wealth exceeds ordinary 100%-risk equal sizing;
2. terminal wealth exceeds equal sizing at the same risk-budget scale;
3. max drawdown is no worse than ordinary 100%-risk equal sizing;
4. CVaR5 is no worse than ordinary 100%-risk equal sizing;
5. the unchanged trade-level EV/p10 contribution gate remains satisfied: positive mean contribution, >=60% positive ticker/year/family breadth, ticker-cluster CI lower bound >0, and <=15% ticker/genome concentration.

## Stability
Prefer a result that works across both 1.25x and 1.50x caps and/or neighboring 90%/95% risk levels. No isolated optimum.

## Integrity
This is portfolio risk normalization, not relaxation of the risk gate. The ordinary 100% equal-sizing risk envelope remains the benchmark. No Verification evidence is accessed.
