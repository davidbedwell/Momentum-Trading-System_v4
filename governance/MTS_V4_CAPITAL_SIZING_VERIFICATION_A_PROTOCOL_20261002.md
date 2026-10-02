# MTS v4 — Capital-Sizing Verification A Frozen Protocol

**Freeze date:** 2026-10-02
**Role:** untouched out-of-sample validation of one already-frozen capital-sizing candidate. No Search, retuning, candidate substitution, threshold change, genome selection, or score recalibration is permitted.

## Evidence boundary
Verification A1 (20 names) was previously opened for a different hypothesis and is excluded. This validation uses exactly the still-sealed 80-name `verification_a_remaining` cohort in `MTS_V4_CAPITAL_SIZING_VERIFICATION_A_INPUT_FROZEN_20261002.json`. Verification B remains sealed regardless of this result.

## Frozen hypothesis
Compare equal-sized MTS trades with the already-frozen growth policy `ev_over_risk_p10_loss_floor0.5_cap2.0`: causal expected return divided by p10 loss, hierarchy exact genome when >=100 completed observations, else family when >=100, else global when >=100, else neutral 1.0x; score scale `3.2434248679805613`; floor 0.50x; cap 2.00x. No value may be recalibrated from Verification A.

## Frozen transported trade population
Use all 1,289 unique candidate genomes actually present in the corrected 125,002-trade Discovery capital-study population, unchanged, on every one of the 80 Verification-A targets. Candidate definitions and target identities are frozen in the input manifest. Within each target/candidate signal stream, use the same completed signal-day information cutoff and non-overlap/cooldown semantics as Discovery. Entry is next-session open and exit is the close at the candidate's frozen forward horizon. No stop or profit target is introduced.

This transport tests whether the capital-sizing relationship generalizes to new securities. Equal sizing and conditional sizing receive exactly the same transported trades; therefore any difference is attributable to sizing, not signal selection.

## Causal history
Seed risk/expectancy history only with completed observations from the frozen Discovery population. During Verification A, prior Verification-A observations may enter history only after their exits and only causally; same-date or not-yet-completed outcomes are unavailable. No future Verification information may enter a score.

## Portfolio model
Use the frozen non-levered 100% capital-budget simulator and frozen base trade fraction from the Discovery experiment. Deterministic same-time allocation. Report average and peak gross exposure, minimum cash, terminal compounded wealth, CAGR-equivalent, max drawdown, daily p05/CVaR5, volatility, and return-to-drawdown. Also compute an exposure-matched equal-sizing baseline as a falsification control without changing the candidate.

## Primary validation criteria — frozen before results
The candidate VALIDATES on Verification A only if all are true:
1. terminal compounded wealth exceeds the ordinary equal-sizing baseline;
2. terminal compounded wealth exceeds the exposure-matched equal-sizing baseline;
3. max drawdown is no worse than the ordinary equal-sizing baseline;
4. daily CVaR5 is no worse than the ordinary equal-sizing baseline;
5. the sizing contribution is positive on >50% of usable Verification-A tickers.

These are deliberately conservative directional replication criteria. No rescue threshold may be invented after results. Report CAGR and return-to-drawdown as secondary evidence, not substitutes for a failed primary criterion.

## Outcome and governance
Possible conclusions: `VERIFICATION_A_VALIDATED`, `VERIFICATION_A_FAILED`, or `IMPLEMENTATION_FAILURE`. A failed result may not be repaired on these 80 names and retested as pristine. A validated result still does not authorize paper/live deployment. First audit concentration, provenance, and implementation; only then may a separate frozen Verification-B protocol be proposed. Analysis Engine/deterministic code performs calculations only; it does not reason or formulate hypotheses.
