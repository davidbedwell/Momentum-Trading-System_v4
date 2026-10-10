# Defensive short-duration opportunity rule until R-1

Status: USER APPROVED 2026-10-09. Supplements cash-first crash response and independent LONG/SHORT evaluation freezes.

1. When A/B/C detects a crash, FIRST transition toward cash by cancelling conflicting entries and initiating risk-managed liquidation of existing positions; execution can be delayed or adverse.
2. While the crash/Defensive state persists and before R-1 recovery, independently discover and evaluate **short-duration** opportunities in BOTH LONG and SHORT trading directions. Short-duration is a holding-horizon restriction, not a SHORT-direction mandate.
3. Repeated short-duration positions are permitted in principle: enter, exit, and reenter on distinct qualifying signals, subject to the independently validated Defensive strategy, execution costs, portfolio controls, and state checks. No automatic rollover or indefinite extension of an otherwise short-term position.
4. **No long-horizon positions may be initiated or maintained during the crash/Defensive state before R-1.** Any existing position crossing into Defensive is subject to the cash-first liquidation response. Repeated short-duration entries must not be used to circumvent the long-horizon restriction.
5. R-1 recovery is required before ordinary long-horizon trading becomes eligible again. R-1 does not itself guarantee any trade entry; each candidate still requires independent qualification.
6. The maximum permitted Defensive holding duration in sessions/calendar days is NOT YET NUMERICALLY FROZEN. No engineer may invent a cutoff; freeze and test that value before implementing or activating Defensive entry logic. Evaluate exit/reentry daily, including fresh crash-state gating.
7. Preserve the SHORT borrow cap at 6% quoted annualized and 6% research accrual; all protected banks and scientific promotion gates remain unchanged.

This file documents policy; it does not certify or activate the controller.
