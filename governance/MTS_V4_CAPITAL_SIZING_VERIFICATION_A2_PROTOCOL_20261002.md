# MTS v4 Capital Sizing — Verification A2 Frozen Protocol — 2026-10-02

## Incident-aware role
This is the formal 20-name capital-sizing Verification A2 tranche following the validation-scope incident documented in `MTS_V4_VALIDATION_SCOPE_INCIDENT_20261002.md`.

The original Verification-A cohort contained 100 names. Twenty A1 names were previously opened for a separate structural hypothesis. The remaining 80 were mechanically reconstructed during the scope incident, but no aggregate capital-sizing result, ticker-level capital-sizing result, criterion value, or conclusion was exposed to David or the AI Research Director.

A2 consumes exactly 20 of those 80. The other 60 remain MACHINE-ACCESSED / RESEARCHER-BLINDED and are sequestered from this evaluation. Verification B remains sealed.

## A2 selection
A2 is the first 20 records in the pre-existing frozen 80-target input manifest, preserving its existing order. This rule uses no outcome-derived information and was fixed before any A2 performance result was observed.

Evidence budget: EXACTLY 20 target security IDs. The executable MUST abort unless target count is 20. It may read checkpoints only for those 20 targets. It must not aggregate, score, inspect, or report the sequestered 60.

## Frozen hypothesis and calibration
Unchanged from the pre-result capital-sizing protocol frozen at commit `13506ad`:
- candidate: `ev_over_risk_p10_loss_floor0.5_cap2.0`
- causal expected return / p10 loss
- exact genome history when >=100 completed observations; otherwise family >=100; otherwise global >=100; otherwise neutral 1.0x
- score scale 3.2434248679805613
- floor 0.50x
- cap 2.00x
- base trade fraction 0.001321003963011889
- no recalibration, optimization, search, or retuning.

The same 1,289 transported frozen candidate genomes, completed signal-day cutoff, cooldown/non-overlap, next-session-open entry, frozen-horizon close exit, and causal history rules remain unchanged.

## Frozen evaluation criteria
No criteria are changed because of the incident. `VERIFICATION_A2_VALIDATED` requires ALL:
1. sized terminal wealth > ordinary equal-sizing baseline;
2. sized terminal wealth > exposure-matched equal-sizing baseline;
3. sized max drawdown no worse than ordinary equal baseline;
4. sized daily CVaR5 no worse than ordinary equal baseline;
5. positive sizing contribution on >50% of usable A2 tickers.

Report all component metrics regardless of composite outcome. A failure of the composite does not erase informative component effects.

## Sequestration
The 60 non-A2 Verification-A checkpoints must not be opened or aggregated during A2. They remain labeled MACHINE-ACCESSED / RESEARCHER-BLINDED. Verification B must not be accessed.
