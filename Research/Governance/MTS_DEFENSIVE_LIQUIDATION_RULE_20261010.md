# Frozen Defensive liquidation rule — 2026-10-10

When the causal regime controller designates DEFENSIVE, all open NORMAL positions must be liquidated at the first executable price after the designation, with exit costs; proceeds move to cash. No Normal new entries during DEFENSIVE. Normal entries resume only after R-1 recovery authorizes NORMAL.

A calendar-exclusion entry mask alone does NOT implement this rule. Normal-only study evaluation must model pre-Defensive positions truncated to the first executable exit, using actual price paths and transaction costs; it must not use the original horizon endpoint or silently omit boundary-crossing trades. No same-close fills based on an end-of-day designation. Record transition timestamp, signal timestamp, execution timestamp, side, holding days, realized return, costs, and cash status.

Historical episode exclusion dates are provisional proxies, NOT validated causal controller designations. Do not claim they are equivalent to A/B/C or R-1. Use a clearly labeled calendar-proxy sensitivity analysis if the real causal state series is unavailable. Freeze regime designations before assessing the Normal strategy results.

The previously queued entry-mask-only Normal re-evaluation has been stopped BEFORE it ran beyond its one-row smoke test. Do not restart it as an integrated Normal-only performance assessment without forced-exit implementation. Active Generation 3 is not modified.