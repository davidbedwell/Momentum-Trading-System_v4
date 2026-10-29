# MTS Frozen Open-State Controller Verification-B Protocol
Date: 2026-10-03
Status: FROZEN BEFORE FIRST VERIFICATION-B OUTCOME ACCESS

## Purpose
Test whether the development finding from MTS_OPEN_STATE_SCIENTIFIC_AUDIT_20261003 transports unchanged to the untouched 100-ticker Verification B bank.

## Frozen candidate
Use rank-1 audited genome from MTS_OPEN_STATE_SCIENTIFIC_AUDIT_20261003 and the binary architecture exactly as audited: binary exposure = 1 when continuous exposure >= 0.5, otherwise 0. No genome, feature, weight, threshold, smoothing, floor, ceiling, gamma, interaction, cost, era, or portfolio-rule retuning is permitted after Verification B is opened.

## State calibration
All robust center/scale statistics used by the frozen genome are calculated only from the consumed 67-ticker development state history. They are then applied unchanged to Verification B dates. Market-state construction remains causal and shifted one session. Portfolio signal-count state is calculated causally from the Verification-B portfolio because it is a live portfolio-state variable; no future signal information is permitted.

## Verification population
Exactly all 100 names in VERIFICATION_B from MTS_V4_SP500_SCIENTIFIC_PARTITION_303_100_100_PRIOR_SOL_REPAIRED_20260915.json. Verification A is not used. No ticker may be removed because of performance. Mechanical data-unavailability exclusions must be reported.

## Base MTS
Use the same frozen Phase-3 chromosome index 0, portable 396-genome catalog, causal evidence hierarchy, safe asset, execution ordering, four era boundaries, and 10 bps primary cost used by the development audit. Each era resets to $100,000.

## Prespecified outputs
For baseline and frozen binary controller report each era and pooled: terminal factor, compounded CAGR, max drawdown, CVaR5, worst day, time underwater, average exposure, and exposure switching. Report controller minus baseline deltas.

## Pass/fail
Primary transport PASS requires: (1) pooled terminal wealth after 10 bps > baseline; (2) controller CAGR > baseline in at least 3 of 4 eras; (3) controller max drawdown is no worse than baseline in at least 3 of 4 eras; and (4) no era has controller CAGR <= 0 when baseline CAGR > 0. Otherwise FAIL. This gate is frozen before opening outcomes.

## Scientific boundary
This is one-shot Verification B. Results may be interpreted but not used to repair this candidate. Any modification after inspection is a new hypothesis and Verification B is thereafter consumed for this architecture.
