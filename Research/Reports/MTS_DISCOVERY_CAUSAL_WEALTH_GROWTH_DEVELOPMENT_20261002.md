# MTS v4 — Causal Wealth Growth — Development Result — 2026-10-02

## Finding
Allowing the causal EV/p10 capital-allocation principle to increase exposure materially changes the Development result. The tested wealth response is still rising at the frozen 2.00x upper boundary, so 2.00x must not be treated as an optimum.

Equal-sizing Development baseline: terminal wealth 15.822560x, CAGR 18.5442%, max drawdown -45.7329%, CVaR5 -3.26747%, average gross exposure 0.8582.

Key frontier points:
- Same-day top 50%, cap 2.00x: 20.0035x terminal wealth (+26.42%); average gross exposure 0.950; max drawdown ~0.236pp worse; CVaR5 ~0.053pp worse; +0.31% wealth versus exposure-matched equal.
- Same-day top 25%, cap 2.00x: 19.4955x (+23.21%); average gross exposure 0.936; max drawdown essentially unchanged (+0.002pp versus equal); CVaR5 ~0.041pp worse; +2.77% wealth versus exposure-matched equal.
- Boost-all cap 2.00x: 18.8234x (+18.97%); average gross exposure 0.926; max drawdown ~0.225pp worse; CVaR5 ~0.024pp worse; +1.39% wealth versus exposure-matched equal.

All 15 tested candidates passed the broad evidence screen. Eleven are nondominated under the frozen terminal-wealth/maxDD/CVaR definition. The response across 1.10x, 1.25x, 1.50x, 1.75x, and 2.00x is broad rather than an isolated parameter spike.

## Interpretation
Exposure growth is part of the economically relevant hypothesis, not merely a nuisance variable. Exposure-matched controls remain necessary to decompose allocation skill from additional risk-taking, but they should not veto a wealth-growth rule whose purpose is to deploy more capital when causal opportunity quality is high.

The 2.00x boundary is binding: terminal wealth continues to improve through the largest tested cap. Therefore the next Discovery step is a prospectively frozen frontier-extension experiment, not Holdout access. It should extend broad caps beyond 2.00x and explicitly measure whether wealth saturates or reverses as drawdown, CVaR, gross exposure, and cash constraints rise.

No Discovery Holdout, additional Verification A, or Verification B evidence was accessed.
