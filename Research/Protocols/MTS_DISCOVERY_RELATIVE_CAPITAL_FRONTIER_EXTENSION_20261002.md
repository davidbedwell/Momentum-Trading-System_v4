# MTS v4 — Relative Capital Frontier Extension — 2026-10-02

## Rationale
The frozen mechanism audit and pre-existing Development search indicate causal EV/p10 behaves more usefully as a relative same-day priority signal than as an isolated absolute multiplier. Existing coarse search remained wealth-censored at 4.0x, so no optimum is claimed.

## Evidence boundary
Discovery Development only. Discovery Holdout remains closed. No Verification A access. Verification B remains sealed.

## Frozen architecture
Causal EV/p10 score only. Rank simultaneously signaled trades by score. Test top 25% and top 50% boost architectures. Non-selected trades remain 1.0x. This extension changes only the coarse boost ceiling; it does not add predictors or optimize on Holdout.

## Coarse extension
Test 5x, 6x, 8x, 10x. Stop extension if neighboring points show clear wealth rollover or disproportionate risk acceleration. No fine search around the best point.

## Evaluation
Terminal wealth/CAGR, maxDD, CVaR5, exposure-matched equal baseline, ticker/year/family/genome breadth, concentration, and ticker-cluster CI. Prefer broad plateau and lower-complexity representative over peak wealth.
