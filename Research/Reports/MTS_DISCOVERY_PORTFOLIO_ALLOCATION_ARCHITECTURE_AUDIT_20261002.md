# MTS v4 — Portfolio Allocation Architecture Development Audit — 2026-10-02

## Finding
The apparent zero-nominee result is not a coding or concentration-gate artifact. Strong portfolio-aware candidates failed exactly one frozen gate: both max drawdown and CVaR5 were slightly worse than the ordinary equal-sizing baseline.

The strongest raw candidate, same-day top-50% EV/p10 opportunities boosted to 1.50x, produced 18.723862x terminal wealth versus 15.822560x equal sizing (+18.34%). Breadth was 56/56 tickers, 16/17 years, and 8/8 families positive, with ticker-cluster CI [0.0116351, 0.0146370]. Its max drawdown was -46.1475% versus -45.7329% and CVaR5 -3.31398% versus -3.26747%, so the frozen tail gate correctly rejected it.

## Exposure decomposition
The raw wealth gains partly reflect increased gross exposure. Same-day top-50%/1.50x beats exposure-matched equal sizing by only +0.35%, despite beating ordinary equal sizing by +18.34%.

More informative allocation effects:
- Same-day top-25%/1.50x: +14.64% wealth versus ordinary equal and +0.93% versus exposure-matched equal. Relative to exposure-matched equal, max drawdown improves about 0.117pp and CVaR5 improves about 0.006pp.
- Fixed-budget same-day top-50%/1.50x: +13.98% versus ordinary equal and +2.71% versus exposure-matched equal. Relative to exposure-matched equal, CVaR5 improves about 0.004pp while max drawdown worsens about 0.111pp.
- Legacy centered 0.75x–1.50x: +9.94% versus ordinary equal and +1.80% versus exposure-matched equal, with both max drawdown and CVaR5 better than ordinary equal in Development.

## Interpretation
EV/p10 continues to show exceptionally broad directional information. The large boost-only raw gains cannot be attributed entirely to allocation skill because they increase exposure. However, same-day relative ranking and fixed-budget redistribution retain positive excess wealth against exposure-matched controls, indicating a possible portfolio-level opportunity-ranking effect.

The next Discovery experiment should isolate that effect under a genuinely fixed capital/heat budget rather than relax the frozen risk gate. It should compare contemporaneous EV/p10 ranking against randomized or equal redistribution controls and test broad top-fraction/uplift plateaus. No additional Verification A or B evidence should be consumed.

## Integrity
This audit used only the already-generated Discovery Development report. Discovery Holdout was not opened. No additional Verification A was accessed. Verification B remains sealed. No gate or result was altered.
