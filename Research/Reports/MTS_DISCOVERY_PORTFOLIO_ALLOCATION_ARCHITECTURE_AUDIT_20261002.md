# MTS v4 — Portfolio Allocation Architecture Development Audit — 2026-10-02

## Result
The architecture experiment produced no formal nominees because every new architecture failed the same frozen gate: `not_both_tail_worse`. This is a real gate failure, not a breadth, concentration, or uncertainty failure.

## Headline versus mechanism
The highest raw terminal wealth was same-day top-50% boost at 1.50x: 18.723862x versus 15.822560x equal sizing (+18.34%). It was positive in 56/56 tickers, 16/17 years, and 8/8 families, with ticker-cluster CI [0.0116351, 0.0146370]. However average gross exposure rose by 7.11 percentage points, and its advantage over exposure-matched equal sizing was only +0.35%. Both max drawdown and CVaR5 were slightly worse.

Boost-only 1.50x showed the same pattern: 18.213499x (+15.11% versus equal), 56/56 tickers, 16/17 years, 8/8 families, but only +0.57% versus exposure-matched equal sizing and slightly worse DD/CVaR.

## Strongest allocation-efficiency lead
Same-day fixed-budget redistribution is the most interesting architecture because it retains a larger advantage after exposure matching:
- top 50%, cap 1.10x: +0.96% versus exposure-matched equal
- top 50%, cap 1.25x: +1.94%
- top 50%, cap 1.50x: +2.71%
All three have positive ticker-cluster CI and broad ticker/year/family support. This is a monotonic architecture-level relationship across the coarse pre-frozen grid, not an isolated endpoint.

The top-25% fixed-budget family also remains positive versus exposure-matched equal at all three caps (+0.55%, +1.12%, +1.49%), providing structural corroboration.

## Risk tradeoff
The fixed-budget gains currently buy a small deterioration in both frozen tail metrics. For top-50% / 1.50x, max drawdown worsens about 0.254 percentage points and CVaR5 about 0.026 percentage points versus ordinary equal sizing. Under the frozen gate, that is sufficient to reject nomination.

## Interpretation
Discovery supports two distinct facts:
1. EV/p10 ranking is extraordinarily broad at the trade level.
2. Portfolio implementation determines whether that information becomes incremental compounded wealth.

Simply boosting good-looking trades mostly adds exposure. Same-day fixed-budget redistribution shows stronger evidence of genuine capital-allocation value because its advantage survives exposure matching and increases monotonically across the coarse cap grid.

## Next scientific question
Do not weaken the frozen tail-risk gate post hoc. Instead open a new Discovery experiment asking whether the same-day fixed-budget ranking edge can be combined with an independently specified portfolio-risk budget (gross exposure / portfolio heat / contemporaneous overlap constraint) so that allocation advantage survives while tail risk is not worsened.

No additional Verification A or Verification B evidence was accessed in this audit.
