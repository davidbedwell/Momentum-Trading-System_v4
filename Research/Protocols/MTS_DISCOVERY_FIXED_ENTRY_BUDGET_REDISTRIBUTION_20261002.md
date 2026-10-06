# MTS v4 Discovery Fixed Entry-Budget Redistribution Protocol

Date: 2026-10-02
Stage: Discovery mechanism test

## Question
Does causal EV/p10 ranking add economic value when capital assigned to simultaneous new opportunities is redistributed rather than increased?

## Evidence boundary
Use only the pre-2021-09-13 Discovery Development population from the frozen 67-ticker Discovery cache. Do not access additional Verification A evidence or Verification B. The previously opened Discovery Holdout is researcher-exposed for this newly motivated architecture and is not fresh confirmation.

## Frozen score
Use the existing causal historical expected-return / p10-downside score with minimum 100 completed observations and genome -> family -> global fallback. Only outcomes completed before each signal date may enter the score.

## Frozen architecture
For each signal date, consider score-available simultaneous opportunities. Rank by causal EV/p10. If fewer than two are score-available, leave weights at 1x. Otherwise boost the top ceil(25%) and reduce the remaining score-available opportunities so their total entry weight is exactly the number of score-available opportunities (baseline total).

Test only top-quartile multipliers 1.5x, 2.0x, 2.5x, 3.0x, 3.5x, and 4.0x. A candidate is infeasible on a date if the required lower-rank weight would be negative; on such a date use equal 1x for score-available opportunities. Score-unavailable opportunities remain 1x.

## Primary diagnostics
Report terminal wealth, CAGR, max drawdown, daily 5% CVaR, average/peak gross exposure, minimum cash, arithmetic contribution, ticker/year/family/genome breadth, ticker-cluster bootstrap CI, and actual entry-budget conservation error.

## Interpretation
A broad positive result across the coarse ladder supports H2/H4: EV/p10 contains relative opportunity-priority information beyond merely adding exposure. Failure or instability supports the interpretation that prior wealth gains were substantially an exposure effect. This is Discovery evidence only and does not promote a rule.

No fine search, no post-result threshold adjustment, no additional A draw, and no Verification B access are authorized by this protocol.
