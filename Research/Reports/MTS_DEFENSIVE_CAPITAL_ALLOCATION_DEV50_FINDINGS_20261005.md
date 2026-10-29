# MTS Defensive Capital Allocation — DEV50 First-Pass Findings
Date: 2026-10-05

## Governance
This run used the exact frozen DEV50 development universe, direct daily predictor-panel observations, Yahoo-adjusted daily prices, and contemporaneous FRED DGS3MO safe accrual. It did not use the prior ticker-by-ticker optimized candidate-event cache. preserved50, TEST17, remaining Discovery, Verification A, and Verification B were not accessed.

43 of the 50 DEV symbols had usable predictor/price observations in the six historical Defensive research windows. There were 836 distinct Defensive opportunity dates and 210,488 action/hold observation rows.

## What was tested
Four risky mechanism classes were searched independently against SAFE:
- LONG_SECURITY
- SHORT_SECURITY
- LONG_MARKET
- SHORT_MARKET

SAFE was the incumbent/hurdle, not a GA chromosome. Risky economics were net of 0.10% round-trip cost and matched contemporaneous 3-month Treasury accrual.

Five stock outer folds and six leave-one-bear-out folds were used. Same-date security outcomes were averaged before fitness so correlated ticker multiplicity did not create independent-success credit.

## Stock-fold transport
LONG_SECURITY activated in all 5 omitted stock folds:
- +13.03% mean excess over SAFE across 21 heldout opportunity dates
- +15.09% across 34
- +12.76% across 25
- +15.25% across 42
- +6.11% across 68
All five independently trained winners chose 20-session holds.

SHORT_SECURITY activated in all 5 omitted stock folds, but transport was mixed:
- -8.88% across 14 dates
- +8.44% across 17
- -2.80% across 1
- +5.88% across 14
- +5.21% across 36
All five independently trained winners also chose 20-session holds.

Stock-fold results are cross-sectional transport tests, not independent bear-environment tests.

## Leave-one-bear-out transport
LONG_SECURITY:
- GFC: +0.03% mean excess vs SAFE, 153 dates, 49.0% positive dates
- 2011: +13.71%, 10 dates, 90.0% positive
- 2015-16: -6.63%, 3 dates, 33.3% positive
- 2018: no qualifying opportunity
- COVID: no qualifying opportunity
- 2022: +10.00%, 7 dates, 100% positive

SHORT_SECURITY:
- GFC: +11.81%, 12 dates, 83.3% positive
- 2011: +9.69%, 3 dates, 100% positive
- 2015-16: -5.50%, 6 dates, 0% positive
- 2018: -5.62%, 2 dates, 0% positive
- COVID: no qualifying opportunity
- 2022: +11.58%, 5 dates, 100% positive

LONG_MARKET:
- GFC: no qualifying opportunity
- 2011: no qualifying opportunity
- 2015-16: no qualifying opportunity
- 2018: +4.26%, 2 dates
- COVID: +0.79%, 2 dates
- 2022: +0.10%, 32 dates

SHORT_MARKET:
- GFC: no qualifying opportunity
- 2011: no qualifying opportunity
- 2015-16: no qualifying opportunity
- 2018: -5.28%, 4 dates
- COVID: no qualifying opportunity
- 2022: -0.10%, 124 dates

## Recurrence
Security-level winners repeatedly used stock drawdown, stock realized-volatility percentile, breadth-above-SMA200, market drawdown/return, and related breadth/stress variables. Exact rule sets were not identical, which is expected under mechanism-level recurrence rather than chromosome identity.

The strongest mechanical recurrence was holding horizon: every stock-fold LONG_SECURITY and SHORT_SECURITY winner chose 20 sessions; all six episode LONG_SECURITY and all six episode SHORT_SECURITY winners also chose 20 sessions. This is a development finding, not yet a production rule.

## Interpretation
The first-pass result rejects the idea that DEFENSIVE should imply one fixed trade direction.

1. Some unseen bear environments contain portable long-security opportunities.
2. Some contain portable short-security opportunities.
3. Some contain neither, making SAFE a legitimate winner.
4. Long and short security mechanisms can both fail in the same omitted environment (2015-16).
5. Market-direction mechanisms were much less consistently supported than security-specific mechanisms.
6. Cross-sectional stock-fold success is encouraging but cannot substitute for independent bear-environment transport.

## Important limitations before verification
This is mechanism discovery, not yet a complete capital allocator. The four risky actions were evolved independently. A causal arbitration rule deciding LONG vs SHORT vs MARKET vs SAFE has not yet been frozen.

Short-security results do not include a separate historical hard-to-borrow fee and are not production-ready.

The 20-session recurrence must be audited for interaction with the historical research-window boundaries and actual DEFENSIVE-state exit behavior before being promoted.

## Determination
DO NOT ACCESS preserved50 YET.

Use DEV50 only to design and freeze the causal arbitration layer and audit the 20-session horizon/state-boundary interaction. preserved50 remains the next verification stage only after the complete capital-allocation policy is frozen.
